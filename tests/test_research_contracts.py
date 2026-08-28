from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ficopilot.contracts import (
    Claim,
    ResearchRequest,
    SynthesisDraft,
)


def test_research_request_accepts_valid_input() -> None:
    request = ResearchRequest(
        question="What are the main risks facing Company A?",
        as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        max_sources=5,
    )

    assert request.question == "What are the main risks facing Company A?"
    assert request.max_sources == 5


def test_research_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ResearchRequest(
            question="Analyse Company A",
            as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
            max_sources=5,
            unexpected_field="should not be accepted",
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "extra_forbidden" in error_types


def test_research_request_rejects_naive_datetime() -> None:
    naive_as_of = datetime(2026, 8, 28, 12, 0)  # noqa: DTZ001

    with pytest.raises(ValidationError) as exc_info:
        ResearchRequest(
            question="Analyse Company A",
            as_of=naive_as_of,
            max_sources=5,
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "timezone_aware" in error_types


def test_research_request_rejects_blank_question() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ResearchRequest(
            question="   ",
            as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "string_too_short" in error_types


def test_research_request_normalizes_question_whitespace() -> None:
    request = ResearchRequest(
        question="  Analyse Company A  ",
        as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
    )

    assert request.question == "Analyse Company A"


def test_synthesis_draft_contains_only_model_authored_content() -> None:
    draft = SynthesisDraft(
        answer="Company A faces market and liquidity risks.",
        claims=[
            Claim(
                statement=(
                    "Company A identifies market risk and "
                    "liquidity risk as material risks."
                ),
                citation_ids=["source-1"],
            )
        ],
    )

    assert draft.warnings == []
    assert set(draft.model_dump()) == {
        "answer",
        "claims",
        "warnings",
    }


def test_synthesis_draft_rejects_system_owned_metadata() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SynthesisDraft(
            answer="Company A faces market risk.",
            claims=[
                Claim(
                    statement="Company A faces market risk.",
                    citation_ids=["source-1"],
                )
            ],
            trace_id="model-controlled-trace",
        )

    error_types = {error["type"] for error in exc_info.value.errors()}

    assert "extra_forbidden" in error_types
