from datetime import UTC, datetime
from hashlib import sha256
from typing import Annotated, Literal

from langchain_tavily import TavilySearch
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
)

from ficopilot.contracts import Citation, ResearchRequest

NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class TavilyResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: NonBlankText
    url: HttpUrl
    content: NonBlankText


class TavilyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    results: list[TavilyResult] = Field(default_factory=list)


class TavilySearchProvider:
    def __init__(
        self,
        *,
        api_key: str,
        search_depth: Literal[
            "basic",
            "advanced",
        ] = "basic",
    ) -> None:
        if not api_key.strip():
            raise ValueError("Tavily API key must not be blank.")

        self._api_key = api_key
        self._search_depth = search_depth

    def search(
        self,
        request: ResearchRequest,
    ) -> list[Citation]:
        tool = TavilySearch(
            tavily_api_key=self._api_key,
            max_results=request.max_sources,
            topic="finance",
            search_depth=self._search_depth,
            include_answer=False,
            include_raw_content=False,
            include_images=False,
        )

        raw_response = tool.invoke(
            {
                "query": request.question,
                "end_date": request.as_of.date().isoformat(),
            }
        )

        if not isinstance(raw_response, dict):
            raise TypeError("Tavily returned an unexpected response.")

        if error := raw_response.get("error"):
            raise RuntimeError(f"Tavily search failed: {error}")

        response = TavilyResponse.model_validate(raw_response)
        retrieved_at = datetime.now(UTC)

        return [
            Citation(
                citation_id=self._citation_id(result.url),
                title=result.title,
                url=result.url,
                published_at=None,
                retrieved_at=retrieved_at,
                excerpt=result.content,
            )
            for result in response.results
        ]

    @staticmethod
    def _citation_id(url: HttpUrl) -> str:
        digest = sha256(str(url).encode("utf-8")).hexdigest()[:16]

        return f"tavily-{digest}"
