from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_maps_server_key: SecretStr
    nvidia_api_key: SecretStr

    @property
    def google_maps_server_key_value(self) -> str:
        return self.google_maps_server_key.get_secret_value()

    @property
    def nvidia_api_key_value(self) -> str:
        return self.nvidia_api_key.get_secret_value()


settings = Settings()  # pyright: ignore[reportCallIssue]
