from typing import Protocol

from ficopilot.contracts import (
    DataAgentResult,
    DataAnswerDraft,
    DataQuestion,
    SqlDraft,
    SqlQueryResult,
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


class SqlExecutor(Protocol):
    def execute(self, sql: str) -> SqlQueryResult: ...


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
        schema_context = self._schema_catalog.describe()

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

        query_result = self._sql_executor.execute(draft.sql)

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
            warnings=answer_draft.warnings,
        )
