from uuid import UUID

from fastapi.testclient import TestClient

from ficopilot.api.app import create_app
from ficopilot.contracts import ResearchRequest, ResearchResult


class FakeResearchService:
    def __init__(self) -> None:
        self.calls: list[tuple[ResearchRequest, str]] = []

    def run(
        self,
        request: ResearchRequest,
        *,
        trace_id: str,
    ) -> ResearchResult:
        self.calls.append((request, trace_id))

        return ResearchResult(
            answer="Company A faces liquidity risk.",
            claims=[],
            citations=[],
            as_of=request.as_of,
            warnings=[],
            trace_id=trace_id,
        )


def test_health_check_returns_ok() -> None:
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_endpoint_runs_service() -> None:
    research_service = FakeResearchService()
    app = create_app(research_service=research_service)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            headers={"X-Trace-ID": "trace-api-001"},
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-29T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "Company A faces liquidity risk."
    assert response.json()["trace_id"] == "trace-api-001"

    request, trace_id = research_service.calls[0]
    assert isinstance(request, ResearchRequest)
    assert request.question == "What are the main risks facing Company A?"
    assert trace_id == "trace-api-001"


def test_research_endpoint_returns_503_without_service() -> None:
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-29T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "Research service is not configured."}


def test_research_endpoint_generates_trace_id() -> None:
    research_service = FakeResearchService()
    app = create_app(research_service=research_service)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-29T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 200

    generated_trace_id = response.json()["trace_id"]
    assert UUID(generated_trace_id).version == 4

    _, service_trace_id = research_service.calls[0]
    assert service_trace_id == generated_trace_id
