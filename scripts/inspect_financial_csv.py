from pathlib import Path

from ficopilot.data_agent.csv_ingestion import (
    CsvFinancialFactReader,
)


def main() -> None:
    source_path = Path("data/financial_facts/eib_financial_facts.csv")

    records = CsvFinancialFactReader().read(source_path)

    print(f"source={source_path}")
    print(f"records={len(records)}")

    for record in records[:3]:
        print(record.model_dump())


if __name__ == "__main__":
    main()
