from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from langchain_core.tools import ToolException

from ficopilot.contracts import ResearchRequest
from ficopilot.research.tavily_provider import TavilySearchProvider


def make_request() -> ResearchRequest:
    return ResearchRequest(
        question="What are the main risks facing Company A?",
        as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        max_sources=5,
    )


def test_tavily_provider_maps_search_results() -> None:
    payload = {
        "results": [
            {
                "title": "Company A Annual Report",
                "url": "https://example.com/company-a-annual-report",
                "content": "Company A identifies liquidity risk as material.",
            }
        ]
    }

    with patch("ficopilot.research.tavily_provider.TavilySearch") as search_cls:
        search_cls.return_value.invoke.return_value = payload
        citations = TavilySearchProvider(api_key="test-key").search(make_request())

    assert len(citations) == 1
    assert citations[0].title == "Company A Annual Report"
    assert citations[0].excerpt == "Company A identifies liquidity risk as material."
    assert citations[0].citation_id.startswith("tavily-")


def test_tavily_provider_parses_json_string_response() -> None:
    payload = (
        '{"results":[{"title":"Company A Annual Report",'
        '"url":"https://example.com/company-a-annual-report",'
        '"content":"Liquidity risk is material."}]}'
    )

    with patch("ficopilot.research.tavily_provider.TavilySearch") as search_cls:
        search_cls.return_value.invoke.return_value = payload
        citations = TavilySearchProvider(api_key="test-key").search(make_request())

    assert len(citations) == 1
    assert citations[0].title == "Company A Annual Report"


def test_tavily_provider_empty_results_are_no_evidence() -> None:
    with patch("ficopilot.research.tavily_provider.TavilySearch") as search_cls:
        search_cls.return_value.invoke.side_effect = ToolException(
            "No search results found."
        )
        citations = TavilySearchProvider(api_key="test-key").search(make_request())

    assert citations == []


def test_tavily_provider_rejects_api_error_payload() -> None:
    with (
        patch("ficopilot.research.tavily_provider.TavilySearch") as search_cls,
        pytest.raises(RuntimeError, match="Tavily search failed"),
    ):
        search_cls.return_value.invoke.return_value = {"error": "quota exceeded"}
        TavilySearchProvider(api_key="test-key").search(make_request())
