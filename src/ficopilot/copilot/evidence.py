import json

from ficopilot.contracts import CopilotEvidence, CopilotSource


def collect_sources(evidence: CopilotEvidence) -> list[CopilotSource]:
    sources: list[CopilotSource] = []

    if evidence.research_result is not None:
        for citation in evidence.research_result.citations:
            sources.append(
                CopilotSource(
                    source_id=f"research:{citation.citation_id}",
                    module="research",
                    label=citation.title,
                    excerpt=citation.excerpt,
                    url=citation.url,
                )
            )

    if evidence.document_result is not None:
        for citation in evidence.document_result.citations:
            sources.append(
                CopilotSource(
                    source_id=f"document:{citation.chunk_id}",
                    module="document",
                    label=f"Uploaded PDF, page {citation.page_number}",
                    excerpt=citation.excerpt,
                    page_number=citation.page_number,
                )
            )

    if (
        evidence.data_result is not None
        and evidence.data_result.query_result is not None
    ):
        for index, row in enumerate(
            evidence.data_result.query_result.rows,
            start=1,
        ):
            source_document = row.get("source_document")
            source_page = row.get("source_page")

            label = (
                source_document
                if isinstance(source_document, str) and source_document.strip()
                else "Database query result"
            )

            page_number = (
                source_page
                if isinstance(source_page, int) and source_page > 0
                else None
            )

            sources.append(
                CopilotSource(
                    source_id=f"data:row:{index}",
                    module="data",
                    label=label,
                    excerpt=json.dumps(row, default=str, ensure_ascii=False),
                    page_number=page_number,
                )
            )

    return sources
