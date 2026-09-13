from fastapi import APIRouter, HTTPException, status

from ficopilot.contracts import DataAgentResult, DataQuestion
from ficopilot.data_agent.service import (
    DataAgentService,
    SqlRepairExhaustedError,
)


def create_data_router(
    *,
    data_service: DataAgentService | None,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1",
        tags=["data-agent"],
    )

    @router.post(
        "/data-questions",
        response_model=DataAgentResult,
    )
    def answer_data_question(
        request: DataQuestion,
    ) -> DataAgentResult:
        if data_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Data Agent service is not configured.",
            )

        try:
            return data_service.run(request)
        except SqlRepairExhaustedError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    "Unable to produce a safe executable SQL query "
                    "after one repair attempt."
                ),
            ) from error

    return router
