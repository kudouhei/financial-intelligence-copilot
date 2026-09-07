from argparse import ArgumentParser
from pathlib import Path

from langchain_openai import OpenAIEmbeddings

from ficopilot.config import Settings
from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)
from ficopilot.document_rag.vector_index import (
    InMemoryDocumentIndex,
)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("query")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    settings = Settings()
    config = settings.require_azure_openai_embedding_config()

    embeddings = OpenAIEmbeddings(
        model=config.deployment,
        base_url=config.base_url,
        api_key=config.api_key,
        chunk_size=64,
        timeout=60,
        max_retries=3,
    )

    ingestion_result = PdfIngestionService().ingest(args.pdf_path)

    index = InMemoryDocumentIndex(embeddings=embeddings)

    print(
        f"indexing={len(ingestion_result.chunks)} chunks",
        flush=True,
    )

    indexed_count = index.add_chunks(ingestion_result.chunks)

    print(f"indexed={indexed_count}")
    print(f"query={args.query}")

    results = index.search(
        args.query,
        k=args.k,
    )

    for rank, result in enumerate(results, start=1):
        preview = " ".join(result.content.split())

        print(
            f"\nrank={rank} "
            f"score={result.similarity_score:.4f} "
            f"page={result.page_number} "
            f"chunk_id={result.chunk_id}"
        )
        print(preview[:700])


if __name__ == "__main__":
    main()
