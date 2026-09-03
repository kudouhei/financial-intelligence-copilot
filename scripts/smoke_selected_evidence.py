from datetime import UTC, datetime

from ficopilot.config import Settings
from ficopilot.contracts import ResearchRequest
from ficopilot.research.azure_scope_provider import (
    AzureResearchScopeProvider,
)
from ficopilot.research.azure_selection_provider import (
    AzureSourceSelectionProvider,
)
from ficopilot.research.tavily_extraction_provider import (
    TavilyExtractionProvider,
)
from ficopilot.research.tavily_provider import TavilySearchProvider


def main() -> None:
    settings = Settings()
    azure_config = settings.require_azure_openai_config()

    request = ResearchRequest(
        question=(
            "What market-related financial risks does Microsoft "
            "disclose in its 2025 Annual Report?"
        ),
        as_of=datetime.now(UTC),
        max_sources=5,
    )

    scope_provider = AzureResearchScopeProvider(config=azure_config)
    scope = scope_provider.identify(request)

    print("SCOPE")
    print(scope.model_dump_json(indent=2))

    if scope.latest_requested:
        print(
            "\nStopped: latest-report resolution is not implemented. "
            "Use an explicitly identified report year for this experiment."
        )
        return

    tavily_key = settings.require_tavily_api_key()

    search_provider = TavilySearchProvider(
        api_key=tavily_key,
        search_depth="advanced",
        topic="general",
    )
    hits = search_provider.search(request)

    print(f"\nSEARCH: {len(hits)} candidate(s)")

    if not hits:
        print("Stopped: no search candidates.")
        return

    selection_provider = AzureSourceSelectionProvider(config=azure_config)
    selection = selection_provider.select(request, scope, hits)

    print("\nSELECTION")

    for decision in selection.decisions:
        hit = hits[decision.source_index]
        print(f"[{decision.source_index}] {decision.action}: {hit.title}")
        print(f"  {decision.reason}")

    selected_hits = [
        hits[decision.source_index]
        for decision in selection.decisions
        if decision.action == "keep"
    ]

    pending_count = sum(
        decision.action == "needs_verification" for decision in selection.decisions
    )

    print(f"\nSelected for extraction: {len(selected_hits)}")
    print(f"Held for verification: {pending_count}")

    if not selected_hits:
        print(
            "Stopped: no candidate passed the initial screen. "
            "This does not prove that suitable evidence does not exist."
        )
        return

    extraction_provider = TavilyExtractionProvider(api_key=tavily_key)
    citations = extraction_provider.extract(
        request,
        selected_hits,
        evidence_query=scope.evidence_query,
    )

    selected_urls = {str(hit.url) for hit in selected_hits}
    assert all(str(citation.url) in selected_urls for citation in citations)

    print(f"\nEXTRACTED: {len(citations)} citation(s)")
    print("Metadata screening is not independent source verification.")

    for citation in citations:
        print(f"\n{citation.title}")
        print(citation.url)
        print(citation.excerpt)


if __name__ == "__main__":
    main()
