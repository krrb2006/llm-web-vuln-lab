"""Job endpoints: upload, list, detail, demo and markdown export."""

from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..db import get_db
from ..deps import get_current_user
from ..models import Finding, Job, User
from ..schemas import FindingOut, JobDetailOut, JobListOut, JobOut
from ..services import pipeline

router = APIRouter(prefix="/jobs", tags=["jobs"])
settings = get_settings()

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "samples" / "vulnerable-demo"


def _recent_count(db: Session, user_id: str) -> int:
    since = datetime.utcnow() - timedelta(days=1)
    return int(
        db.scalar(
            select(func.count(Job.id)).where(Job.user_id == user_id, Job.created_at >= since)
        )
        or 0
    )


def _enqueue(background: BackgroundTasks, job: Job, api_key: str | None, provider: str, base_url: str | None, model: str) -> None:
    # The key is passed straight into the worker process memory and never persisted.
    background.add_task(pipeline.run_job, job.id, api_key, provider, base_url, model)


@router.post("", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    api_key: str | None = Form(default=None),
    provider: str = Form(default="openai"),
    base_url: str | None = Form(default=None),
    model: str = Form(default="gpt-4o-mini"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobOut:
    if _recent_count(db, user.id) >= settings.daily_job_limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "今日分析次数已达上限，请明天再试")

    filename = Path(file.filename or "upload.zip").name
    suffix = Path(filename).suffix.lower()
    allowed = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz"} | {
        ".php", ".phtml", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
        ".py", ".java", ".go", ".rb", ".jsp", ".html", ".htm", ".vue", ".svelte",
    }
    if suffix not in allowed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请上传 zip/tar.gz 压缩包，或单个源码文件")

    job_id = uuid.uuid4().hex
    workdir = settings.upload_dir / job_id
    workdir.mkdir(parents=True, exist_ok=True)
    target = workdir / filename
    size = 0
    limit = settings.max_upload_mb * 1024 * 1024
    try:
        with target.open("wb") as sink:
            while chunk := await file.read(1024 * 256):
                size += len(chunk)
                if size > limit:
                    raise HTTPException(
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        f"文件超过 {settings.max_upload_mb} MiB 限制",
                    )
                sink.write(chunk)
    except HTTPException:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
    finally:
        await file.close()

    job = Job(
        id=job_id,
        user_id=user.id,
        filename=filename,
        size_bytes=size,
        status="queued",
        stage="queued",
        progress=2,
        provider=provider[:40] if api_key else "",
        model=model[:80] if api_key else "",
        llm_enabled=bool(api_key),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    _enqueue(background, job, (api_key or "").strip() or None, provider, base_url, model)
    return JobOut.model_validate(job)


@router.post("/demo", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def create_demo_job(
    background: BackgroundTasks,
    provider: str = Form(default="openai"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobOut:
    """Run the pipeline on a bundled intentionally vulnerable sample."""
    job_id = uuid.uuid4().hex
    workdir = settings.upload_dir / job_id
    workdir.mkdir(parents=True, exist_ok=True)
    archive = workdir / "vulnerable-demo.zip"
    import zipfile

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in SAMPLE_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(SAMPLE_DIR).as_posix())

    job = Job(
        id=job_id,
        user_id=user.id,
        filename="vulnerable-demo.zip",
        size_bytes=archive.stat().st_size,
        status="queued",
        stage="queued",
        progress=2,
        provider="",
        model="",
        llm_enabled=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    _enqueue(background, job, None, provider, None, "gpt-4o-mini")
    return JobOut.model_validate(job)


@router.get("", response_model=JobListOut)
def list_jobs(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobListOut:
    limit = max(1, min(limit, 100))
    total = int(db.scalar(select(func.count(Job.id)).where(Job.user_id == user.id)) or 0)
    rows = list(
        db.scalars(
            select(Job)
            .where(Job.user_id == user.id)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return JobListOut(items=[JobOut.model_validate(row) for row in rows], total=total)


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDetailOut:
    job = db.scalar(
        select(Job).options(selectinload(Job.findings)).where(Job.id == job_id, Job.user_id == user.id)
    )
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    detail = JobDetailOut.model_validate(job)
    detail.findings = [FindingOut.model_validate(row) for row in job.findings]
    return detail


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    db.delete(job)
    db.commit()
    shutil.rmtree(settings.upload_dir / job_id, ignore_errors=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{job_id}/export")
def export_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    job = db.scalar(
        select(Job).options(selectinload(Job.findings)).where(Job.id == job_id, Job.user_id == user.id)
    )
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")

    lines = [
        f"# 漏洞分析报告 · {job.filename}",
        "",
        f"- 任务 ID：`{job.id}`",
        f"- 状态：{job.status}（{job.stage}）",
        f"- 文件数：{job.file_count}",
        f"- 发现：{job.findings_count} 条",
        f"- 模型确认：{'是 · ' + job.model if job.llm_enabled else '未启用（仅静态规则）'}",
        f"- 创建时间：{job.created_at:%Y-%m-%d %H:%M:%S}",
        "",
        "| # | 严重度 | 类别 | 位置 | 结论 | 来源 |",
        "|---|---|---|---|---|---|",
    ]
    for index, finding in enumerate(job.findings, start=1):
        lines.append(
            f"| {index} | {finding.severity} | {finding.category} | "
            f"`{finding.file_path}:{finding.line}` | {finding.verdict} | {finding.source} |"
        )
    lines.append("")
    for index, finding in enumerate(job.findings, start=1):
        lines += [
            f"## {index}. {finding.title}",
            "",
            f"- 位置：`{finding.file_path}:{finding.line}`",
            f"- 严重度：{finding.severity}；置信度：{finding.confidence}%",
            f"- 结论：{finding.verdict}（来源：{finding.source}）",
            "",
        ]
        if finding.flow:
            lines.append("**数据流路径**：")
            lines.append("")
            for step in finding.flow:
                lines.append(f"- L{step.get('line')} · {step.get('note', '')} · `{step.get('code', '')}`")
            lines.append("")
        lines += [
            "```",
            finding.snippet,
            "```",
            "",
            f"**分析**：{finding.explanation}",
            "",
            f"**修复建议**：{finding.remediation}",
            "",
        ]
    body = "\n".join(lines)
    return Response(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="vuln-report-{job.id[:8]}.md"'},
    )
