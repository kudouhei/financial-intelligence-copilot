from ficopilot.contracts.data import SqlDraft, SqlQueryResult
from ficopilot.contracts.document import (
    DocumentAnswer,
    DocumentAnswerDraft,
    DocumentChunk,
    DocumentCitation,
    DocumentIngestionResult,
    DocumentQuestion,
    DocumentRecord,
    DocumentUploadResult,
    RetrievedChunk,
)
from ficopilot.contracts.research import (
    Citation,
    Claim,
    ResearchRequest,
    ResearchResult,
    SearchHit,
    SynthesisDraft,
)
from ficopilot.contracts.scope import ResearchScope
from ficopilot.contracts.selection import SourceDecision, SourceSelection

__all__ = [
    "Citation",
    "Claim",
    "DocumentAnswer",
    "DocumentAnswerDraft",
    "DocumentChunk",
    "DocumentCitation",
    "DocumentIngestionResult",
    "DocumentQuestion",
    "DocumentRecord",
    "DocumentUploadResult",
    "ResearchRequest",
    "ResearchResult",
    "ResearchScope",
    "RetrievedChunk",
    "SearchHit",
    "SourceDecision",
    "SourceSelection",
    "SqlDraft",
    "SqlQueryResult",
    "SynthesisDraft",
]
