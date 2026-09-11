from typing import Annotated, Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

NonBlankText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class SqlDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str
    explanation: NonBlankText
    assumptions: list[NonBlankText]
    cannot_answer: bool

    @model_validator(mode="after")
    def validate_sql_presence(self) -> Self:
        has_sql = bool(self.sql.strip())

        if self.cannot_answer and has_sql:
            raise ValueError("An unanswerable question must not contain SQL.")

        if not self.cannot_answer and not has_sql:
            raise ValueError("An answerable question must contain SQL.")

        return self


class SqlQueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int = Field(ge=0)
    truncated: bool


class DataQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: NonBlankText


class DataAgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: NonBlankText
    answer: NonBlankText
    draft: SqlDraft
    query_result: SqlQueryResult | None = None
    warnings: list[NonBlankText] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_query_result(self) -> Self:
        if self.draft.cannot_answer and self.query_result is not None:
            raise ValueError(
                "An unanswerable question must not contain a query result."
            )

        if not self.draft.cannot_answer and self.query_result is None:
            raise ValueError("An answerable question must contain a query result.")

        return self


class DataAnswerDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: NonBlankText
    warnings: list[NonBlankText] = Field(default_factory=list)
