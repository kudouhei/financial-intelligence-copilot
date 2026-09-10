from ficopilot.config import Settings
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.sql_executor import (
    SafeSqlExecutor,
    UnsafeSqlError,
)

SAFE_QUERY = """
SELECT
    p.fiscal_year,
    f.metric_value AS lcr_percent
FROM financial_facts AS f
JOIN reporting_periods AS p
    ON p.id = f.period_id
JOIN entities AS e
    ON e.id = p.entity_id
WHERE e.entity_code = 'EIB'
  AND f.metric_code = 'liquidity_coverage_ratio'
ORDER BY p.fiscal_year
"""


def main() -> None:
    settings = Settings()
    config = settings.require_data_agent_database_config()

    engine = create_database_engine(config)

    executor = SafeSqlExecutor(
        engine=engine,
        max_rows=20,
    )

    result = executor.execute(SAFE_QUERY)

    print(f"sql={result.sql}")
    print(f"columns={result.columns}")
    print(f"rows={result.rows}")
    print(f"truncated={result.truncated}")

    try:
        executor.execute("DELETE FROM financial_facts")
    except UnsafeSqlError as error:
        print(f"blocked={error}")


if __name__ == "__main__":
    main()
