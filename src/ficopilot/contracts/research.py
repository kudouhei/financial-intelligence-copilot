from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=3),
    ]
    as_of: AwareDatetime
    max_sources: int = Field(default=5, ge=1, le=20)