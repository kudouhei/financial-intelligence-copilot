from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    tavily_api_key: SecretStr | None = None

    azure_openai_endpoint: str | None = None
    azure_openai_api_key: SecretStr | None = None
    azure_openai_deployment: str | None = None

    def require_tavily_api_key(self) -> str:
        if self.tavily_api_key is None:
            raise RuntimeError("TAVILY_API_KEY is required for live research.")

        value = self.tavily_api_key.get_secret_value()

        if not value.strip():
            raise RuntimeError("TAVILY_API_KEY is required for live research.")

        return value
