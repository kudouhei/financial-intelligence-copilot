from datetime import UTC, datetime

from ficopilot.config import Settings
from ficopilot.contracts import ResearchRequest
from ficopilot.research.tavily_provider import TavilySearchProvider


def main() -> None:
    settings = Settings()
    api_key = settings.require_tavily_api_key()

    request = ResearchRequest(
        question=(
            "What market-related financial risks does Microsoft "
            "disclose in its 2025 Annual Report?"
        ),
        as_of=datetime.now(UTC),
        max_sources=5,
    )

    print(f"QUERY: {request.question}")
    print(f"CUTOFF: {request.as_of.date()}")

    for topic in ("finance", "general"):
        provider = TavilySearchProvider(
            api_key=api_key,
            search_depth="advanced",
            topic=topic,
        )
        hits = provider.search(request)

        print(f"\nTOPIC: {topic}")
        print(f"RESULTS: {len(hits)}")

        for index, hit in enumerate(hits):
            print(f"[{index}] {hit.title}")
            print(f"    {hit.url}")


if __name__ == "__main__":
    main()
