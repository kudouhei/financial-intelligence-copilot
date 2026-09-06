from uuid import uuid4

from langsmith import Client

from ficopilot.api.live import create_live_service
from ficopilot.contracts import ResearchRequest

DATASET_NAME = "ficopilot-financial-research-v1"


def claims_behavior(
    outputs: dict,
    reference_outputs: dict,
) -> bool:
    has_claims = bool(outputs["claims"])
    return has_claims == reference_outputs["expect_claims"]


def required_answer_terms(
    outputs: dict,
    reference_outputs: dict,
) -> bool:
    answer = outputs["answer"].lower()

    return all(
        term.lower() in answer for term in reference_outputs["required_answer_terms"]
    )


def expected_source(
    outputs: dict,
    reference_outputs: dict,
) -> bool:
    expected_url = reference_outputs["expected_source_url"]
    actual_urls = {citation["url"] for citation in outputs["citations"]}

    if expected_url is None:
        return not actual_urls

    return expected_url in actual_urls


def scope_and_stop_behavior(
    outputs: dict,
    reference_outputs: dict,
) -> bool:
    process = outputs.get("process")

    if process is None:
        return False

    scope = process.get("scope")

    if scope is None:
        return False

    expected_year = reference_outputs["expected_report_year"]

    year_matches = (
        scope["report_years"] == []
        if expected_year is None
        else expected_year in scope["report_years"]
    )

    latest_matches = (
        scope["latest_requested"] == reference_outputs["expected_latest_requested"]
    )

    expected_warning = reference_outputs["expected_warning_substring"]
    warnings_text = " ".join(outputs["warnings"])

    warning_matches = (
        True if expected_warning is None else expected_warning in warnings_text
    )

    return year_matches and latest_matches and warning_matches


def main() -> None:
    client = Client()
    service = create_live_service()

    def target(inputs: dict) -> dict:
        request = ResearchRequest.model_validate(inputs)
        result = service.run(
            request,
            trace_id=f"eval-{uuid4()}",
        )

        return result.model_dump(mode="json")

    results = client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[
            claims_behavior,
            required_answer_terms,
            expected_source,
            scope_and_stop_behavior,
        ],
        experiment_prefix="financial-research-v1",
        max_concurrency=1,
        metadata={
            "workflow": "financial_research",
            "evaluation_version": "v1",
        },
    )

    print(results)


if __name__ == "__main__":
    main()
