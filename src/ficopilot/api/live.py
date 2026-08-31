from fastapi import FastAPI

from ficopilot.api.app import create_app
from ficopilot.config import Settings
from ficopilot.research.azure_synthesis_provider import (
    AzureOpenAISynthesisProvider,
)
from ficopilot.research.graph import (
    build_research_graph,
)
from ficopilot.research.service import (
    LangGraphResearchService,
)
from ficopilot.research.tavily_provider import (
    TavilySearchProvider,
)


def create_live_app() -> FastAPI:
    settings = Settings()

    graph = build_research_graph(
        search_provider=TavilySearchProvider(
            api_key=settings.require_tavily_api_key(),
            search_depth="basic",
        ),
        synthesis_provider=(
            AzureOpenAISynthesisProvider(config=settings.require_azure_openai_config())
        ),
    )
    service = LangGraphResearchService(graph=graph)

    return create_app(research_service=service)
