from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ficopilot.contracts.scope import ResearchScope
from ficopilot.contracts.selection import SourceDecision


class SourceScreening(SourceDecision):
    title: str
    url: HttpUrl


class ResearchProcess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ResearchScope | None = None

    candidate_count: int | None = Field(default=None, ge=0)
    selected_count: int | None = Field(default=None, ge=0)
    extracted_count: int | None = Field(default=None, ge=0)

    sources: list[SourceScreening] = Field(default_factory=list)
    stop_reason: str | None = None
