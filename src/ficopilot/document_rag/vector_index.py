from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore

from ficopilot.contracts import DocumentChunk, RetrievedChunk


class InMemoryDocumentIndex:
    def __init__(self, *, embeddings: Embeddings) -> None:
        self._vector_store = InMemoryVectorStore(embedding=embeddings)

    def add_chunks(
        self,
        chunks: Sequence[DocumentChunk],
    ) -> int:
        documents = [
            Document(
                page_content=chunk.content,
                metadata={
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "start_index": chunk.start_index,
                },
            )
            for chunk in chunks
        ]

        ids = self._vector_store.add_documents(
            documents=documents,
            ids=[chunk.chunk_id for chunk in chunks],
        )

        return len(ids)

    def search(
        self,
        query: str,
        *,
        k: int = 5,
    ) -> list[RetrievedChunk]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError("query must not be blank.")

        if k <= 0:
            raise ValueError("k must be positive.")

        results = self._vector_store.similarity_search_with_score(
            clean_query,
            k=k,
        )

        return [
            RetrievedChunk(
                chunk_id=str(document.metadata["chunk_id"]),
                document_id=str(document.metadata["document_id"]),
                page_number=int(document.metadata["page_number"]),
                start_index=int(document.metadata["start_index"]),
                content=document.page_content,
                similarity_score=score,
            )
            for document, score in results
        ]
