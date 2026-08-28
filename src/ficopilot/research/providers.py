from typing import Protocol

from ficopilot.contracts import Citation, ResearchRequest


class SearchProvider(Protocol):
    def search(
        self,
        request: ResearchRequest,
    ) -> list[Citation]: ...
