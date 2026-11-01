"""FastAPI application entry point."""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import get_settings
from .db import Base, SessionLocal, engine
from .models import User
from .routers import auth, health, jobs
from .security import hash_password

settings = get_settings()
logger = logging.getLogger("vulnlab")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def _wait_for_db(attempts: int = 40) -> None:
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except Exception as error:  # MySQL container may still be booting
            logger.warning("数据库未就绪（%s/%s）：%s", attempt, attempts, type(error).__name__)
            time.sleep(2)
    raise RuntimeError("数据库连接失败")


def _create_schema_and_demo() -> None:
    Base.metadata.create_all(bind=engine)
    if os.getenv("SEED_DEMO", "true").lower() != "true":
        return
    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == settings.demo_email.lower()).first()
        if existing is None:
            db.add(
                User(
                    email=settings.demo_email.lower(),
                    password_hash=hash_password(settings.demo_password),
                    display_name="演示账号",
                )
            )
            db.commit()
            logger.info("已创建演示账号 %s", settings.demo_email)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _wait_for_db()
    _create_schema_and_demo()
    yield


app = FastAPI(
    title="LLM Web Vuln Lab · 智能代码审计",
    version="1.0.0",
    description="上传开源仓库代码，用你自己的模型 API Key 做静态 + LLM 辅助漏洞分析。",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api"
app.include_router(health.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(jobs.router, prefix=api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/api/docs", "health": "/api/health"}
