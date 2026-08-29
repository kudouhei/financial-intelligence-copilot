from typing import Protocol

from ficopilot.contracts import ResearchRequest, ResearchResult


class ResearchService(Protocol):
    def run(
        self,
        request: ResearchRequest,
        *,
        trace_id: str,
    ) -> ResearchResult: ...
