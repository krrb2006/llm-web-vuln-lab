"""Analysis pipeline: extract -> static candidates -> optional LLM confirmation -> persist."""

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
from .scan import Candidate, scan_files

settings = get_settings()

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _touch(db, job: Job, *, stage: str | None = None, progress: int | None = None) -> None:
    if stage is not None:
        job.stage = stage
    if progress is not None:
        job.progress = progress
    db.commit()


def _cleanup(job_id: str) -> None:
    shutil.rmtree(settings.upload_dir / job_id, ignore_errors=True)


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
        _touch(db, job, stage="scanning", progress=32)

        candidates: list[Candidate] = scan_files(
            files, lambda item: LANGUAGE_BY_SUFFIX.get(item.suffix.lower(), "Other")
        )
        candidates.sort(key=lambda item: SEVERITY_RANK.get(item.rule.severity, 9))
        candidates = candidates[: settings.max_candidates]
        _touch(db, job, stage="analyzing", progress=55)

        llm_candidates = candidates[: settings.max_llm_findings] if api_key else []
        results: list[dict] = []
        llm_errors: list[str] = []

        for index, candidate in enumerate(candidates):
            data = {
                "verdict": "uncertain",
                "severity": candidate.rule.severity,
                "title": candidate.rule.title,
                "explanation": "静态规则命中，尚未经过模型确认；请人工复核数据流。",
                "remediation": candidate.rule.remediation,
                "confidence": 45,
                "source": "static",
            }
            if candidate in llm_candidates:
                try:
                    enriched = llm.confirm_candidate(
                        api_key=api_key,
                        provider=provider,
                        base_url=base_url,
                        model=model,
                        file_path=candidate.file_path,
                        language=LANGUAGE_BY_SUFFIX.get(Path(candidate.file_path).suffix.lower(), ""),
                        category=candidate.rule.category,
                        rule_title=candidate.rule.title,
                        snippet=candidate.snippet,
                    )
                    data.update(enriched)
                    data["source"] = "llm"
                except llm.LLMError as error:
                    llm_errors.append(str(error))
            results.append({"candidate": candidate, **data})
            done = 55 + int(40 * (index + 1) / max(len(candidates), 1))
            _touch(db, job, progress=min(done, 95))

        for item in results:
            candidate = item["candidate"]
            db.add(
                Finding(
                    job_id=job.id,
                    category=candidate.rule.category,
                    severity=item["severity"],
                    severity_rank=SEVERITY_RANK.get(item["severity"], 9),
                    verdict=item["verdict"],
                    title=item["title"][:190],
                    file_path=candidate.file_path[:490],
                    line=candidate.line,
                    snippet=candidate.snippet[:4000],
                    explanation=item["explanation"][:4000],
                    remediation=item["remediation"][:2000],
                    confidence=item["confidence"],
                    source=item["source"],
                )
            )

        counts: dict[str, int] = {}
        for item in results:
            counts[item["severity"]] = counts.get(item["severity"], 0) + 1
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
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
    )
