from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, status

from ficopilot.api.data_routes import create_data_router
from ficopilot.api.document_routes import create_document_router
from ficopilot.contracts import ResearchRequest, ResearchResult
from ficopilot.data_agent.service import DataAgentService
from ficopilot.document_rag.service import DocumentRagService
from ficopilot.research.service import ResearchService


def create_app(
    *,
    research_service: ResearchService | None = None,
    document_service: DocumentRagService | None = None,
    data_service: DataAgentService | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Financial Intelligence Copilot API",
        version="0.1.0",
    )

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/api/v1/research",
        response_model=ResearchResult,
        tags=["research"],
    )
    def run_research(
        request: ResearchRequest,
        x_trace_id: Annotated[str | None, Header()] = None,
    ) -> ResearchResult:
        if research_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Research service is not configured.",
            )

        trace_id = x_trace_id or str(uuid4())

        return research_service.run(
            request,
            trace_id=trace_id,
        )

    app.include_router(
        create_document_router(
            document_service=document_service,
        )
    )

    app.include_router(
        create_data_router(
            data_service=data_service,
        )
    )

    return app
