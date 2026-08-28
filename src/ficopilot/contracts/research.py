from collections import Counter
from typing import Annotated, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    model_validator,
)


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=3),
    ]
    as_of: AwareDatetime
    max_sources: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    url: HttpUrl
    # original publication date
    published_at: AwareDatetime | None = None
    # date and time the content was retrieved
    retrieved_at: AwareDatetime
    # excerpt of the content
    excerpt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statement: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    citation_ids: list[str] = Field(min_length=1)


class SynthesisDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    claims: list[Claim]
    warnings: list[str] = Field(default_factory=list)


class ResearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    claims: list[Claim]
    citations: list[Citation]
    as_of: AwareDatetime
    warnings: list[str] = Field(default_factory=list)
    trace_id: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]

    @model_validator(mode="after")
    def validate_citation_references(self) -> Self:
        citation_ids = [citation.citation_id for citation in self.citations]
        duplicate_ids = sorted(
            citation_id
            for citation_id, count in Counter(citation_ids).items()
            if count > 1
        )

        if duplicate_ids:
            duplicate_ids_text = ", ".join(duplicate_ids)
            raise ValueError(f"Duplicate citation IDs: {duplicate_ids_text}")

        available_ids = set(citation_ids)
        referenced_ids = {
            citation_id for claim in self.claims for citation_id in claim.citation_ids
        }
        missing_ids = sorted(referenced_ids - available_ids)

        if missing_ids:
            missing_ids_text = ", ".join(missing_ids)
            raise ValueError(f"Unknown citation IDs: {missing_ids_text}")

        return self
