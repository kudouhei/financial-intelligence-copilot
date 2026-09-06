from langsmith import Client

DATASET_NAME = "ficopilot-financial-research-v1"

MICROSOFT_ANNUAL_REPORT_URL = (
    "https://www.microsoft.com/investor/reports/ar25/index.html"
)


def main() -> None:
    client = Client()

    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset already exists: {DATASET_NAME}")
        return

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Minimal regression dataset for the FICopilot financial research workflow."
        ),
    )

    examples = [
        {
            "inputs": {
                "question": (
                    "What market-related financial risks does "
                    "Microsoft disclose in its 2025 Annual Report?"
                ),
                "as_of": "2026-09-01T12:00:00Z",
                "max_sources": 5,
            },
            "outputs": {
                "expect_claims": True,
                "required_answer_terms": [
                    "foreign exchange",
                    "interest rate",
                    "credit",
                    "equity",
                ],
                "expected_source_url": (MICROSOFT_ANNUAL_REPORT_URL),
                "expected_report_year": 2025,
                "expected_latest_requested": False,
                "expected_warning_substring": None,
            },
            "metadata": {
                "case": "risk_categories",
                "split": "baseline",
            },
        },
        {
            "inputs": {
                "question": (
                    "What hypothetical earnings impact does "
                    "Microsoft's 2025 Annual Report report for "
                    "a 10% decrease in foreign exchange rates "
                    "on revenue-related exposure?"
                ),
                "as_of": "2026-09-01T12:00:00Z",
                "max_sources": 5,
            },
            "outputs": {
                "expect_claims": True,
                "required_answer_terms": [
                    "11,596",
                    "earnings",
                    "10%",
                    "hypothetical",
                ],
                "expected_source_url": (MICROSOFT_ANNUAL_REPORT_URL),
                "expected_report_year": 2025,
                "expected_latest_requested": False,
                "expected_warning_substring": None,
            },
            "metadata": {
                "case": "financial_table_semantics",
                "split": "baseline",
            },
        },
        {
            "inputs": {
                "question": (
                    "What market-related financial risks does "
                    "Microsoft disclose in its latest annual report?"
                ),
                "as_of": "2026-09-01T12:00:00Z",
                "max_sources": 5,
            },
            "outputs": {
                "expect_claims": False,
                "required_answer_terms": [],
                "expected_source_url": None,
                "expected_report_year": None,
                "expected_latest_requested": True,
                "expected_warning_substring": (
                    "Latest-report resolution is not implemented"
                ),
            },
            "metadata": {
                "case": "controlled_latest_stop",
                "split": "baseline",
            },
        },
    ]

    client.create_examples(
        dataset_id=dataset.id,
        examples=examples,
    )

    print(f"Created dataset: {dataset.name}")
    print(f"Examples: {len(examples)}")


if __name__ == "__main__":
    main()
