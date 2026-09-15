from ficopilot.config import Settings
from ficopilot.contracts import CopilotRequest
from ficopilot.copilot.azure_planner import (
    AzureCopilotPlanner,
)
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.schema_catalog import (
    PostgresSchemaCatalog,
)


def main() -> None:
    settings = Settings()

    engine = create_database_engine(settings.require_data_agent_database_config())

    planner = AzureCopilotPlanner(config=settings.require_azure_openai_config())

    request = CopilotRequest(
        question=(
            "How does the EIB manage liquidity risk, "
            "and what was its 2024 liquidity coverage ratio?"
        ),
        document_id="doc-1de41668df03e9d9",
    )

    plan = planner.plan(
        request,
        document_context=(
            "Selected uploaded PDF: "
            "eib-financial-report-2024.pdf; "
            "entity EIB; report year 2024."
        ),
        data_context=PostgresSchemaCatalog(engine=engine).describe(),
    )

    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
