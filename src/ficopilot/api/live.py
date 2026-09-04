from fastapi import FastAPI

from ficopilot.api.app import create_app
from ficopilot.config import Settings
from ficopilot.research.azure_scope_provider import AzureResearchScopeProvider
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


def create_live_app() -> FastAPI:
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

    service = LangGraphResearchService(graph=graph)
    return create_app(research_service=service)
