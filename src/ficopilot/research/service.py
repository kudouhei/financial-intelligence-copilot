from typing import Protocol

from langgraph.graph.state import CompiledStateGraph

from ficopilot.contracts import ResearchRequest, ResearchResult


class ResearchService(Protocol):
    def run(
        self,
        request: ResearchRequest,
        *,
        trace_id: str,
    ) -> ResearchResult: ...


class LangGraphResearchService(ResearchService):
    def __init__(
        self,
        *,
        graph: CompiledStateGraph,
        workflow_name: str = "financial_research",
    ) -> None:
        self._graph = graph
        self._workflow_name = workflow_name

    def run(
        self,
        request: ResearchRequest,
        *,
        trace_id: str,
    ) -> ResearchResult:
        final_state = self._graph.invoke(
            {"request": request},
            config={
                "run_name": self._workflow_name,
                "tags": [
                    "ficopilot",
                    "research",
                    "development",
                ],
                "metadata": {
                    "application_trace_id": trace_id,
                    "workflow": self._workflow_name,
                    "environment": "development",
                },
            },
            context={"trace_id": trace_id},
        )

        result = final_state.get("result")

        if not isinstance(result, ResearchResult):
            raise TypeError("Research graph completed without a valid result.")

        return result
