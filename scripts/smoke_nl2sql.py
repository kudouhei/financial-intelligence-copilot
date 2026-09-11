from ficopilot.config import Settings
from ficopilot.contracts import DataQuestion
from ficopilot.data_agent.azure_answer_provider import (
    AzureDataAnswerProvider,
)
from ficopilot.data_agent.azure_sql_provider import (
    AzureSqlGenerationProvider,
)
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.schema_catalog import (
    PostgresSchemaCatalog,
)
from ficopilot.data_agent.service import DataAgentService
from ficopilot.data_agent.sql_executor import (
    SafeSqlExecutor,
)


def main() -> None:
    # question = "What were the EIB liquidity coverage ratio values in 2023 and 2024?"
    question = "What was Microsoft's net income in 2024?"

    settings = Settings()

    model_config = settings.require_azure_openai_config()
    database_config = settings.require_data_agent_database_config()

    provider = AzureSqlGenerationProvider(
        config=model_config,
    )

    engine = create_database_engine(database_config)

    catalog = PostgresSchemaCatalog(engine=engine)

    executor = SafeSqlExecutor(
        engine=engine,
        max_rows=50,
    )
    answer_provider = AzureDataAnswerProvider(
        config=model_config,
    )

    service = DataAgentService(
        schema_catalog=catalog,
        sql_provider=provider,
        sql_executor=executor,
        answer_provider=answer_provider,
    )

    response = service.run(
        DataQuestion(question=question),
    )

    draft = response.draft

    print(f"answer={response.answer}")
    print(f"warnings={response.warnings}")

    print(f"question={response.question}")
    print(f"cannot_answer={draft.cannot_answer}")
    print(f"explanation={draft.explanation}")
    print(f"assumptions={draft.assumptions}")
    print(f"sql=\n{draft.sql}")

    if response.query_result is None:
        return

    result = response.query_result

    print(f"columns={result.columns}")
    print(f"rows={result.rows}")
    print(f"row_count={result.row_count}")
    print(f"truncated={result.truncated}")


if __name__ == "__main__":
    main()
