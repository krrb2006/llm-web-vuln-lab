from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class AuditRequest(BaseModel):
    project_name: str = Field(default="未命名仓库", alias="projectName", max_length=255)
    provider: str = Field(default="openai", max_length=80)
    model: str = Field(min_length=1, max_length=160)
    endpoint: str = Field(min_length=1, max_length=500)
    api_key: str = Field(alias="apiKey", min_length=1, max_length=500)
    source: str = Field(min_length=1, max_length=100_000)
    file_names: list[str] = Field(default_factory=list, alias="fileNames", max_length=100)

    model_config = {"populate_by_name": True}

    @field_validator("source")
    @classmethod
    def source_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source cannot be blank")
        return value


class ChatRequest(BaseModel):
    model: str = Field(min_length=1, max_length=160)
    endpoint: str = Field(min_length=1, max_length=500)
    api_key: str = Field(alias="apiKey", min_length=1, max_length=500)
    source: str = Field(min_length=1, max_length=100_000)
    message: str = Field(min_length=1, max_length=10_000)
    model_config = {"populate_by_name": True}


class Finding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"] = "low"
    title: str
    location: str = "位置未定位"
    evidence: str = ""
    impact: str = ""
    recommendation: str = ""
    confidence: Literal["high", "medium", "low"] = "medium"


class AuditResult(BaseModel):
    summary: str = ""
    risk_level: Literal["critical", "high", "medium", "low"] = "low"
    findings: list[Finding] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AuditResponse(BaseModel):
    id: str
    result: AuditResult
    messages: list[Message]


class ChatResponse(BaseModel):
    id: str
    message: Message


class ProjectResponse(BaseModel):
    id: str
    name: str
    file_count: int
    total_chars: int
    created_at: str
