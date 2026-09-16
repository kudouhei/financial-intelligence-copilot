from fastapi import FastAPI
from langchain_openai import OpenAIEmbeddings

from ficopilot.api.app import create_app
from ficopilot.config import Settings
from ficopilot.copilot.azure_planner import AzureCopilotPlanner
from ficopilot.copilot.azure_synthesis_provider import (
    AzureCopilotSynthesisProvider,
)
from ficopilot.copilot.service import CopilotOrchestrator
from ficopilot.data_agent.azure_answer_provider import (
    AzureDataAnswerProvider,
)
from ficopilot.data_agent.azure_sql_provider import (
    AzureSqlGenerationProvider,
)
from ficopilot.data_agent.database import create_database_engine
from ficopilot.data_agent.schema_catalog import PostgresSchemaCatalog
from ficopilot.data_agent.service import DataAgentService
from ficopilot.data_agent.sql_executor import SafeSqlExecutor
from ficopilot.document_rag.azure_answer_provider import (
    AzureDocumentAnswerProvider,
)
from ficopilot.document_rag.azure_search_index import (
    AzureAiSearchDocumentIndex,
)
from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)
from ficopilot.document_rag.service import (
    DocumentRagService,
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
    search_config = settings.require_azure_ai_search_config()

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
        index=AzureAiSearchDocumentIndex(
            endpoint=search_config.endpoint,
            api_key=search_config.api_key,
            index_name=search_config.index_name,
            embeddings=embeddings,
        ),
        answer_provider=AzureDocumentAnswerProvider(
            config=chat_config,
        ),
    )


def create_live_data_service() -> DataAgentService:
    settings = Settings()

    model_config = settings.require_azure_openai_config()
    database_config = settings.require_data_agent_database_config()

    engine = create_database_engine(database_config)

    return DataAgentService(
        schema_catalog=PostgresSchemaCatalog(
            engine=engine,
        ),
        sql_provider=AzureSqlGenerationProvider(
            config=model_config,
        ),
        sql_executor=SafeSqlExecutor(
            engine=engine,
            max_rows=100,
        ),
        answer_provider=AzureDataAnswerProvider(
            config=model_config,
        ),
    )


def create_live_copilot_service(
    *,
    research_service: LangGraphResearchService,
    document_service: DocumentRagService,
    data_service: DataAgentService,
) -> CopilotOrchestrator:
    settings = Settings()
    model_config = settings.require_azure_openai_config()

    return CopilotOrchestrator(
        planner=AzureCopilotPlanner(
            config=model_config,
        ),
        synthesis_provider=AzureCopilotSynthesisProvider(
            config=model_config,
        ),
        research_service=research_service,
        document_service=document_service,
        data_service=data_service,
    )


def create_live_app() -> FastAPI:
    research_service = create_live_service()
    document_service = create_live_document_service()
    data_service = create_live_data_service()

    copilot_service = create_live_copilot_service(
        research_service=research_service,
        document_service=document_service,
        data_service=data_service,
    )

    return create_app(
        research_service=research_service,
        document_service=document_service,
        data_service=data_service,
        copilot_service=copilot_service,
    )
