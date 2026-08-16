from typing import Optional

from pydantic import (
    SecretStr,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    google_maps_server_key: SecretStr
    nvidia_api_key: SecretStr
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    langsmith_tracing: bool = False
    langsmith_api_key: Optional[SecretStr] = None
    langsmith_project: str = "google-maps-chatbot"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def google_maps_key(self) -> str:
        return self.google_maps_server_key.get_secret_value()

    @property
    def nvidia_llm_key(self) -> str:
        return self.nvidia_api_key.get_secret_value()

    @property
    def langsmith_key(self) -> Optional[str]:
        if self.langsmith_api_key is None:
            return None
        return self.langsmith_api_key.get_secret_value()
    


settings = Settings()  # pyright: ignore[reportCallIssue]
