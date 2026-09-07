from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    status,
)

from ficopilot.contracts import (
    DocumentAnswer,
    DocumentQuestion,
    DocumentUploadResult,
)
from ficopilot.document_rag.service import (
    DocumentNotFoundError,
    DocumentRagService,
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def create_document_router(
    *,
    document_service: DocumentRagService | None,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1",
        tags=["document-rag"],
    )

    @router.post(
        "/documents",
        response_model=DocumentUploadResult,
        status_code=status.HTTP_201_CREATED,
    )
    def upload_document(
        file: UploadFile,
    ) -> DocumentUploadResult:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail=("Document RAG service is not configured."),
            )

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="A PDF filename is required.",
            )

        file_bytes = file.file.read(MAX_UPLOAD_BYTES + 1)

        if len(file_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The PDF exceeds the 25 MB limit.",
            )

        try:
            return document_service.ingest_pdf(
                filename=file.filename,
                file_bytes=file_bytes,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

    @router.post(
        "/document-questions",
        response_model=DocumentAnswer,
    )
    def answer_document_question(
        request: DocumentQuestion,
    ) -> DocumentAnswer:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail=("Document RAG service is not configured."),
            )

        try:
            return document_service.ask(request)
        except DocumentNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error),
            ) from error

    return router
