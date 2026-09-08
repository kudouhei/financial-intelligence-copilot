from dataclasses import dataclass

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True, slots=True)
class AzureOpenAIConfig:
    endpoint: str
    api_key: str
    deployment: str

    @property
    def base_url(self) -> str:
        return f"{self.endpoint.rstrip('/')}/openai/v1/"


@dataclass(frozen=True, slots=True)
class AzureOpenAIEmbeddingConfig:
    endpoint: str
    api_key: str
    deployment: str

    @property
    def base_url(self) -> str:
        return f"{self.endpoint.rstrip('/')}/openai/v1/"

@dataclass(frozen=True, slots=True)
class AzureAiSearchConfig:
    endpoint: str
    api_key: str
    index_name: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    tavily_api_key: SecretStr | None = None

    azure_openai_endpoint: str | None = None
    azure_openai_api_key: SecretStr | None = None
    azure_openai_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None

    azure_ai_search_endpoint: str | None = None
    azure_ai_search_api_key: SecretStr | None = None
    azure_ai_search_index_name: str = (
        "financial-document-chunks-v1"
    )

    def require_tavily_api_key(self) -> str:
        if self.tavily_api_key is None:
            raise RuntimeError("TAVILY_API_KEY is required for live research.")

        value = self.tavily_api_key.get_secret_value()

        if not value.strip():
            raise RuntimeError("TAVILY_API_KEY is required for live research.")

        return value

    def require_azure_openai_config(self) -> AzureOpenAIConfig:
        endpoint = (self.azure_openai_endpoint or "").strip()

        deployment = (self.azure_openai_deployment or "").strip()

        api_key = (
            self.azure_openai_api_key.get_secret_value()
            if self.azure_openai_api_key
            else ""
        ).strip()

        if not endpoint or not api_key or not deployment:
            raise RuntimeError(
                "AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_API_KEY, and "
                "AZURE_OPENAI_DEPLOYMENT are required."
            )

        return AzureOpenAIConfig(
            endpoint=endpoint,
            api_key=api_key,
            deployment=deployment,
        )

    def require_azure_openai_embedding_config(
        self,
    ) -> AzureOpenAIEmbeddingConfig:
        endpoint = (self.azure_openai_endpoint or "").strip()
        deployment = (self.azure_openai_embedding_deployment or "").strip()

        api_key = (
            self.azure_openai_api_key.get_secret_value()
            if self.azure_openai_api_key
            else ""
        ).strip()

        if not endpoint or not api_key or not deployment:
            raise RuntimeError(
                "AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_API_KEY, and "
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT are required."
            )

        return AzureOpenAIEmbeddingConfig(
            endpoint=endpoint,
            api_key=api_key,
            deployment=deployment,
        )

    def require_azure_ai_search_config(
        self,
    ) -> AzureAiSearchConfig:
        endpoint = (
            self.azure_ai_search_endpoint or ""
        ).strip()

        api_key = (
            self.azure_ai_search_api_key.get_secret_value()
            if self.azure_ai_search_api_key
            else ""
        ).strip()

        index_name = self.azure_ai_search_index_name.strip()

        if not endpoint or not api_key or not index_name:
            raise RuntimeError(
                "AZURE_AI_SEARCH_ENDPOINT, "
                "AZURE_AI_SEARCH_API_KEY, and "
                "AZURE_AI_SEARCH_INDEX_NAME are required."
            )

        return AzureAiSearchConfig(
            endpoint=endpoint,
            api_key=api_key,
            index_name=index_name,
        )