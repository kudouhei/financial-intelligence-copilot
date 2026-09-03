from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResearchScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    companies: list[str] = Field(
        description=(
            "Companies explicitly named in the question. "
            "Use an empty list if none are specified."
        )
    )

    document_types: list[
        Literal[
            "annual_report",
            "quarterly_report",
            "current_report",
            "earnings_release",
        ]
    ] = Field(
        description=(
            "Document types explicitly requested by the user. "
            "Use an empty list if no supported document type is specified."
        )
    )

    report_years: list[int] = Field(
        description=(
            "Report years explicitly requested in the question. "
            "Do not infer years from latest, the current date, "
            "publication dates, or the information cutoff."
        )
    )

    latest_requested: bool = Field(
        description=(
            "Whether the user explicitly requests the latest or most recent report."
        )
    )

    evidence_query: str = Field(
        min_length=1,
        description=(
            "A concise query for locating relevant passages within selected "
            "documents. Preserve the question's topic without answering it. "
            "This is a retrieval hint, not an additional scope constraint."
        ),
    )
