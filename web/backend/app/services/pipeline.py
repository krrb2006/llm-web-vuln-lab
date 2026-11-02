"""Analysis pipeline: extract -> dataflow/regex candidates -> optional LLM -> persist."""

from __future__ import annotations

import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from ..config import get_settings
from ..db import SessionLocal
from ..models import Finding, Job
from . import llm
from .archive import ArchiveError, LANGUAGE_BY_SUFFIX, extract, language_counts
from .dataflow import analyze_files as dataflow_analyze
from .scan import scan_files

settings = get_settings()

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
DATAFLOW_LANGUAGES = {"PHP", "JavaScript", "TypeScript", "Python"}


def _touch(db, job: Job, *, stage: str | None = None, progress: int | None = None) -> None:
    if stage is not None:
        job.stage = stage
    if progress is not None:
        job.progress = progress
    db.commit()


def _cleanup(job_id: str) -> None:
    shutil.rmtree(settings.upload_dir / job_id, ignore_errors=True)


def _merge(dataflow_hits: list[dict], regex_hits: list[dict]) -> list[dict]:
    """数据流结果优先；同一 (文件, 行, 类别) 只保留一条，正则补充其它类别。"""
    merged: dict[tuple[str, int, str], dict] = {}
    for item in dataflow_hits:
        merged[(item["file_path"], item["line"], item["category"])] = item
    for item in regex_hits:
        key = (item["file_path"], item["line"], item["category"])
        if key not in merged:
            merged[key] = item
    items = list(merged.values())
    items.sort(key=lambda item: (SEVERITY_RANK.get(item["severity"], 9), item["file_path"], item["line"]))
    return items


def run_job(job_id: str, api_key: str | None, provider: str, base_url: str | None, model: str) -> None:
    """Background entry point. The API key never leaves this process."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.status = "running"
        job.started_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        _touch(db, job, stage="extracting", progress=8)

        workdir = settings.upload_dir / job_id
        archive_path = next((p for p in workdir.iterdir() if p.is_file()), None)
        if archive_path is None:
            raise ArchiveError("上传文件丢失，请重新上传")

        files = extract(archive_path, workdir, job.filename)
        job.file_count = len(files)
        languages = language_counts(files)
        job.languages = languages

        def language_of(item) -> str:
            return LANGUAGE_BY_SUFFIX.get(item.suffix.lower(), "Other")

        _touch(db, job, stage="scanning", progress=30)

        regex_candidates = scan_files(files, language_of)
        regex_hits = [
            {
                "category": candidate.rule.category,
                "severity": candidate.rule.severity,
                "title": candidate.rule.title,
                "file_path": candidate.file_path,
                "line": candidate.line,
                "snippet": candidate.snippet,
                "explanation": "静态规则命中，尚未经过模型确认；请人工复核数据流。",
                "remediation": candidate.rule.remediation,
                "confidence": 45,
                "source": "static",
                "flow": [],
            }
            for candidate in regex_candidates
        ]

        dataflow_hits = []
        supported = [item for item in files if language_of(item) in DATAFLOW_LANGUAGES]
        if supported:
            _touch(db, job, stage="dataflow", progress=42)
            for finding in dataflow_analyze(supported, language_of):
                dataflow_hits.append(
                    {
                        "category": finding.category,
                        "severity": finding.severity,
                        "title": finding.title,
                        "file_path": finding.file_path,
                        "line": finding.line,
                        "snippet": finding.snippet,
                        "explanation": finding.explanation,
                        "remediation": finding.remediation,
                        "confidence": finding.confidence,
                        "source": "dataflow",
                        "flow": [step.as_dict() for step in finding.flow],
                    }
                )

        candidates = _merge(dataflow_hits, regex_hits)[: settings.max_candidates]
        _touch(db, job, stage="analyzing", progress=58)

        llm_targets = candidates[: settings.max_llm_findings] if api_key else []
        job.llm_candidate_count = len(llm_targets)
        job.llm_call_count = 0
        db.commit()
        llm_errors: list[str] = []
        results: list[dict] = []

        for index, item in enumerate(candidates):
            record = dict(item)
            if record in llm_targets:
                job.llm_call_count += 1
                language = LANGUAGE_BY_SUFFIX.get(Path(record["file_path"]).suffix.lower(), "")
                flow_text = " → ".join(step.get("note", "") for step in record.get("flow") or [])
                try:
                    enriched = llm.confirm_candidate(
                        api_key=api_key,
                        provider=provider,
                        base_url=base_url,
                        model=model,
                        file_path=record["file_path"],
                        language=language,
                        category=record["category"],
                        rule_title=record["title"],
                        snippet=record["snippet"],
                        flow_text=flow_text,
                    )
                    record.update(enriched)
                    record["source"] = "llm"
                except llm.LLMError as error:
                    llm_errors.append(str(error))
            results.append(record)
            _touch(db, job, progress=min(58 + int(37 * (index + 1) / max(len(candidates), 1)), 95))

        for record in results:
            db.add(
                Finding(
                    job_id=job.id,
                    category=record["category"],
                    severity=record["severity"],
                    severity_rank=SEVERITY_RANK.get(record["severity"], 9),
                    verdict=record.get("verdict", "uncertain"),
                    title=record["title"][:190],
                    file_path=record["file_path"][:490],
                    line=record["line"],
                    snippet=record["snippet"][:4000],
                    explanation=record["explanation"][:4000],
                    remediation=record["remediation"][:2000],
                    confidence=record["confidence"],
                    source=record["source"],
                    flow=record.get("flow") or [],
                )
            )

        counts: dict[str, int] = {}
        for record in results:
            counts[record["severity"]] = counts.get(record["severity"], 0) + 1
        job.findings_count = len(results)
        job.severity_counts = counts
        job.status = "succeeded"
        job.stage = "done"
        job.progress = 100
        job.finished_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        job.error = "；".join(dict.fromkeys(llm_errors))[:1500]
        db.commit()
    except ArchiveError as error:
        db.rollback()
        job = db.get(Job, job_id)
        if job is not None:
            job.status = "failed"
            job.stage = "failed"
            job.error = str(error)[:1500]
            db.commit()
    except Exception as error:  # keep the API alive, surface the reason to the user
        db.rollback()
        job = db.get(Job, job_id)
        if job is not None:
            job.status = "failed"
            job.stage = "failed"
            job.error = f"{type(error).__name__}: {error}"[:1500]
            db.commit()
        traceback.print_exc()
    finally:
        try:
            _cleanup(job_id)
        finally:
            db.close()


def recent_jobs(db, user_id: str, limit: int = 12) -> list[Job]:
    return list(
        db.scalars(
            select(Job).where(Job.user_id == user_id).order_by(Job.created_at.desc()).limit(limit)
        )
    )
