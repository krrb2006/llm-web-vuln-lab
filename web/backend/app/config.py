"""Application settings, loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


class Settings:
    """Minimal settings object (no external dependency)."""

    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "LLM Web Vuln Lab")
        self.env = os.getenv("APP_ENV", "production")
        self.database_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://vulnlab:vulnlab@mysql:3306/vulnlab?charset=utf8mb4",
        )
        self.jwt_secret = os.getenv("JWT_SECRET", "change-me-in-production")
        self.jwt_ttl_seconds = int(os.getenv("JWT_TTL_SECONDS", "604800"))
        self.data_dir = Path(os.getenv("DATA_DIR", "/data"))
        self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "20"))
        self.max_files = int(os.getenv("MAX_FILES", "3000"))
        self.max_file_kb = int(os.getenv("MAX_FILE_KB", "512"))
        self.max_candidates = int(os.getenv("MAX_CANDIDATES", "40"))
        self.max_llm_findings = int(os.getenv("MAX_LLM_FINDINGS", "8"))
        self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        self.daily_job_limit = int(os.getenv("DAILY_JOB_LIMIT", "10"))
        self.allow_register = os.getenv("ALLOW_REGISTER", "true").lower() == "true"
        # Demo account is only created when the flag is on (used by docker-compose demo mode).
        self.demo_email = os.getenv("DEMO_EMAIL", "demo@vulnlab.local")
        self.demo_password = os.getenv("DEMO_PASSWORD", "demo-vulnlab-2026")

    @property
    def upload_dir(self) -> Path:
        path = self.data_dir / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
