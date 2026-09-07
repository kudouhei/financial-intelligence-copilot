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
from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)
from ficopilot.document_rag.vector_index import (
    InMemoryDocumentIndex,
)


class DocumentNotFoundError(Exception):
    pass


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
        index: InMemoryDocumentIndex,
        answer_provider: DocumentAnswerProvider,
    ) -> None:
        self._ingestion_service = ingestion_service
        self._index = index
        self._answer_provider = answer_provider
        self._documents: dict[str, DocumentRecord] = {}

    def ingest_pdf(
        self,
        *,
        filename: str,
        file_bytes: bytes,
    ) -> DocumentUploadResult:
        result = self._ingestion_service.ingest_bytes(
            filename=filename,
            file_bytes=file_bytes,
        )
        indexed_count = 0
        if result.chunks:
            indexed_count = self._index.add_chunks(result.chunks)

        if indexed_count != len(result.chunks):
            raise RuntimeError("Not all document chunks were indexed.")

        self._documents[result.document.document_id] = result.document

        return DocumentUploadResult(
            document=result.document,
            chunk_count=indexed_count,
            warnings=result.warnings,
        )

    def ask(
        self,
        request: DocumentQuestion,
    ) -> DocumentAnswer:
        if request.document_id not in self._documents:
            raise DocumentNotFoundError(f"Document not found: {request.document_id}")

        retrieved_chunks = self._index.search(
            request.question,
            k=request.top_k,
            document_id=request.document_id,
        )

        if not retrieved_chunks:
            return DocumentAnswer(
                document_id=request.document_id,
                question=request.question,
                answer=("Insufficient document evidence to answer the question."),
                citations=[],
                insufficient_evidence=True,
                warnings=["No chunks were retrieved for the document."],
            )

        draft = self._answer_provider.answer(
            request.question,
            retrieved_chunks,
        )

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
            insufficient_evidence=(draft.insufficient_evidence),
            warnings=warnings,
        )
