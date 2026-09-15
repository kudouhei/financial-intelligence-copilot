from typing import Protocol

from ficopilot.contracts import (
    DataAgentResult,
    DataAnswerDraft,
    DataQuestion,
    SqlDraft,
    SqlQueryResult,
)
from ficopilot.data_agent.sql_executor import (
    SqlExecutionError,
    UnsafeSqlError,
)


class DataAnswerProvider(Protocol):
    def answer(
        self,
        *,
        question: str,
        sql_draft: SqlDraft,
        query_result: SqlQueryResult,
    ) -> DataAnswerDraft: ...


class SchemaCatalog(Protocol):
    def describe(self) -> str: ...


class SqlGenerationProvider(Protocol):
    def generate(
        self,
        question: str,
        *,
        schema_context: str,
    ) -> SqlDraft: ...

    def repair(
        self,
        question: str,
        *,
        schema_context: str,
        failed_sql: str,
        error_message: str,
    ) -> SqlDraft: ...


class SqlExecutor(Protocol):
    def execute(self, sql: str) -> SqlQueryResult: ...


class SqlRepairExhaustedError(RuntimeError):
    """Raised when SQL still fails after one repair attempt."""


class DataAgentService:
    def __init__(
        self,
        *,
        schema_catalog: SchemaCatalog,
        sql_provider: SqlGenerationProvider,
        sql_executor: SqlExecutor,
        answer_provider: DataAnswerProvider,
    ) -> None:
        self._schema_catalog = schema_catalog
        self._sql_provider = sql_provider
        self._sql_executor = sql_executor
        self._answer_provider = answer_provider

    def run(self, request: DataQuestion) -> DataAgentResult:
        schema_context = self.describe_available_data()

        draft = self._sql_provider.generate(
            request.question,
            schema_context=schema_context,
        )

        if draft.cannot_answer:
            return DataAgentResult(
                question=request.question,
                answer=draft.explanation,
                draft=draft,
                query_result=None,
            )

        warnings: list[str] = []

        try:
            query_result = self._sql_executor.execute(draft.sql)

        except (UnsafeSqlError, SqlExecutionError) as error:
            failed_sql = draft.sql

            draft = self._sql_provider.repair(
                request.question,
                schema_context=schema_context,
                failed_sql=failed_sql,
                error_message=str(error),
            )

            warnings.append(
                "The initial SQL failed validation or execution and was repaired once."
            )

            if draft.cannot_answer:
                return DataAgentResult(
                    question=request.question,
                    answer=draft.explanation,
                    draft=draft,
                    query_result=None,
                    warnings=warnings,
                )

            try:
                query_result = self._sql_executor.execute(draft.sql)
            except (UnsafeSqlError, SqlExecutionError) as final_error:
                raise SqlRepairExhaustedError(
                    "The generated SQL still failed after one repair attempt."
                ) from final_error

        answer_draft = self._answer_provider.answer(
            question=request.question,
            sql_draft=draft,
            query_result=query_result,
        )

        return DataAgentResult(
            question=request.question,
            answer=answer_draft.answer,
            draft=draft,
            query_result=query_result,
            warnings=[
                *warnings,
                *answer_draft.warnings,
            ],
        )

    def describe_available_data(self) -> str:
        return self._schema_catalog.describe()
