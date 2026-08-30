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
    def __init__(self, *, graph: CompiledStateGraph) -> None:
        self._graph = graph

    def run(self, request: ResearchRequest, *, trace_id: str) -> ResearchResult:
        final_state = self._graph.invoke(
            {"request": request},
            context={"trace_id": trace_id},
        )

        result = final_state.get("result")

        if not isinstance(result, ResearchResult):
            raise TypeError("Research graph completed without a valid result.")

        return result
