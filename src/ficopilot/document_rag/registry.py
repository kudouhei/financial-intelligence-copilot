from typing import Protocol

from ficopilot.contracts import (
    DocumentRecord,
    DocumentUploadResult,
)


class DocumentRegistry(Protocol):
    def find_by_sha256(
        self,
        sha256: str,
    ) -> DocumentUploadResult | None: ...

    def get_by_id(
        self,
        document_id: str,
    ) -> DocumentRecord | None: ...

    def save(
        self,
        upload_result: DocumentUploadResult,
    ) -> None: ...


class InMemoryDocumentRegistry:
    def __init__(self) -> None:
        self._documents: dict[str, DocumentRecord] = {}
        self._uploads_by_sha256: dict[str, DocumentUploadResult] = {}

    def find_by_sha256(
        self,
        sha256: str,
    ) -> DocumentUploadResult | None:
        result = self._uploads_by_sha256.get(sha256)

        if result is None:
            return None

        return result.model_copy(deep=True)

    def get_by_id(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        record = self._documents.get(document_id)

        if record is None:
            return None

        return record.model_copy(deep=True)

    def save(
        self,
        upload_result: DocumentUploadResult,
    ) -> None:
        stored_result = upload_result.model_copy(
            update={"cache_hit": False},
            deep=True,
        )

        document = stored_result.document

        self._documents[document.document_id] = document
        self._uploads_by_sha256[document.sha256] = stored_result
