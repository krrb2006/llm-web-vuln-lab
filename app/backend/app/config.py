from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "mysql+asyncmy://traceguard:change-me@localhost:3306/traceguard?charset=utf8mb4"
    cors_origins: str = "http://localhost"
    max_source_chars: int = 90_000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
