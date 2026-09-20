from datetime import UTC, datetime

from ficopilot.contracts import (
    DocumentRecord,
    DocumentUploadResult,
)
from ficopilot.document_rag.registry import (
    InMemoryDocumentRegistry,
)


def test_in_memory_registry_round_trip() -> None:
    registry = InMemoryDocumentRegistry()

    document = DocumentRecord(
        document_id="doc-test",
        filename="report.pdf",
        media_type="application/pdf",
        sha256="a" * 64,
        page_count=10,
        ingested_at=datetime(2026, 9, 20, tzinfo=UTC),
    )

    upload_result = DocumentUploadResult(
        document=document,
        chunk_count=25,
        warnings=[],
        cache_hit=False,
    )

    registry.save(upload_result)

    stored_document = registry.get_by_id("doc-test")
    cached_upload = registry.find_by_sha256("a" * 64)

    assert stored_document == document
    assert cached_upload == upload_result
    assert stored_document is not document
    assert cached_upload is not upload_result
