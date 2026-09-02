import logging
from datetime import UTC, datetime
from hashlib import sha256

from langchain_core.tools import ToolException
from langchain_tavily import TavilyExtract
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ficopilot.contracts import Citation, ResearchRequest, SearchHit

logger = logging.getLogger(__name__)


class TavilyExtractResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: HttpUrl
    raw_content: str | None


class TavilyExtractResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    results: list[TavilyExtractResult]
    failed_results: list[dict[str, object]] = Field(default_factory=list)


class TavilyExtractionProvider:
    def __init__(self, *, api_key: str) -> None:
        if not api_key.strip():
            raise ValueError("Tavily API key must not be blank.")

        self._tool = TavilyExtract(
            tavily_api_key=api_key,
            extract_depth="advanced",
            format="text",
            chunks_per_source=3,
        )
        self._tool.handle_tool_error = False

    def extract(
        self,
        request: ResearchRequest,
        hits: list[SearchHit],
    ) -> list[Citation]:
        if not hits:
            return []

        # Deduplicate URLs while preserving search order.
        hits_by_url: dict[str, SearchHit] = {}

        for hit in hits:
            hits_by_url.setdefault(str(hit.url), hit)

        selected_urls = list(hits_by_url)[: request.max_sources]

        try:
            payload = self._tool.invoke(
                {
                    "urls": selected_urls,
                    "query": request.question,
                }
            )
        except ToolException:
            logger.warning("Tavily returned no extracted content.")
            return []

        if not isinstance(payload, dict):
            raise TypeError("Tavily Extract returned an unexpected response.")

        if payload.get("error"):
            raise RuntimeError("Tavily Extract request failed.")

        response = TavilyExtractResponse.model_validate(payload)

        if response.failed_results:
            logger.warning(
                "Extraction failed for %d URL(s).",
                len(response.failed_results),
            )

        # Index by URL because response order may differ from request order.
        content_by_url = {
            str(result.url): (result.raw_content or "").strip()
            for result in response.results
        }

        retrieved_at = datetime.now(UTC)
        citations: list[Citation] = []

        for url in selected_urls:
            content = content_by_url.get(url, "")

            if not content:
                continue

            hit = hits_by_url[url]
            digest = sha256(url.encode("utf-8")).hexdigest()[:16]

            citations.append(
                Citation(
                    citation_id=f"tavily-{digest}",
                    title=hit.title,
                    url=hit.url,
                    published_at=None,
                    retrieved_at=retrieved_at,
                    excerpt=content,
                )
            )

        return citations
