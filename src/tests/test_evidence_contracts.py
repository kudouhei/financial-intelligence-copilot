from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ficopilot.contracts.research import Citation, Claim


def test_citation_represents_traceable_web_evidence() -> None:
    citation = Citation(
        citation_id="source-1",
        title="Company A Annual Report 2025",
        url="https://example.com/reports/company-a-2025.pdf",
        retrieved_at=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        excerpt="Revenue increased by 8% during the reporting period.",
    )

    assert citation.citation_id == "source-1"
    assert str(citation.url).startswith("https://")
    assert citation.published_at is None


def test_citation_rejects_invalid_url() -> None:
    with pytest.raises(ValidationError):
        Citation(
            citation_id="source-1",
            title="Company A Annual Report 2025",
            url="not-a-valid-url",
            retrieved_at=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
            excerpt="Revenue increased by 8%.",
        )


def test_claim_requires_at_least_one_citation() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Claim(
            statement="Company A's revenue grew by 8% in 2025.",
            citation_ids=[],
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "too_short" in error_types
