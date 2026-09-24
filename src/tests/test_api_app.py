from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from ficopilot.api.app import create_app
from ficopilot.config import AppAccessConfig
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


def test_app_can_serve_frontend_build(
    tmp_path: Path,
) -> None:
    index_file = tmp_path / "index.html"
    index_file.write_text(
        "<html><body>Financial Intelligence Copilot</body></html>",
        encoding="utf-8",
    )

    app = create_app(frontend_dist_dir=tmp_path)

    with TestClient(app) as client:
        frontend_response = client.get("/")
        health_response = client.get("/health")

    assert frontend_response.status_code == 200
    assert "Financial Intelligence Copilot" in frontend_response.text

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}


def test_access_gate_rejects_request_before_service_runs() -> None:
    research_service = FakeResearchService()
    app = create_app(
        research_service=research_service,
        access_config=AppAccessConfig(
            username="demo-user",
            password="demo-password",
        ),
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-29T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 401
    assert response.headers["www-authenticate"].startswith("Basic")
    assert research_service.calls == []


def test_access_gate_accepts_valid_credentials() -> None:
    research_service = FakeResearchService()
    app = create_app(
        research_service=research_service,
        access_config=AppAccessConfig(
            username="demo-user",
            password="demo-password",
        ),
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            auth=("demo-user", "demo-password"),
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-29T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 200
    assert len(research_service.calls) == 1


def test_health_check_remains_public_when_access_gate_is_enabled() -> None:
    app = create_app(
        access_config=AppAccessConfig(
            username="demo-user",
            password="demo-password",
        ),
    )

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_access_gate_rejects_invalid_credentials() -> None:
    app = create_app(
        access_config=AppAccessConfig(
            username="demo-user",
            password="demo-password",
        ),
    )

    with TestClient(app) as client:
        response = client.get(
            "/docs",
            auth=("demo-user", "wrong-password"),
        )

    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
