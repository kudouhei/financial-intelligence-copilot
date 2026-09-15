from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ficopilot.contracts import Citation, Claim, ResearchResult

AS_OF = datetime(2026, 8, 28, 12, 0, tzinfo=UTC)


def make_citation(citation_id: str) -> Citation:
    return Citation(
        citation_id=citation_id,
        title="Company A Annual Report 2025",
        url="https://example.com/company-a-2025.pdf",
        published_at=datetime(2026, 3, 15, 9, 0, tzinfo=UTC),
        retrieved_at=AS_OF,
        excerpt="Revenue increased by 8% during the reporting period.",
    )


def test_research_result_accepts_grounded_claims() -> None:
    result = ResearchResult(
        answer="Company A reported revenue growth of 8%.",
        claims=[
            Claim(
                statement="Company A's revenue grew by 8% in 2025.",
                citation_ids=["source-1"],
            )
        ],
        citations=[make_citation("source-1")],
        as_of=AS_OF,
        trace_id="trace-001",
    )

    assert result.claims[0].citation_ids == ["source-1"]
    assert result.warnings == []


def test_research_result_rejects_missing_citation_reference() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ResearchResult(
            answer="Company A reported revenue growth of 8%.",
            claims=[
                Claim(
                    statement="Company A's revenue grew by 8% in 2025.",
                    citation_ids=["missing-source"],
                )
            ],
            citations=[make_citation("source-1")],
            as_of=AS_OF,
            trace_id="trace-002",
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "value_error" in error_types
    assert "missing-source" in str(exc_info.value)


def test_research_result_rejects_duplicate_citation_ids() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ResearchResult(
            answer="Company A reported revenue growth of 8%.",
            claims=[
                Claim(
                    statement="Company A's revenue grew by 8% in 2025.",
                    citation_ids=["source-1"],
                )
            ],
            citations=[
                make_citation("source-1"),
                make_citation("source-1"),
            ],
            as_of=AS_OF,
            trace_id="trace-003",
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "value_error" in error_types
    assert "source-1" in str(exc_info.value)
