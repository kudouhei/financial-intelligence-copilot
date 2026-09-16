from datetime import UTC, datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    model_validator,
)

from ficopilot.contracts.data import DataAgentResult
from ficopilot.contracts.document import DocumentAnswer
from ficopilot.contracts.research import ResearchResult

QuestionText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3),
]

NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class CopilotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: QuestionText
    document_id: NonBlankText | None = None
    as_of: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))


class CopilotPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    research_question: QuestionText | None
    document_question: QuestionText | None
    data_question: QuestionText | None
    cannot_answer: bool
    routing_reason: NonBlankText

    @model_validator(mode="after")
    def validate_routes(self) -> Self:
        has_route = any(
            (
                self.research_question,
                self.document_question,
                self.data_question,
            )
        )

        if self.cannot_answer and has_route:
            raise ValueError("A cannot-answer plan must not route to a module.")

        if not self.cannot_answer and not has_route:
            raise ValueError("An answerable plan needs at least one module.")

        return self


class CopilotEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: CopilotRequest
    plan: CopilotPlan
    trace_id: NonBlankText
    research_result: ResearchResult | None = None
    document_result: DocumentAnswer | None = None
    data_result: DataAgentResult | None = None


class CopilotSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: NonBlankText
    module: Literal["research", "document", "data"]
    label: NonBlankText
    excerpt: NonBlankText
    url: HttpUrl | None = None
    page_number: int | None = Field(default=None, ge=1)


class CopilotSynthesisDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: NonBlankText
    cited_source_ids: list[NonBlankText]
    coverage: Literal["complete", "partial", "insufficient"]
    warnings: list[NonBlankText]

    @model_validator(mode="after")
    def validate_citations(self) -> Self:
        if len(self.cited_source_ids) != len(set(self.cited_source_ids)):
            raise ValueError("Cited source IDs must be unique.")

        if self.coverage == "insufficient" and self.cited_source_ids:
            raise ValueError("An insufficient answer must not cite unrelated sources.")

        if self.coverage != "insufficient" and not self.cited_source_ids:
            raise ValueError("A supported answer must cite at least one source.")

        return self
