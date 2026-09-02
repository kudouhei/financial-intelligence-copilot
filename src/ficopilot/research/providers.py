from typing import Protocol

from ficopilot.contracts import Citation, ResearchRequest, SearchHit, SynthesisDraft


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
    ) -> list[Citation]: ...
