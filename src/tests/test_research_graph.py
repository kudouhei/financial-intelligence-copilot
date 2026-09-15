from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ficopilot.contracts import (
    Citation,
    Claim,
    ResearchRequest,
    ResearchResult,
    SearchHit,
    SynthesisDraft,
)
from ficopilot.research.graph import build_research_graph


class FakeSearchProvider:
    def __init__(self, citations: list[Citation]) -> None:
        self._citations = citations
        self.requests: list[ResearchRequest] = []

    def search(self, request: ResearchRequest) -> list[SearchHit]:
        self.requests.append(request)

        return [
            SearchHit(
                title=citation.title,
                url=citation.url,
                snippet="Search snippet only; not the extracted evidence.",
            )
            for citation in self._citations[: request.max_sources]
        ]


class FakeExtractionProvider:
    def __init__(self, citations: list[Citation]) -> None:
        self._citations = citations
        self.calls: list[tuple[ResearchRequest, list[SearchHit]]] = []

    def extract(
        self,
        request: ResearchRequest,
        hits: list[SearchHit],
    ) -> list[Citation]:
        self.calls.append((request, list(hits)))

        return self._citations


class FakeSynthesisProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[ResearchRequest, list[Citation]]] = []

    def synthesize(
        self,
        request: ResearchRequest,
        citations: list[Citation],
    ) -> SynthesisDraft:
        self.calls.append((request, list(citations)))
        citation = citations[0]

        return SynthesisDraft(
            answer=citation.excerpt,
            claims=[
                Claim(
                    statement=citation.excerpt,
                    citation_ids=[citation.citation_id],
                )
            ],
        )


class HallucinatingSynthesisProvider:
    def synthesize(
        self,
        request: ResearchRequest,
        citations: list[Citation],
    ) -> SynthesisDraft:
        return SynthesisDraft(
            answer="An unsupported model-generated answer.",
            claims=[
                Claim(
                    statement=("This claim is not supported by retrieved evidence."),
                    citation_ids=["hallucinated-source"],
                )
            ],
        )


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
    citation = make_citation(request)
    search_provider = FakeSearchProvider([citation])
    extraction_provider = FakeExtractionProvider([citation])
    synthesis_provider = FakeSynthesisProvider()
    graph = build_research_graph(
        search_provider=search_provider,
        extraction_provider=extraction_provider,
        synthesis_provider=synthesis_provider,
    )

    final_state = graph.invoke(
        {"request": request},
        context={"trace_id": "trace-success-001"},
    )

    assert search_provider.requests == [request]
    assert synthesis_provider.calls == [(request, [citation])]

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
    assert result.trace_id == "trace-success-001"


def test_research_graph_returns_controlled_no_evidence_result() -> None:
    request = make_request()
    search_provider = FakeSearchProvider([])
    synthesis_provider = FakeSynthesisProvider()
    graph = build_research_graph(
        search_provider=search_provider,
        extraction_provider=FakeExtractionProvider([]),
        synthesis_provider=synthesis_provider,
    )

    final_state = graph.invoke(
        {"request": request},
        context={"trace_id": "trace-no-evidence-001"},
    )
    result = final_state["result"]
    assert result.trace_id == "trace-no-evidence-001"
    assert result.answer == ("Insufficient evidence to answer the research question.")
    assert result.claims == []
    assert result.citations == []
    assert result.warnings == ["No evidence was returned by the search provider."]

    assert synthesis_provider.calls == []


def test_research_graph_rejects_hallucinated_citation() -> None:
    request = make_request()
    citation = make_citation(request)
    search_provider = FakeSearchProvider([citation])
    synthesis_provider = HallucinatingSynthesisProvider()
    graph = build_research_graph(
        search_provider=search_provider,
        extraction_provider=FakeExtractionProvider([citation]),
        synthesis_provider=synthesis_provider,
    )

    with pytest.raises(
        ValidationError,
        match="hallucinated-source",
    ):
        graph.invoke(
            {"request": request},
            context={"trace_id": "trace-hallucination-001"},
        )


def test_research_graph_skips_synthesis_when_extraction_is_empty() -> None:
    request = make_request()
    citation = make_citation(request)
    extraction_provider = FakeExtractionProvider([])
    synthesis_provider = FakeSynthesisProvider()

    graph = build_research_graph(
        search_provider=FakeSearchProvider([citation]),
        extraction_provider=extraction_provider,
        synthesis_provider=synthesis_provider,
    )

    final_state = graph.invoke(
        {"request": request},
        context={"trace_id": "trace-empty-extraction"},
    )

    assert final_state["hits"]
    assert extraction_provider.calls == [(request, final_state["hits"])]
    assert final_state["citations"] == []
    assert final_state["result"].claims == []
    assert final_state["result"].warnings == [
        "Search returned candidate sources, but no usable content was extracted."
    ]
    assert synthesis_provider.calls == []
