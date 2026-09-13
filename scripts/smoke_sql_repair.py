from ficopilot.config import Settings
from ficopilot.contracts import DataQuestion, SqlDraft
from ficopilot.data_agent.azure_answer_provider import (
    AzureDataAnswerProvider,
)
from ficopilot.data_agent.azure_sql_provider import (
    AzureSqlGenerationProvider,
)
from ficopilot.data_agent.database import create_database_engine
from ficopilot.data_agent.schema_catalog import PostgresSchemaCatalog
from ficopilot.data_agent.service import DataAgentService
from ficopilot.data_agent.sql_executor import SafeSqlExecutor


class FailOnceSqlProvider:
    """Inject invalid SQL, then delegate repair to Azure OpenAI."""

    def __init__(
        self,
        *,
        delegate: AzureSqlGenerationProvider,
    ) -> None:
        self._delegate = delegate

    def generate(
        self,
        question: str,
        *,
        schema_context: str,
    ) -> SqlDraft:
        return SqlDraft(
            sql=("SELECT missing_metric_value FROM financial_facts"),
            explanation="Deliberately injected invalid SQL.",
            assumptions=[],
            cannot_answer=False,
        )

    def repair(
        self,
        question: str,
        *,
        schema_context: str,
        failed_sql: str,
        error_message: str,
    ) -> SqlDraft:
        return self._delegate.repair(
            question,
            schema_context=schema_context,
            failed_sql=failed_sql,
            error_message=error_message,
        )


def main() -> None:
    question = "What were the EIB liquidity coverage ratio values in 2023 and 2024?"

    settings = Settings()
    model_config = settings.require_azure_openai_config()
    database_config = settings.require_data_agent_database_config()

    engine = create_database_engine(database_config)

    real_sql_provider = AzureSqlGenerationProvider(
        config=model_config,
    )

    service = DataAgentService(
        schema_catalog=PostgresSchemaCatalog(engine=engine),
        sql_provider=FailOnceSqlProvider(
            delegate=real_sql_provider,
        ),
        sql_executor=SafeSqlExecutor(
            engine=engine,
            max_rows=50,
        ),
        answer_provider=AzureDataAnswerProvider(
            config=model_config,
        ),
    )

    response = service.run(
        DataQuestion(question=question),
    )

    print(f"answer={response.answer}")
    print(f"warnings={response.warnings}")
    print(f"repaired_sql=\n{response.draft.sql}")
    print(f"rows={response.query_result.rows}")


if __name__ == "__main__":
    main()
