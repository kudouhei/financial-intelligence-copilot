from typing import Protocol

from ficopilot.contracts import Citation, ResearchRequest, SynthesisDraft


class SearchProvider(Protocol):
    def search(
        self,
        request: ResearchRequest,
    ) -> list[Citation]: ...


class SynthesisProvider(Protocol):
    def synthesize(
        self,
        request: ResearchRequest,
        citations: list[Citation],
    ) -> SynthesisDraft: ...
