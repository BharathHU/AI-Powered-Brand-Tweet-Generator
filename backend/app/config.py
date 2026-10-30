from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    frontend_url: str = "http://localhost:5173"
    request_timeout_seconds: float = 45.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]
        local_origins = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }
        if any(origin in local_origins for origin in origins):
            origins.extend(local_origins.difference(origins))
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
