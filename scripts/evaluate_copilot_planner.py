from dataclasses import dataclass

from ficopilot.config import Settings
from ficopilot.contracts import CopilotRequest
from ficopilot.copilot.azure_planner import AzureCopilotPlanner
from ficopilot.data_agent.database import create_database_engine
from ficopilot.data_agent.schema_catalog import PostgresSchemaCatalog


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    request: CopilotRequest
    document_context: str
    expected_routes: set[str]


def selected_routes(
    *,
    research_question: str | None,
    document_question: str | None,
    data_question: str | None,
) -> set[str]:
    routes: set[str] = set()

    if research_question is not None:
        routes.add("research")

    if document_question is not None:
        routes.add("document")

    if data_question is not None:
        routes.add("data")

    return routes


def main() -> None:
    settings = Settings()

    planner = AzureCopilotPlanner(
        config=settings.require_azure_openai_config(),
    )

    engine = create_database_engine(settings.require_data_agent_database_config())

    data_context = PostgresSchemaCatalog(
        engine=engine,
    ).describe()

    cases = [
        EvaluationCase(
            name="combined_document_and_data",
            request=CopilotRequest(
                question=(
                    "How does the EIB manage liquidity risk, "
                    "and what was its 2024 liquidity coverage ratio?"
                ),
                document_id="doc-eib-evaluation",
            ),
            document_context=(
                "Selected PDF: eib-financial-report-2024.pdf; page count: 320."
            ),
            expected_routes={"document", "data"},
        ),
        EvaluationCase(
            name="data_only",
            request=CopilotRequest(
                question=("What was the EIB liquidity coverage ratio in 2024?"),
            ),
            document_context="No PDF selected.",
            expected_routes={"data"},
        ),
        EvaluationCase(
            name="public_research_only",
            request=CopilotRequest(
                question=(
                    "What market-related financial risks did "
                    "Microsoft disclose in its 2025 Annual Report?"
                ),
            ),
            document_context="No PDF selected.",
            expected_routes={"research"},
        ),
    ]

    all_passed = True

    for case in cases:
        plan = planner.plan(
            case.request,
            document_context=case.document_context,
            data_context=data_context,
        )

        actual_routes = selected_routes(
            research_question=plan.research_question,
            document_question=plan.document_question,
            data_question=plan.data_question,
        )

        passed = not plan.cannot_answer and actual_routes == case.expected_routes

        all_passed = all_passed and passed

        print(f"{case.name}: {'PASS' if passed else 'FAIL'}")
        print(f"  expected={sorted(case.expected_routes)}")
        print(f"  actual={sorted(actual_routes)}")
        print(f"  reason={plan.routing_reason}")

    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
