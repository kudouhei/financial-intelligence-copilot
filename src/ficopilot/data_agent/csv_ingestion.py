from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from ficopilot.contracts import FinancialFactInput


class CsvValidationError(ValueError):
    pass


class CsvFinancialFactReader:
    def read(
        self,
        source_path: Path,
    ) -> list[FinancialFactInput]:
        frame = pd.read_csv(
            source_path,
            dtype=str,
            keep_default_na=False,
        )

        required_columns = set(FinancialFactInput.model_fields)
        actual_columns = set(frame.columns)

        missing_columns = required_columns - actual_columns
        unexpected_columns = actual_columns - required_columns

        if missing_columns:
            raise CsvValidationError(f"Missing CSV columns: {sorted(missing_columns)}")

        if unexpected_columns:
            raise CsvValidationError(
                f"Unexpected CSV columns: {sorted(unexpected_columns)}"
            )

        records: list[FinancialFactInput] = []
        errors: list[str] = []

        for row_number, row in enumerate(
            frame.to_dict(orient="records"),
            start=2,
        ):
            try:
                records.append(FinancialFactInput.model_validate(row))
            except ValidationError as error:
                errors.append(f"CSV row {row_number}: {error}")

        if errors:
            raise CsvValidationError("\n".join(errors))

        self._validate_unique_business_keys(records)

        return records

    def _validate_unique_business_keys(
        self,
        records: list[FinancialFactInput],
    ) -> None:
        seen: set[tuple[str, int, str, int, str]] = set()

        for record in records:
            key = (
                record.entity_code,
                record.fiscal_year,
                record.period_type,
                record.fiscal_quarter,
                record.metric_code,
            )

            if key in seen:
                raise CsvValidationError(f"Duplicate financial fact in CSV: {key}")

            seen.add(key)
