from math import sqrt

from langchain_openai import OpenAIEmbeddings

from ficopilot.config import Settings

DOCUMENTS = [
    ("The bank maintains liquidity buffers and diversifies its funding sources."),
    (
        "Credit risk is the possibility that a borrower "
        "fails to meet its financial obligations."
    ),
    "The EIB finances climate and infrastructure projects.",
]

QUERY = "How does the bank manage funding-related risk?"


def cosine_similarity(
    left: list[float],
    right: list[float],
) -> float:
    dot_product = sum(
        left_value * right_value
        for left_value, right_value in zip(
            left,
            right,
            strict=True,
        )
    )
    left_length = sqrt(sum(value * value for value in left))
    right_length = sqrt(sum(value * value for value in right))

    return dot_product / (left_length * right_length)


def main() -> None:
    settings = Settings()
    config = settings.require_azure_openai_embedding_config()

    embeddings = OpenAIEmbeddings(
        model=config.deployment,
        base_url=config.base_url,
        api_key=config.api_key,
    )

    document_vectors = embeddings.embed_documents(DOCUMENTS)
    query_vector = embeddings.embed_query(QUERY)

    print(f"documents={len(document_vectors)}")
    print(f"dimensions={len(query_vector)}")
    print(f"query={QUERY}")

    scored_documents = [
        (
            cosine_similarity(query_vector, vector),
            document,
        )
        for document, vector in zip(
            DOCUMENTS,
            document_vectors,
            strict=True,
        )
    ]

    for score, document in sorted(
        scored_documents,
        reverse=True,
    ):
        print(f"\nscore={score:.4f}")
        print(document)


if __name__ == "__main__":
    main()
