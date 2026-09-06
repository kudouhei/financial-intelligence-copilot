from datetime import UTC, datetime

from ficopilot.contracts import ResearchRequest, ResearchResult
from ficopilot.research.service import LangGraphResearchService


class FakeGraph:
    def __init__(self, result: ResearchResult) -> None:
        self._result = result
        self.calls: list[
            tuple[
                dict[str, ResearchRequest],
                dict[str, object],
                dict[str, str],
            ]
        ] = []

    def invoke(
        self,
        input_state: dict[str, ResearchRequest],
        *,
        config: dict[str, object],
        context: dict[str, str],
    ) -> dict[str, ResearchResult]:
        self.calls.append((input_state, config, context))

        return {"result": self._result}


def test_langgraph_research_service_invokes_graph() -> None:
    request = ResearchRequest(
        question="What are the main risks facing Company A?",
        as_of=datetime(2026, 8, 30, 12, 0, tzinfo=UTC),
        max_sources=5,
    )
    expected_result = ResearchResult(
        answer="Company A faces liquidity risk.",
        claims=[],
        citations=[],
        as_of=request.as_of,
        warnings=[],
        trace_id="trace-service-001",
    )
    graph = FakeGraph(expected_result)
    service = LangGraphResearchService(graph=graph)

    result = service.run(
        request,
        trace_id="trace-service-001",
    )

    assert result == expected_result
    assert graph.calls == [
        (
            {"request": request},
            {
                "run_name": "financial_research",
                "tags": ["ficopilot", "research", "development"],
                "metadata": {
                    "application_trace_id": "trace-service-001",
                    "workflow": "financial_research",
                    "environment": "development",
                },
            },
            {"trace_id": "trace-service-001"},
        )
    ]
