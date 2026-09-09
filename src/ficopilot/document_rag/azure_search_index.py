from collections.abc import Sequence

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from langchain_core.embeddings import Embeddings

from ficopilot.contracts import DocumentChunk, RetrievedChunk


class AzureAiSearchDocumentIndex:
    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        index_name: str,
        embeddings: Embeddings,
        vector_dimensions: int = 1_536,
        upload_batch_size: int = 500,
    ) -> None:
        clean_endpoint = endpoint.strip().rstrip("/")
        clean_api_key = api_key.strip()
        clean_index_name = index_name.strip()

        if not clean_endpoint:
            raise ValueError("Azure AI Search endpoint is required.")

        if not clean_api_key:
            raise ValueError("Azure AI Search API key is required.")

        if not clean_index_name:
            raise ValueError("Azure AI Search index name is required.")

        if vector_dimensions <= 0:
            raise ValueError("vector_dimensions must be positive.")

        if upload_batch_size <= 0:
            raise ValueError("upload_batch_size must be positive.")

        self._embeddings = embeddings
        self._index_name = clean_index_name
        self._vector_dimensions = vector_dimensions
        self._upload_batch_size = upload_batch_size

        credential = AzureKeyCredential(clean_api_key)

        self._index_client = SearchIndexClient(
            endpoint=clean_endpoint,
            credential=credential,
        )

        self._create_index_if_missing()

        self._search_client = SearchClient(
            endpoint=clean_endpoint,
            index_name=clean_index_name,
            credential=credential,
        )

    def _create_index_if_missing(self) -> None:
        try:
            self._index_client.get_index(self._index_name)
            return
        except ResourceNotFoundError:
            pass

        fields = [
            SimpleField(
                name="chunk_id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SimpleField(
                name="document_id",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="page_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
            SimpleField(
                name="start_index",
                type=SearchFieldDataType.Int32,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self._vector_dimensions,
                vector_search_profile_name="document-vector-profile",
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="document-hnsw",
                ),
            ],
            profiles=[
                VectorSearchProfile(
                    name="document-vector-profile",
                    algorithm_configuration_name="document-hnsw",
                ),
            ],
        )

        index = SearchIndex(
            name=self._index_name,
            fields=fields,
            vector_search=vector_search,
        )

        self._index_client.create_index(index)

    def add_chunks(
        self,
        chunks: Sequence[DocumentChunk],
    ) -> int:
        if not chunks:
            return 0

        indexed_count = 0

        for start in range(
            0,
            len(chunks),
            self._upload_batch_size,
        ):
            batch = list(chunks[start : start + self._upload_batch_size])

            vectors = self._embeddings.embed_documents(
                [chunk.content for chunk in batch]
            )

            if len(vectors) != len(batch):
                raise RuntimeError("Embedding count does not match chunk count.")

            documents = [
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "start_index": chunk.start_index,
                    "content": chunk.content,
                    "content_vector": vector,
                }
                for chunk, vector in zip(
                    batch,
                    vectors,
                    strict=True,
                )
            ]

            results = self._search_client.merge_or_upload_documents(
                documents=documents,
            )

            failed_results = [result for result in results if not result.succeeded]

            if failed_results:
                failed_keys = [result.key for result in failed_results]

                raise RuntimeError(
                    f"Azure AI Search failed to index chunks: {failed_keys}"
                )

            indexed_count += len(results)

        return indexed_count

    def search(
        self,
        query: str,
        *,
        k: int = 5,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError("query must not be blank.")

        if k <= 0:
            raise ValueError("k must be positive.")

        filter_expression: str | None = None

        if document_id is not None:
            clean_document_id = document_id.strip()

            if not clean_document_id:
                raise ValueError("document_id must not be blank.")

            escaped_document_id = clean_document_id.replace(
                "'",
                "''",
            )

            filter_expression = f"document_id eq '{escaped_document_id}'"

        query_vector = self._embeddings.embed_query(clean_query)

        candidate_k = max(50, k)

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=candidate_k,
            fields="content_vector",
        )

        results = self._search_client.search(
            search_text=clean_query,
            search_fields=["content"],
            vector_queries=[vector_query],
            filter=filter_expression,
            select=[
                "chunk_id",
                "document_id",
                "page_number",
                "start_index",
                "content",
            ],
            top=k,
        )

        return [
            RetrievedChunk(
                chunk_id=str(result["chunk_id"]),
                document_id=str(result["document_id"]),
                page_number=int(result["page_number"]),
                start_index=int(result["start_index"]),
                content=str(result["content"]),
                similarity_score=float(result.get("@search.score", 0.0)),
            )
            for result in results
        ]
