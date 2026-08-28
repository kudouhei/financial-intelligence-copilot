from datetime import UTC, datetime

from ficopilot.contracts import ResearchRequest, ResearchResult
from ficopilot.research.graph import build_research_graph


def test_research_graph_runs_deterministic_vertical_slice() -> None:
    graph = build_research_graph()
    request = ResearchRequest(
        question="What are the main risks facing Company A?",
        as_of=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        max_sources=5,
    )

    final_state = graph.invoke({"request": request})

    assert final_state["plan"] == [
        "Find reliable sources for: What are the main risks facing Company A?",
        "Synthesize claims with citation references",
    ]
    assert final_state["citations"][0].citation_id == ("fixture-company-a-risk")

    result = final_state["result"]

    assert isinstance(result, ResearchResult)
    assert result.answer == (
        "Company A identifies market risk and liquidity risk as material risks."
    )
    assert result.claims[0].citation_ids == ["fixture-company-a-risk"]
    assert result.citations[0].citation_id == "fixture-company-a-risk"
    assert result.as_of == request.as_of
