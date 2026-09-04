from functools import partial
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from ficopilot.contracts import (
    Citation,
    ResearchRequest,
    ResearchResult,
    ResearchScope,
    SearchHit,
    SourceSelection,
)
from ficopilot.research.providers import (
    ExtractionProvider,
    ScopeProvider,
    SearchProvider,
    SelectionProvider,
    SynthesisProvider,
)


class ResearchContext(TypedDict):
    trace_id: str


class ResearchState(TypedDict):
    request: ResearchRequest
    plan: NotRequired[list[str]]
    scope: NotRequired[ResearchScope]
    hits: NotRequired[list[SearchHit]]
    selection: NotRequired[SourceSelection]
    selected_hits: NotRequired[list[SearchHit]]
    citations: NotRequired[list[Citation]]
    pipeline_warnings: NotRequired[list[str]]
    stop_reason: NotRequired[str]
    result: NotRequired[ResearchResult]


# Plan: generate a list of tasks to complete, without invoke model
def plan_node(state: ResearchState) -> dict[str, list[str]]:
    question = state["request"].question

    return {
        "plan": [
            f"Find reliable sources for: {question}",
            "Synthesize claims with citation references",
        ]
    }


def scope_node(
    state: ResearchState,
    *,
    scope_provider: ScopeProvider,
) -> dict[str, object]:
    scope = scope_provider.identify(state["request"])

    stop_reason = ""
    if scope.latest_requested:
        stop_reason = (
            "Latest-report resolution is not implemented. Please specify a report year."
        )

    return {
        "scope": scope,
        "stop_reason": stop_reason,
        "pipeline_warnings": [],
    }


def route_after_scope(
    state: ResearchState,
) -> Literal["search", "no_evidence"]:
    return "no_evidence" if state["stop_reason"] else "search"


def selection_node(
    state: ResearchState,
    *,
    selection_provider: SelectionProvider,
) -> dict[str, object]:
    hits = state["hits"]
    selection = selection_provider.select(state["request"], state["scope"], hits)

    indices = [item.source_index for item in selection.decisions]
    if sorted(indices) != list(range(len(hits))):
        raise ValueError("Selection must cover every candidate exactly once.")

    selected_hits = [
        hits[item.source_index] for item in selection.decisions if item.action == "keep"
    ]

    pending_count = sum(
        item.action == "needs_verification" for item in selection.decisions
    )

    warnings = [
        (
            "Sources passed metadata screening, not independent content "
            "or historical-availability verification."
        )
    ]
    if pending_count:
        warnings.append(
            f"{pending_count} candidate(s) were withheld pending verification."
        )

    return {
        "selection": selection,
        "selected_hits": selected_hits,
        "pipeline_warnings": warnings,
        "stop_reason": (
            ""
            if selected_hits
            else "No candidate passed source screening. "
            "This does not prove that suitable evidence does not exist."
        ),
    }


def route_after_selection(
    state: ResearchState,
) -> Literal["extract", "no_evidence"]:
    return "extract" if state["selected_hits"] else "no_evidence"


# Search: retrieve candidate sources from the web, Python Tavily API
def search_node(
    state: ResearchState,
    *,
    search_provider: SearchProvider,
) -> dict[str, list[SearchHit]]:
    hits = search_provider.search(state["request"])

    return {"hits": hits}


def route_after_search(
    state: ResearchState,
) -> Literal["select", "extract", "no_evidence"]:
    if not state["hits"]:
        return "no_evidence"

    return "select" if "scope" in state else "extract"


# Extract: extract evidence from the candidate sources
def extract_node(
    state: ResearchState,
    *,
    extraction_provider: ExtractionProvider,
) -> dict[str, list[Citation]]:
    if "scope" in state:
        hits = state["selected_hits"]
        citations = extraction_provider.extract(
            state["request"],
            hits,
            evidence_query=state["scope"].evidence_query,
        )

        allowed_urls = {str(hit.url) for hit in hits}
        if any(str(item.url) not in allowed_urls for item in citations):
            raise ValueError("Extraction returned an unselected source.")
    else:
        citations = extraction_provider.extract(
            state["request"],
            state["hits"],
        )

    return {"citations": citations}


