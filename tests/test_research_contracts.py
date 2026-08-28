from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ficopilot.contracts.research import ResearchRequest


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
