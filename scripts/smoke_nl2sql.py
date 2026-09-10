from ficopilot.config import Settings
from ficopilot.data_agent.azure_sql_provider import (
    AzureSqlGenerationProvider,
)
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.sql_executor import (
    SafeSqlExecutor,
)
from ficopilot.data_agent.schema_catalog import (
    PostgresSchemaCatalog,
)


def main() -> None:
    question = "What were the EIB liquidity coverage ratio values in 2023 and 2024?"

    settings = Settings()

    model_config = settings.require_azure_openai_config()
    database_config = settings.require_data_agent_database_config()

    provider = AzureSqlGenerationProvider(
        config=model_config,
    )

    engine = create_database_engine(database_config)

    catalog = PostgresSchemaCatalog(engine=engine)
    schema_context = catalog.describe()

    executor = SafeSqlExecutor(
        engine=engine,
        max_rows=50,
    )
    draft = provider.generate(
        question,
        schema_context=schema_context,
    )

    print(f"question={question}")
    print(f"cannot_answer={draft.cannot_answer}")
    print(f"explanation={draft.explanation}")
    print(f"assumptions={draft.assumptions}")
    print(f"sql=\n{draft.sql}")

    if draft.cannot_answer:
        return

    result = executor.execute(draft.sql)

    print(f"columns={result.columns}")
    print(f"rows={result.rows}")
    print(f"row_count={result.row_count}")
    print(f"truncated={result.truncated}")


if __name__ == "__main__":
    main()
