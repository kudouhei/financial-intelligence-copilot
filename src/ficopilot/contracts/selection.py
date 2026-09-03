from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class SourceDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_index: int = Field(
        ge=0,
        description="The exact candidate index supplied in the input.",
    )

    action: Literal["keep", "exclude", "needs_verification"]

    reason: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ] = Field(
        description=(
            "A brief explanation based on the supplied candidate metadata. "
            "Mention the matching constraint, mismatch, or missing information."
        )
    )


class SourceSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisions: list[SourceDecision]
