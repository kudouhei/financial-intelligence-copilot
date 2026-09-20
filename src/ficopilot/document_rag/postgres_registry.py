from sqlalchemy import Engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ficopilot.contracts import (
    DocumentRecord,
    DocumentUploadResult,
)
from ficopilot.document_rag.models import StoredDocument


class PostgresDocumentRegistry:
    def __init__(
        self,
        *,
        engine: Engine,
    ) -> None:
        self._engine = engine

    def find_by_sha256(
        self,
        sha256: str,
    ) -> DocumentUploadResult | None:
        with Session(self._engine) as session:
            stored = session.scalar(
                select(StoredDocument).where(
                    StoredDocument.sha256 == sha256,
                )
            )

            if stored is None:
                return None

            return self._to_upload_result(stored)

    def get_by_id(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        with Session(self._engine) as session:
            stored = session.get(
                StoredDocument,
                document_id,
            )

            if stored is None:
                return None

            return self._to_document_record(stored)

    def save(
        self,
        upload_result: DocumentUploadResult,
    ) -> None:
        document = upload_result.document

        statement = insert(StoredDocument).values(
            document_id=document.document_id,
            sha256=document.sha256,
            filename=document.filename,
            media_type=document.media_type,
            page_count=document.page_count,
            chunk_count=upload_result.chunk_count,
            warnings=upload_result.warnings,
            ingested_at=document.ingested_at,
        )

        statement = statement.on_conflict_do_update(
            index_elements=[StoredDocument.sha256],
            set_={
                "filename": statement.excluded.filename,
                "media_type": statement.excluded.media_type,
                "page_count": statement.excluded.page_count,
                "chunk_count": statement.excluded.chunk_count,
                "warnings": statement.excluded.warnings,
                "ingested_at": statement.excluded.ingested_at,
            },
        )

        with self._engine.begin() as connection:
            connection.execute(statement)

    @staticmethod
    def _to_document_record(
        stored: StoredDocument,
    ) -> DocumentRecord:
        return DocumentRecord(
            document_id=stored.document_id,
            filename=stored.filename,
            media_type=stored.media_type,
            sha256=stored.sha256,
            page_count=stored.page_count,
            ingested_at=stored.ingested_at,
        )

    @classmethod
    def _to_upload_result(
        cls,
        stored: StoredDocument,
    ) -> DocumentUploadResult:
        return DocumentUploadResult(
            document=cls._to_document_record(stored),
            chunk_count=stored.chunk_count,
            warnings=list(stored.warnings),
            cache_hit=False,
        )
