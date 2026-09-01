from langchain_tavily import TavilyExtract

from ficopilot.config import Settings

REPORT_URL = "https://www.microsoft.com/investor/reports/ar25/index.html"


def main() -> None:
    settings = Settings()

    extractor = TavilyExtract(
        tavily_api_key=settings.require_tavily_api_key(),
        extract_depth="advanced",
        format="text",
        query=(
            "Microsoft financial risks, risk factors, foreign exchange, "
            "interest rate, credit risk, cybersecurity and competition"
        ),
        chunks_per_source=3,
    )

    response = extractor.invoke({"urls": [REPORT_URL]})

    if not isinstance(response, dict):
        raise TypeError("Tavily Extract returned an unexpected response")

    if error := response.get("error"):
        raise RuntimeError(f"Tavily Extract failed: {error}")

    results = response.get("results", [])
    failed_results = response.get("failed_results", [])

    print(f"results={len(results)}")
    print(f"failed_results={len(failed_results)}")

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"url={result.get('url')}")

        content = result.get("raw_content", "")
        print(content[:5_000])


if __name__ == "__main__":
    main()
