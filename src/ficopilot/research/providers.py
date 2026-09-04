from typing import Protocol

from ficopilot.contracts import (
    Citation,
    ResearchRequest,
    ResearchScope,
    SearchHit,
    SourceSelection,
    SynthesisDraft,
)


class SearchProvider(Protocol):
    def search(
        self,
        request: ResearchRequest,
    ) -> list[SearchHit]: ...


class SynthesisProvider(Protocol):
    def synthesize(
        self,
        request: ResearchRequest,
        citations: list[Citation],
    ) -> SynthesisDraft: ...


class ExtractionProvider(Protocol):
    def extract(
        self,
        request: ResearchRequest,
        hits: list[SearchHit],
        *,
        evidence_query: str | None = None,
    ) -> list[Citation]: ...


class ScopeProvider(Protocol):
    def identify(
        self,
        request: ResearchRequest,
    ) -> ResearchScope: ...


class SelectionProvider(Protocol):
    def select(
        self,
        request: ResearchRequest,
        scope: ResearchScope,
        hits: list[SearchHit],
    ) -> SourceSelection: ...
