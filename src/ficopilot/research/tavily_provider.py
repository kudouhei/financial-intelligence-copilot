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

from ficopilot.contracts import ResearchRequest, SearchHit

NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class TavilyResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: NonBlankText
    url: HttpUrl
    content: NonBlankText
    score: float | None = Field(default=None, ge=0, le=1)


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
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: Literal["general", "news", "finance"] = "finance",
    ) -> None:
        if not api_key.strip():
            raise ValueError("Tavily API key must not be blank.")

        self._api_key = api_key
        self._search_depth = search_depth
        self._topic = topic

    def search(
        self,
        request: ResearchRequest,
    ) -> list[SearchHit]:
        tool = TavilySearch(
            tavily_api_key=self._api_key,
            max_results=request.max_sources,
            topic=self._topic,
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

        return [
            SearchHit(
                title=result.title,
                url=result.url,
                snippet=result.content,
                score=result.score,
            )
            for result in response.results
        ]
