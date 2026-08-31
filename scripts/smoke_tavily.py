from datetime import UTC, datetime

from ficopilot.config import Settings
from ficopilot.contracts import ResearchRequest
from ficopilot.research.tavily_provider import (
    TavilySearchProvider,
)


def main() -> None:
    settings = Settings()
    provider = TavilySearchProvider(
        api_key=settings.require_tavily_api_key(),
        search_depth="basic",
    )
    request = ResearchRequest(
        question=(
            "What are the main financial risks disclosed "
            "by Microsoft in its latest annual report?"
        ),
        as_of=datetime.now(UTC),
        max_sources=3,
    )

    citations = provider.search(request)

    print(f"citations={len(citations)}")

    for citation in citations:
        print(f"- {citation.title}")
        print(f"  {citation.url}")


if __name__ == "__main__":
    main()
