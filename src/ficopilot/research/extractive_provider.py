from ficopilot.contracts import (
    Citation,
    Claim,
    ResearchRequest,
    SynthesisDraft,
)


class ExtractiveSynthesisProvider:
    def synthesize(
        self,
        request: ResearchRequest,
        citations: list[Citation],
    ) -> SynthesisDraft:
        if not citations:
            raise ValueError("Extractive synthesis requires evidence.")

        primary_citation = citations[0]

        return SynthesisDraft(
            answer=primary_citation.excerpt,
            claims=[
                Claim(
                    statement=citation.excerpt,
                    citation_ids=[citation.citation_id],
                )
                for citation in citations
            ],
            warnings=[
                (
                    "Live web search with deterministic "
                    "extractive synthesis; no LLM was used."
                ),
                "This output is not investment advice.",
            ],
        )
