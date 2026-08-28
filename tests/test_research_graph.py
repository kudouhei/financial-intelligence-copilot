from datetime import UTC, datetime

from ficopilot.contracts import (
    Citation,
    ResearchRequest,
    ResearchResult,
)
from ficopilot.research.graph import build_research_graph


class FakeSearchProvider:
    def __init__(self, citations: list[Citation]) -> None:
        self._citations = citations
        self.requests: list[ResearchRequest] = []

    def search(self, request: ResearchRequest) -> list[Citation]:
        self.requests.append(request)

        return self._citations[: request.max_sources]


def make_request() -> ResearchRequest:
    return ResearchRequest(
        question="What are the main risks facing Company A?",
        as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        max_sources=5,
    )


def make_citation(request: ResearchRequest) -> Citation:
    return Citation(
        citation_id="fixture-company-a-risk",
        title="Company A Annual Report",
        url="https://example.com/company-a-annual-report",
        published_at=None,
        retrieved_at=request.as_of,
        excerpt=(
            "Company A identifies market risk and liquidity risk as material risks."
        ),
    )


def test_research_graph_runs_deterministic_vertical_slice() -> None:
    request = make_request()
    provider = FakeSearchProvider([make_citation(request)])
    graph = build_research_graph(search_provider=provider)

    final_state = graph.invoke({"request": request})

    assert provider.requests == [request]
    assert final_state["plan"] == [
        "Find reliable sources for: What are the main risks facing Company A?",
        "Synthesize claims with citation references",
    ]

    result = final_state["result"]

    assert isinstance(result, ResearchResult)
    assert result.answer == (
        "Company A identifies market risk and liquidity risk as material risks."
    )
    assert result.claims[0].citation_ids == ["fixture-company-a-risk"]
    assert result.citations[0].citation_id == ("fixture-company-a-risk")
    assert result.as_of == request.as_of


def test_research_graph_returns_controlled_no_evidence_result() -> None:
    request = make_request()
    provider = FakeSearchProvider([])
    graph = build_research_graph(search_provider=provider)

    final_state = graph.invoke({"request": request})
    result = final_state["result"]

    assert result.answer == ("Insufficient evidence to answer the research question.")
    assert result.claims == []
    assert result.citations == []
    assert result.warnings == ["No evidence was returned by the search provider."]
