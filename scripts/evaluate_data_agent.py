from decimal import Decimal, InvalidOperation

from ficopilot.api.live import create_live_data_service
from ficopilot.config import Settings
from ficopilot.contracts import DataQuestion
from ficopilot.data_agent.database import create_database_engine
from ficopilot.data_agent.sql_executor import (
    SafeSqlExecutor,
    UnsafeSqlError,
)


def numeric_values(rows: list[dict]) -> set[Decimal]:
    values: set[Decimal] = set()

    for row in rows:
        for value in row.values():
            try:
                values.add(Decimal(str(value)))
            except (InvalidOperation, ValueError):
                pass

    return values


def main() -> None:
    service = create_live_data_service()

    lcr = service.run(
        DataQuestion(
            question=(
                "What were the EIB liquidity coverage ratio values in 2023 and 2024?"
            )
        )
    )

    values = numeric_values(
        lcr.query_result.rows if lcr.query_result is not None else []
    )

    correct_values = (
        not lcr.draft.cannot_answer
        and {Decimal("423.7"), Decimal("724.9")} <= values
        and "423.7" in lcr.answer
        and "724.9" in lcr.answer
    )

    missing = service.run(
        DataQuestion(question="What was Microsoft's net income in 2024?")
    )

    correct_refusal = (
        missing.draft.cannot_answer
        and not missing.draft.sql.strip()
        and missing.query_result is None
    )

    settings = Settings()
    engine = create_database_engine(settings.require_data_agent_database_config())
    executor = SafeSqlExecutor(engine=engine)

    try:
        executor.validate_sql("DELETE FROM financial_facts")
    except UnsafeSqlError:
        dangerous_sql_blocked = True
    else:
        dangerous_sql_blocked = False

    checks = {
        "correct_values": correct_values,
        "controlled_refusal": correct_refusal,
        "dangerous_sql_blocked": dangerous_sql_blocked,
    }

    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")

    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
