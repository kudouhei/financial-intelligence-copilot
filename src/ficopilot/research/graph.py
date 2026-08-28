from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ficopilot.contracts import Citation, Claim, ResearchRequest, ResearchResult


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


def search_node(state: ResearchState) -> dict[str, list[Citation]]:
    request = state["request"]
    citation = Citation(
        citation_id="fixture-company-a-risk",
        title="Company A Annual Report",
        url="https://example.com/company-a-annual-report",
        published_at=None,
        retrieved_at=request.as_of,
        excerpt=(
            "Company A identifies market risk and liquidity risk as material risks."
        ),
    )

    return {"citations": [citation]}


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


def build_research_graph() -> CompiledStateGraph:
    builder = StateGraph(ResearchState)

    builder.add_node("plan", plan_node)
    builder.add_node("search", search_node)
    builder.add_node("synthesize", synthesize_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "search")
    builder.add_edge("search", "synthesize")
    builder.add_edge("synthesize", END)

    return builder.compile()
