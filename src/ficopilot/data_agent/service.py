from typing import Protocol

from ficopilot.contracts import (
    DataAgentResult,
    DataQuestion,
    SqlDraft,
    SqlQueryResult,
)


class SchemaCatalog(Protocol):
    def describe(self) -> str: ...


class SqlGenerationProvider(Protocol):
    def generate(
        self,
        question: str,
        *,
        schema_context: str,
    ) -> SqlDraft: ...


class SqlExecutor(Protocol):
    def execute(self, sql: str) -> SqlQueryResult: ...


class DataAgentService:
    def __init__(
        self,
        *,
        schema_catalog: SchemaCatalog,
        sql_provider: SqlGenerationProvider,
        sql_executor: SqlExecutor,
    ) -> None:
        self._schema_catalog = schema_catalog
        self._sql_provider = sql_provider
        self._sql_executor = sql_executor

    def run(self, request: DataQuestion) -> DataAgentResult:
        schema_context = self._schema_catalog.describe()

        draft = self._sql_provider.generate(
            request.question,
            schema_context=schema_context,
        )

        if draft.cannot_answer:
            return DataAgentResult(
                question=request.question,
                draft=draft,
                query_result=None,
            )

        query_result = self._sql_executor.execute(draft.sql)

        return DataAgentResult(
            question=request.question,
            draft=draft,
            query_result=query_result,
        )
