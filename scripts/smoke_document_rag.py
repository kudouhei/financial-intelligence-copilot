from argparse import ArgumentParser
from pathlib import Path

from langchain_openai import OpenAIEmbeddings

from ficopilot.config import Settings
from ficopilot.contracts import DocumentQuestion
from ficopilot.document_rag.azure_answer_provider import (
    AzureDocumentAnswerProvider,
)
from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)
from ficopilot.document_rag.service import (
    DocumentRagService,
)
from ficopilot.document_rag.vector_index import (
    InMemoryDocumentIndex,
)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("questions", nargs="+")
    args = parser.parse_args()

    settings = Settings()

    embedding_config = settings.require_azure_openai_embedding_config()
    chat_config = settings.require_azure_openai_config()

    embeddings = OpenAIEmbeddings(
        model=embedding_config.deployment,
        base_url=embedding_config.base_url,
        api_key=embedding_config.api_key,
        chunk_size=64,
        timeout=60,
        max_retries=3,
    )

    ingestion = PdfIngestionService().ingest(args.pdf_path)

    index = InMemoryDocumentIndex(embeddings=embeddings)

    print(
        f"indexing={len(ingestion.chunks)} chunks",
        flush=True,
    )
    indexed = index.add_chunks(ingestion.chunks)
    print(f"indexed={indexed}")

    service = DocumentRagService(
        index=index,
        answer_provider=AzureDocumentAnswerProvider(config=chat_config),
    )

    for question in args.questions:
        result = service.ask(
            DocumentQuestion(
                document_id=ingestion.document.document_id,
                question=question,
                top_k=5,
            )
        )

        print(f"\nQUESTION\n{result.question}")
        print(f"\nANSWER\n{result.answer}")
        print(f"\nINSUFFICIENT_EVIDENCE={result.insufficient_evidence}")

        print("\nCITATIONS")
        for citation in result.citations:
            print(
                f"- page={citation.page_number} "
                f"score={citation.similarity_score:.4f} "
                f"chunk_id={citation.chunk_id}"
            )

        print("\nWARNINGS")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
