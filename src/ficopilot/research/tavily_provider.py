from datetime import UTC, datetime
from hashlib import sha256
from json import JSONDecodeError, loads
from typing import Annotated, Any, Literal

from langchain_core.tools import ToolException
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


def _coerce_tavily_payload(raw_response: Any) -> dict[str, Any]:
    content = getattr(raw_response, "content", raw_response)

    if isinstance(content, dict):
        return content

    if isinstance(content, str):
        try:
            parsed = loads(content)
        except JSONDecodeError as error:
            raise TypeError("Tavily returned an unexpected response.") from error

        if isinstance(parsed, dict):
            return parsed

    raise TypeError("Tavily returned an unexpected response.")


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
        tool.handle_tool_error = False

        try:
            raw_response = tool.invoke(
                {
                    "query": request.question,
                    "end_date": request.as_of.date().isoformat(),
                }
            )
        except ToolException:
            return []

        payload = _coerce_tavily_payload(raw_response)

        if error := payload.get("error"):
            raise RuntimeError(f"Tavily search failed: {error}")

        response = TavilyResponse.model_validate(payload)
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
