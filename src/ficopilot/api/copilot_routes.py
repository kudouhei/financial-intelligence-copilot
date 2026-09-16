from fastapi import APIRouter, HTTPException, status

from ficopilot.contracts import CopilotAnswer, CopilotRequest
from ficopilot.copilot.service import CopilotOrchestrator
from ficopilot.data_agent.service import SqlRepairExhaustedError
from ficopilot.document_rag.service import DocumentNotFoundError


def create_copilot_router(
    *,
    copilot_service: CopilotOrchestrator | None,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1",
        tags=["copilot"],
    )

    @router.post(
        "/copilot/questions",
        response_model=CopilotAnswer,
    )
    def answer_copilot_question(
        request: CopilotRequest,
    ) -> CopilotAnswer:
        if copilot_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Copilot service is not configured.",
            )

        try:
            return copilot_service.run(request)

        except DocumentNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            ) from error

        except SqlRepairExhaustedError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    "The Data Agent could not produce a safe executable "
                    "query after one repair attempt."
                ),
            ) from error

    return router
