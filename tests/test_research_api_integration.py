from fastapi.testclient import TestClient

from ficopilot.api.app import create_app
from ficopilot.contracts import (
    Citation,
    Claim,
    ResearchRequest,
    SynthesisDraft,
)
from ficopilot.research.graph import build_research_graph
from ficopilot.research.service import LangGraphResearchService

EVIDENCE_TEXT = "Company A identifies liquidity risk as a material financial risk."


class StaticSearchProvider:
    def search(
        self,
        request: ResearchRequest,
    ) -> list[Citation]:
        return [
            Citation(
                citation_id="company-a-risk-001",
                title="Company A Annual Report",
                url="https://example.com/company-a-annual-report",
                published_at=None,
                retrieved_at=request.as_of,
                excerpt=EVIDENCE_TEXT,
            )
        ]


class EvidenceSynthesisProvider:
    def synthesize(
        self,
        request: ResearchRequest,
        citations: list[Citation],
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
        )


def test_research_api_runs_complete_vertical_slice() -> None:
    graph = build_research_graph(
        search_provider=StaticSearchProvider(),
        synthesis_provider=EvidenceSynthesisProvider(),
    )
    service = LangGraphResearchService(graph=graph)
    app = create_app(research_service=service)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            headers={"X-Trace-ID": "trace-integration-001"},
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-30T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["answer"] == EVIDENCE_TEXT
    assert result["trace_id"] == "trace-integration-001"
    assert result["claims"] == [
        {
            "statement": EVIDENCE_TEXT,
            "citation_ids": ["company-a-risk-001"],
        }
    ]
    assert result["citations"][0]["citation_id"] == "company-a-risk-001"
    assert result["citations"][0]["title"] == "Company A Annual Report"