def route_after_extract(
    state: ResearchState,
) -> Literal["synthesize", "no_evidence"]:
    return "synthesize" if state["citations"] else "no_evidence"


# Synthesize: combine the evidence into a coherent answer, call the Azure model
def synthesize_node(
    state: ResearchState,
    runtime: Runtime[ResearchContext],
    *,
    synthesis_provider: SynthesisProvider,
) -> dict[str, ResearchResult]:
    request = state["request"]
    citations = state["citations"]
    draft = synthesis_provider.synthesize(
        request,
        citations,
    )

    result = ResearchResult(
        answer=draft.answer,
        claims=draft.claims,
        citations=citations,
        as_of=request.as_of,
        warnings=[
            *state.get("pipeline_warnings", []),
            *draft.warnings,
        ],
        trace_id=runtime.context["trace_id"],
    )

    return {"result": result}


def no_evidence_node(
    state: ResearchState,
    runtime: Runtime[ResearchContext],
) -> dict[str, ResearchResult]:
    request = state["request"]

    reason = state.get("stop_reason")
    if not reason:
        reason = (
            "Search returned candidate sources, but no usable content was extracted."
            if state.get("hits")
            else "No evidence was returned by the search provider."
        )

    result = ResearchResult(
        answer="Insufficient evidence to answer the research question.",
        claims=[],
        citations=[],
        as_of=request.as_of,
        warnings=[
            *state.get("pipeline_warnings", []),
            reason,
        ],
        trace_id=runtime.context["trace_id"],
    )

    return {"result": result}


def build_research_graph(
    *,
    search_provider: SearchProvider,
    extraction_provider: ExtractionProvider,
    synthesis_provider: SynthesisProvider,
    scope_provider: ScopeProvider | None = None,
    selection_provider: SelectionProvider | None = None,
) -> CompiledStateGraph:
    if (scope_provider is None) != (selection_provider is None):
        raise ValueError(
            "scope_provider and selection_provider must be configured together."
        )

    builder = StateGraph(
        ResearchState,
        context_schema=ResearchContext,
    )

    builder.add_node("plan", plan_node)
    builder.add_node("search", partial(search_node, search_provider=search_provider))

    builder.add_node(
        "extract", partial(extract_node, extraction_provider=extraction_provider)
    )

    builder.add_node(
        "synthesize", partial(synthesize_node, synthesis_provider=synthesis_provider)
    )

    builder.add_node("no_evidence", partial(no_evidence_node))

    builder.add_edge(START, "plan")

    if scope_provider is not None and selection_provider is not None:
        builder.add_node(
            "scope",
            partial(scope_node, scope_provider=scope_provider),
        )
        builder.add_node(
            "select",
            partial(selection_node, selection_provider=selection_provider),
        )

        builder.add_edge("plan", "scope")
        builder.add_conditional_edges(
            "scope",
            route_after_scope,
            {
                "search": "search",
                "no_evidence": "no_evidence",
            },
        )
        builder.add_conditional_edges(
            "search",
            route_after_search,
            {
                "select": "select",
                "no_evidence": "no_evidence",
            },
        )
        builder.add_conditional_edges(
            "select",
            route_after_selection,
            {
                "extract": "extract",
                "no_evidence": "no_evidence",
            },
        )
    else:
        builder.add_edge("plan", "search")
        builder.add_conditional_edges(
            "search",
            route_after_search,
            {
                "extract": "extract",
                "no_evidence": "no_evidence",
            },
        )

    builder.add_conditional_edges(
        "extract",
        route_after_extract,
        {
            "synthesize": "synthesize",
            "no_evidence": "no_evidence",
        },
    )

    builder.add_edge("synthesize", END)
    builder.add_edge("no_evidence", END)

    return builder.compile()
