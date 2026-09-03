from datetime import UTC, datetime

from ficopilot.config import Settings
from ficopilot.contracts import ResearchRequest
from ficopilot.research.azure_scope_provider import (
    AzureResearchScopeProvider,
)


def main() -> None:
    settings = Settings()
    provider = AzureResearchScopeProvider(
        config=settings.require_azure_openai_config(),
    )

    questions = [
        (
            "What market-related financial risks does Microsoft "
            "disclose in its 2025 Annual Report?"
        ),
        (
            "What market-related financial risks does Microsoft "
            "disclose in its latest annual report?"
        ),
        "What financial risks does Microsoft face?",
    ]

    for question in questions:
        request = ResearchRequest(
            question=question,
            as_of=datetime.now(UTC),
            max_sources=5,
        )

        scope = provider.identify(request)

        print(f"\nQuestion: {question}")
        print(scope.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
