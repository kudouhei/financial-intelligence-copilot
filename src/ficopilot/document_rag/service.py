from typing import Protocol

from ficopilot.contracts import (
    DocumentAnswer,
    DocumentAnswerDraft,
    DocumentCitation,
    DocumentQuestion,
    DocumentRecord,
    DocumentUploadResult,
    RetrievedChunk,
)
from ficopilot.document_rag.ingestion import PdfIngestionService
from ficopilot.document_rag.vector_index import DocumentIndex


class DocumentNotFoundError(Exception):
    """Raised when a requested document has not been ingested."""


class DocumentAnswerProvider(Protocol):
    def answer(
        self,
        question: str,
        evidence: list[RetrievedChunk],
    ) -> DocumentAnswerDraft: ...


class DocumentRagService:
    def __init__(
        self,
        *,
        ingestion_service: PdfIngestionService,
        index: DocumentIndex,
        answer_provider: DocumentAnswerProvider,
    ) -> None:
        self._ingestion_service = ingestion_service
        self._index = index
        self._answer_provider = answer_provider

        # Registered documents available for question answering.
        self._documents: dict[str, DocumentRecord] = {}

        # In-process ingestion cache:
        # sha256 -> previous upload result
        self._uploads_by_sha256: dict[str, DocumentUploadResult] = {}

    def ingest_pdf(
        self,
        *,
        filename: str,
        file_bytes: bytes,
    ) -> DocumentUploadResult:
        # This performs lightweight validation and calculates SHA-256.
        # It does not parse, chunk, or embed the PDF.
        identity = self._ingestion_service.identify(
            filename=filename,
            file_bytes=file_bytes,
        )

        cached_result = self._uploads_by_sha256.get(identity.sha256)

        # The same PDF has already been extracted, chunked and indexed
        # during the lifetime of this service instance.
        if cached_result is not None:
            return cached_result.model_copy(
                update={"cache_hit": True},
            )

        # Cache miss: run the expensive ingestion pipeline.
        ingestion_result = self._ingestion_service.ingest_bytes(
            filename=filename,
            file_bytes=file_bytes,
        )

        indexed_count = 0

        if ingestion_result.chunks:
            indexed_count = self._index.add_chunks(
                ingestion_result.chunks,
            )

        if indexed_count != len(ingestion_result.chunks):
            raise RuntimeError("Not all document chunks were indexed.")

        document = ingestion_result.document

        # Register the document so it can be used by ask().
        self._documents[document.document_id] = document

        upload_result = DocumentUploadResult(
            document=document,
            chunk_count=len(ingestion_result.chunks),
            warnings=ingestion_result.warnings,
            cache_hit=False,
        )

        # Only cache after extraction and indexing succeed.
        # This prevents a partially indexed document from being cached.
        self._uploads_by_sha256[document.sha256] = upload_result

        return upload_result

    def ask(
        self,
        request: DocumentQuestion,
    ) -> DocumentAnswer:
        self.get_document_record(request.document_id)

        retrieved_chunks = self._index.search(
            request.question,
            k=request.top_k,
            document_id=request.document_id,
        )

        if not retrieved_chunks:
            return DocumentAnswer(
                document_id=request.document_id,
                question=request.question,
                answer="Insufficient document evidence to answer the question.",
                citations=[],
                insufficient_evidence=True,
                warnings=["No chunks were retrieved for the document."],
            )

        draft = self._answer_provider.answer(
            request.question,
            retrieved_chunks,
        )

        # An insufficient-evidence answer must not expose citations,
        # even if the model unexpectedly returned chunk IDs.
        effective_cited_chunk_ids = (
            [] if draft.insufficient_evidence else draft.cited_chunk_ids
        )

        chunks_by_id = {chunk.chunk_id: chunk for chunk in retrieved_chunks}

        unknown_ids = set(effective_cited_chunk_ids) - set(chunks_by_id)

        if unknown_ids:
            raise ValueError(
                f"The answer cited unknown chunk IDs: {sorted(unknown_ids)}"
            )

        citations = [
            DocumentCitation(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                excerpt=chunk.content,
                similarity_score=chunk.similarity_score,
            )
            for chunk_id in effective_cited_chunk_ids
            if (chunk := chunks_by_id.get(chunk_id)) is not None
        ]

        warnings = list(draft.warnings)

        if draft.insufficient_evidence and not warnings:
            warnings.append("The retrieved evidence was insufficient.")

        return DocumentAnswer(
            document_id=request.document_id,
            question=request.question,
            answer=draft.answer,
            citations=citations,
            insufficient_evidence=draft.insufficient_evidence,
            warnings=warnings,
        )

    def get_document_record(
        self,
        document_id: str,
    ) -> DocumentRecord:
        record = self._documents.get(document_id)

        if record is None:
            raise DocumentNotFoundError(f"Document not found: {document_id}")

        return record.model_copy(deep=True)
