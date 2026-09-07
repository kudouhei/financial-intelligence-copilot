from fastapi import FastAPI
from langchain_openai import OpenAIEmbeddings

from ficopilot.api.app import create_app
from ficopilot.config import Settings
from ficopilot.document_rag.azure_answer_provider import (
    AzureDocumentAnswerProvider,
)
from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)
from ficopilot.document_rag.service import (
    DocumentRagService,
)
from ficopilot.document_rag.vector_index import (
    InMemoryDocumentIndex,
)
from ficopilot.research.azure_scope_provider import (
    AzureResearchScopeProvider,
)
from ficopilot.research.azure_selection_provider import (
    AzureSourceSelectionProvider,
)
from ficopilot.research.azure_synthesis_provider import (
    AzureOpenAISynthesisProvider,
)
from ficopilot.research.graph import (
    build_research_graph,
)
from ficopilot.research.service import (
    LangGraphResearchService,
)
from ficopilot.research.tavily_extraction_provider import (
    TavilyExtractionProvider,
)
from ficopilot.research.tavily_provider import (
    TavilySearchProvider,
)


def create_live_service() -> LangGraphResearchService:
    settings = Settings()
    azure_config = settings.require_azure_openai_config()
    tavily_key = settings.require_tavily_api_key()

    graph = build_research_graph(
        scope_provider=AzureResearchScopeProvider(
            config=azure_config,
        ),
        search_provider=TavilySearchProvider(
            api_key=tavily_key,
            search_depth="advanced",
            topic="general",
        ),
        selection_provider=AzureSourceSelectionProvider(
            config=azure_config,
        ),
        extraction_provider=TavilyExtractionProvider(
            api_key=tavily_key,
        ),
        synthesis_provider=AzureOpenAISynthesisProvider(
            config=azure_config,
        ),
    )

    return LangGraphResearchService(graph=graph)


def create_live_document_service() -> DocumentRagService:
    settings = Settings()
    chat_config = settings.require_azure_openai_config()
    embedding_config = settings.require_azure_openai_embedding_config()

    embeddings = OpenAIEmbeddings(
        model=embedding_config.deployment,
        base_url=embedding_config.base_url,
        api_key=embedding_config.api_key,
        chunk_size=64,
        timeout=60,
        max_retries=3,
    )

    return DocumentRagService(
        ingestion_service=PdfIngestionService(),
        index=InMemoryDocumentIndex(embeddings=embeddings),
        answer_provider=AzureDocumentAnswerProvider(config=chat_config),
    )


def create_live_app() -> FastAPI:
    return create_app(
        research_service=create_live_service(),
        document_service=create_live_document_service(),
    )
