from datetime import UTC, datetime

from ficopilot.config import Settings
from ficopilot.contracts import ResearchRequest, ResearchScope, SearchHit
from ficopilot.research.azure_selection_provider import (
    AzureSourceSelectionProvider,
)


def main() -> None:
    settings = Settings()

    request = ResearchRequest(
        question=(
            "What market-related financial risks does Microsoft "
            "disclose in its 2025 Annual Report?"
        ),
        as_of=datetime.now(UTC),
        max_sources=4,
    )

    scope = ResearchScope(
        companies=["Microsoft"],
        document_types=["annual_report"],
        report_years=[2025],
        latest_requested=False,
        evidence_query="Market risk disclosures and risk management.",
    )

    # Handcrafted screening examples, not fresh search results.
    hits = [
        SearchHit(
            title="Microsoft 2025 Annual Report",
            url="https://www.microsoft.com/investor/reports/ar25/index.html",
            snippet="Annual report for fiscal year 2025, including market risk.",
        ),
        SearchHit(
            title="Form 8-K for Microsoft Corp filed 04/30/2025",
            url=(
                "https://microsoft.gcs-web.com/static-files/"
                "ce54dd71-c9fb-4981-844a-2334bbf42839"
            ),
            snippet=(
                "Current report with a quarterly earnings release. "
                "Readers are referred to the annual report for further risks."
            ),
        ),
        SearchHit(
            title="Microsoft Annual Report 2019",
            url="https://www.microsoft.com/investor/reports/ar19/index.html",
            snippet="Annual report for fiscal year 2019.",
        ),
        SearchHit(
            title="Microsoft Annual Report",
            url="https://example.com/report-with-unknown-year",
            snippet="An annual report containing financial risk disclosures.",
        ),
    ]

    provider = AzureSourceSelectionProvider(
        config=settings.require_azure_openai_config(),
    )
    selection = provider.select(request, scope, hits)

    for decision in selection.decisions:
        hit = hits[decision.source_index]
        print(f"\n[{decision.source_index}] {decision.action}: {hit.title}")
        print(decision.reason)


if __name__ == "__main__":
    main()
