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
