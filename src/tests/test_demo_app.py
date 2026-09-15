from fastapi.testclient import TestClient

from ficopilot.api.demo import create_demo_app


def test_demo_app_wires_complete_research_workflow() -> None:
    app = create_demo_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            headers={"X-Trace-ID": "trace-demo-001"},
            json={
                "question": "What are the main risks facing Company A?",
                "as_of": "2026-08-30T12:00:00Z",
                "max_sources": 5,
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["trace_id"] == "trace-demo-001"
    assert result["answer"]
    assert result["claims"]
    assert result["citations"]
    assert result["citations"][0]["citation_id"] == ("demo-company-a-risk")
