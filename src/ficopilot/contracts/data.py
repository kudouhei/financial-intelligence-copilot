from datetime import date
from decimal import Decimal
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
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


class FinancialFactInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    entity_code: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^[A-Z0-9_-]+$",
    )
    fiscal_year: int = Field(ge=1900, le=2100)
    period_type: Literal["annual", "quarterly"]
    fiscal_quarter: int = Field(ge=0, le=4)
    period_end: date

    metric_code: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9_]+$",
    )
    metric_value: Decimal

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )

    source_document: NonBlankText
    source_page: int = Field(ge=1)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_empty_currency(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str) and not value.strip():
            return None

        return value

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if self.period_type == "annual" and self.fiscal_quarter != 0:
            raise ValueError("Annual periods must use fiscal_quarter=0.")

        if self.period_type == "quarterly" and self.fiscal_quarter == 0:
            raise ValueError("Quarterly periods must use fiscal_quarter=1..4.")

        return self


class FinancialFactLoadResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: NonBlankText
    rows_read: int = Field(ge=0)
    periods_created: int = Field(ge=0)
    facts_upserted: int = Field(ge=0)
