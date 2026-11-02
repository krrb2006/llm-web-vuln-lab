from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import Base, engine, get_session
from .llm import LLMError, SYSTEM_PROMPT, complete, parse_json_content, source_message
from .models import AuditSession, Project
from .schemas import AuditRequest, AuditResponse, AuditResult, ChatRequest, ChatResponse, Message


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="TraceGuard API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/health")
async def health(session: AsyncSession = Depends(get_session)):
    await session.execute(text("SELECT 1"))
    return {"ok": True, "database": "ready"}


@app.post("/api/audits", response_model=AuditResponse)
async def create_audit(payload: AuditRequest, session: AsyncSession = Depends(get_session)):
    messages = [source_message(payload.source), {"role": "user", "content": "请先对项目进行一次防御性安全审计，返回约定的 JSON 结构。"}]
    try:
        raw = await complete(payload.endpoint, payload.api_key, payload.model, [{"role": "system", "content": SYSTEM_PROMPT}, *messages])
        result = AuditResult.model_validate(parse_json_content(raw))
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    project = Project(name=payload.project_name, file_count=len(payload.file_names), total_chars=len(payload.source))
    audit = AuditSession(provider=payload.provider, model=payload.model, summary=result.summary, risk_level=result.risk_level, findings=[item.model_dump() for item in result.findings], messages=[{"role": "assistant", "content": result.summary}], project=project)
    session.add(audit)
    await session.commit()
    await session.refresh(audit)
    return AuditResponse(id=audit.id, result=result, messages=[Message(role="assistant", content=result.summary)])


@app.post("/api/audits/{audit_id}/chat", response_model=ChatResponse)
async def chat(audit_id: str, payload: ChatRequest, session: AsyncSession = Depends(get_session)):
    audit = await session.scalar(select(AuditSession).where(AuditSession.id == audit_id))
    if not audit:
        raise HTTPException(status_code=404, detail="审计会话不存在。")
    history = list(audit.messages or [])[-12:]
    history.extend([{"role": "user", "content": payload.message}])
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n本轮是对话追问，请用清晰的自然语言回答，不要返回 JSON。"}, source_message(payload.source), *history]
    try:
        content = await complete(payload.endpoint, payload.api_key, payload.model, messages)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    history.append({"role": "assistant", "content": content})
    audit.messages = history[-20:]
    audit.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    return ChatResponse(id=audit.id, message=Message(role="assistant", content=content))
