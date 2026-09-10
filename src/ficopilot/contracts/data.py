from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SqlQueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int = Field(ge=0)
    truncated: bool
