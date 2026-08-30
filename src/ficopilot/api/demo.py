from fastapi import FastAPI

from ficopilot.api.app import create_app
from ficopilot.contracts import (
    Citation,
    Claim,
    ResearchRequest,
    SynthesisDraft,
)
from ficopilot.research.graph import build_research_graph
from ficopilot.research.service import LangGraphResearchService

DEMO_EVIDENCE_TEXT = (
    "Company A identifies liquidity risk and market risk as material financial risks."
)


class DemoSearchProvider:
    def search(self, request: ResearchRequest) -> list[Citation]:
        citations = [
            Citation(
                citation_id="demo-company-a-risk",
                title="Demo Company A Annual Report",
                url="https://example.com/company-a-annual-report",
                published_at=None,
                retrieved_at=request.as_of,
                excerpt=DEMO_EVIDENCE_TEXT,
            )
        ]
        return citations[: request.max_sources]


class DemoSynthesisProvider:
    def synthesize(
        self, request: ResearchRequest, citations: list[Citation]
    ) -> SynthesisDraft:
        citation = citations[0]

        return SynthesisDraft(
            answer=citation.excerpt,
            claims=[
                Claim(
                    statement=citation.excerpt,
                    citation_ids=[citation.citation_id],
                )
            ],
            warnings=["Demo mode: response uses deterministic sample evidence."],
        )


def create_demo_app() -> FastAPI:
    graph = build_research_graph(
        search_provider=DemoSearchProvider(),
        synthesis_provider=DemoSynthesisProvider(),
    )
    service = LangGraphResearchService(graph=graph)

    return create_app(research_service=service)
