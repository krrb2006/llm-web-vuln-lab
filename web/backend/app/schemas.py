"""Pydantic schemas for the public API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["critical", "high", "medium", "low", "info"]
Verdict = Literal["vulnerable", "safe", "uncertain"]


class RegisterIn(BaseModel):
    # 用普通字符串 + 路由内正则校验，避免 EmailStr 拒绝测试域名（如 .local）
    email: str = Field(min_length=3, max_length=190)
    password: str = Field(min_length=8, max_length=72)
    display_name: str = Field(default="", max_length=80)


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=190)
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    created_at: datetime


class JobCreateIn(BaseModel):
    """The API key is used for this job only and is never persisted."""

    api_key: str | None = Field(default=None, max_length=400)
    provider: str = Field(default="openai", max_length=40)
    base_url: str | None = Field(default=None, max_length=300)
    model: str = Field(default="gpt-4o-mini", max_length=80)


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    severity: Severity
    verdict: Verdict
    title: str
    file_path: str
    line: int
    snippet: str
    explanation: str
    remediation: str
    confidence: int
    source: str
    flow: list[dict] = []


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    size_bytes: int
    file_count: int
    status: str
    stage: str
    progress: int
    error: str
    provider: str
    model: str
    llm_enabled: bool
    llm_candidate_count: int
    llm_call_count: int
    findings_count: int
    severity_counts: dict
    languages: dict
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class JobDetailOut(JobOut):
    findings: list[FindingOut] = []


class JobListOut(BaseModel):
    items: list[JobOut]
    total: int


class HealthOut(BaseModel):
    status: str
    database: str
    version: str
