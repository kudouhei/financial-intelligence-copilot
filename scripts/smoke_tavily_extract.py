from datetime import UTC, datetime

from ficopilot.config import Settings
from ficopilot.contracts import ResearchRequest, SearchHit
from ficopilot.research.tavily_extraction_provider import (
    TavilyExtractionProvider,
)


def main() -> None:
    settings = Settings()

    request = ResearchRequest(
        question=(
            "What market-related financial risks does Microsoft "
            "disclose in its 2025 Annual Report?"
        ),
        as_of=datetime.now(UTC),
        max_sources=1,
    )

    hit = SearchHit(
        title="Microsoft 2025 Annual Report",
        url="https://www.microsoft.com/investor/reports/ar25/index.html",
        snippet="Microsoft annual report for fiscal year 2025.",
    )

    provider = TavilyExtractionProvider(
        api_key=settings.require_tavily_api_key(),
    )

    citations = provider.extract(
        request,
        [hit],
        evidence_query=(
            "QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK. "
            "Risk exposures and risk management."
        ),
    )

    print(f"citations={len(citations)}")

    for citation in citations:
        print(f"\nid={citation.citation_id}")
        print(f"title={citation.title}")
        print(f"url={citation.url}")
        print(f"excerpt_chars={len(citation.excerpt)}")
        print(citation.excerpt)


if __name__ == "__main__":
    main()
