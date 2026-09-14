from argparse import ArgumentParser
from pathlib import Path

from ficopilot.config import Settings
from ficopilot.data_agent.csv_ingestion import (
    CsvFinancialFactReader,
)
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.financial_fact_loader import (
    FinancialFactLoader,
)


def main() -> None:
    parser = ArgumentParser(description="Import financial facts from CSV.")
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the financial facts CSV.",
    )

    arguments = parser.parse_args()
    source_path: Path = arguments.source

    records = CsvFinancialFactReader().read(source_path)

    settings = Settings()
    database_config = settings.require_database_config()

    engine = create_database_engine(database_config)

    result = FinancialFactLoader(
        engine=engine,
    ).load(
        records,
        source_name=str(source_path),
    )

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
