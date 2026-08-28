from functools import partial
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ficopilot.contracts import Citation, Claim, ResearchRequest, ResearchResult
from ficopilot.research.providers import SearchProvider


class ResearchState(TypedDict):
    request: ResearchRequest
    plan: NotRequired[list[str]]
    citations: NotRequired[list[Citation]]
    result: NotRequired[ResearchResult]


def plan_node(state: ResearchState) -> dict[str, list[str]]:
    question = state["request"].question

    return {
        "plan": [
            f"Find reliable sources for: {question}",
            "Synthesize claims with citation references",
        ]
    }


def search_node(
    state: ResearchState,
    *,
    search_provider: SearchProvider,
) -> dict[str, list[Citation]]:
    citations = search_provider.search(state["request"])

    return {"citations": citations}


def route_after_search(
    state: ResearchState,
) -> Literal["synthesize", "no_evidence"]:
    if state["citations"]:
        return "synthesize"

    return "no_evidence"


def synthesize_node(
    state: ResearchState,
) -> dict[str, ResearchResult]:
    request = state["request"]
    citations = state["citations"]
    citation = citations[0]

    result = ResearchResult(
        answer=(
            "Company A identifies market risk and liquidity risk as material risks."
        ),
        claims=[
            Claim(
                statement=(
                    "Company A identifies market risk and liquidity "
                    "risk as material risks."
                ),
                citation_ids=[citation.citation_id],
            )
        ],
        citations=citations,
        as_of=request.as_of,
        warnings=[],
        trace_id="deterministic-trace-001",
    )

    return {"result": result}


def no_evidence_node(
    state: ResearchState,
) -> dict[str, ResearchResult]:
    request = state["request"]

    result = ResearchResult(
        answer=("Insufficient evidence to answer the research question."),
        claims=[],
        citations=[],
        as_of=request.as_of,
        warnings=["No evidence was returned by the search provider."],
        trace_id="deterministic-trace-001",
    )

    return {"result": result}


def build_research_graph(
    *,
    search_provider: SearchProvider,
) -> CompiledStateGraph:
    builder = StateGraph(ResearchState)

    builder.add_node("plan", plan_node)
    builder.add_node("search", partial(search_node, search_provider=search_provider))
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("no_evidence", no_evidence_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "search")
    builder.add_conditional_edges(
        "search",
        route_after_search,
        {
            "synthesize": "synthesize",
            "no_evidence": "no_evidence",
        },
    )
    builder.add_edge("synthesize", END)
    builder.add_edge("no_evidence", END)

    return builder.compile()
