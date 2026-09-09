from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ficopilot.config import Settings
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.models import (
    Entity,
    FinancialFact,
    MetricDefinition,
    ReportingPeriod,
)

METRICS = [
    {
        "metric_code": "total_liquidity_ratio",
        "display_name": "Total liquidity ratio",
        "category": "liquidity",
        "unit_type": "percent",
        "description": (
            "Liquidity as a percentage of projected "
            "net cash flows over the next 12 months."
        ),
    },
    {
        "metric_code": "minimum_total_liquidity_ratio",
        "display_name": "Minimum total liquidity ratio",
        "category": "liquidity",
        "unit_type": "percent",
        "description": (
            "Minimum internal total liquidity ratio "
            "required by the liquidity risk policy."
        ),
    },
    {
        "metric_code": "liquidity_coverage_ratio",
        "display_name": "Liquidity coverage ratio",
        "category": "liquidity",
        "unit_type": "percent",
        "description": ("Liquidity Coverage Ratio reported by the EIB."),
    },
    {
        "metric_code": "net_stable_funding_ratio",
        "display_name": "Net stable funding ratio",
        "category": "funding",
        "unit_type": "percent",
        "description": ("Net Stable Funding Ratio reported by the EIB."),
    },
    {
        "metric_code": "outstanding_borrowings",
        "display_name": "Outstanding borrowings",
        "category": "funding",
        "unit_type": "currency_million",
        "description": ("Outstanding borrowings and commercial paper."),
    },
    {
        "metric_code": "treasury_assets",
        "display_name": "Treasury assets",
        "category": "liquidity",
        "unit_type": "currency_million",
        "description": "Total treasury assets.",
    },
]


FACTS = {
    2023: [
        (
            "liquidity_coverage_ratio",
            "423.7",
            None,
            8,
        ),
        (
            "net_stable_funding_ratio",
            "118.3",
            None,
            8,
        ),
        (
            "outstanding_borrowings",
            "434800",
            "EUR",
            8,
        ),
    ],
    2024: [
        (
            "total_liquidity_ratio",
            "60.3",
            None,
            31,
        ),
        (
            "minimum_total_liquidity_ratio",
            "25",
            None,
            90,
        ),
        (
            "liquidity_coverage_ratio",
            "724.9",
            None,
            8,
        ),
        (
            "net_stable_funding_ratio",
            "122.2",
            None,
            8,
        ),
        (
            "outstanding_borrowings",
            "442900",
            "EUR",
            8,
        ),
        (
            "treasury_assets",
            "67500",
            "EUR",
            8,
        ),
    ],
}


def upsert_metric(
    session: Session,
    data: dict[str, str],
) -> None:
    metric = session.get(
        MetricDefinition,
        data["metric_code"],
    )

    if metric is None:
        session.add(MetricDefinition(**data))
        return

    metric.display_name = data["display_name"]
    metric.category = data["category"]
    metric.unit_type = data["unit_type"]
    metric.description = data["description"]


def get_or_create_entity(session: Session) -> Entity:
    entity = session.scalar(select(Entity).where(Entity.entity_code == "EIB"))

    if entity is not None:
        return entity

    entity = Entity(
        entity_code="EIB",
        name="European Investment Bank",
        entity_type="supranational_bank",
        country="European Union",
        reporting_currency="EUR",
    )

    session.add(entity)
    session.flush()

    return entity


def get_or_create_period(
    session: Session,
    *,
    entity: Entity,
    fiscal_year: int,
) -> ReportingPeriod:
    period = session.scalar(
        select(ReportingPeriod).where(
            ReportingPeriod.entity_id == entity.id,
            ReportingPeriod.fiscal_year == fiscal_year,
            ReportingPeriod.period_type == "annual",
            ReportingPeriod.fiscal_quarter == 0,
        )
    )

    if period is not None:
        return period

    period = ReportingPeriod(
        entity_id=entity.id,
        fiscal_year=fiscal_year,
        period_type="annual",
        fiscal_quarter=0,
        period_end=date(fiscal_year, 12, 31),
        source_document="eib-financial-report-2024.pdf",
    )

    session.add(period)
    session.flush()

    return period


def upsert_fact(
    session: Session,
    *,
    period: ReportingPeriod,
    metric_code: str,
    value: str,
    currency: str | None,
    source_page: int,
) -> None:
    fact = session.scalar(
        select(FinancialFact).where(
            FinancialFact.period_id == period.id,
            FinancialFact.metric_code == metric_code,
        )
    )

    if fact is None:
        session.add(
            FinancialFact(
                period_id=period.id,
                metric_code=metric_code,
                metric_value=Decimal(value),
                currency=currency,
                source_page=source_page,
            )
        )
        return

    fact.metric_value = Decimal(value)
    fact.currency = currency
    fact.source_page = source_page


def main() -> None:
    settings = Settings()
    config = settings.require_database_config()
    engine = create_database_engine(config)

    with Session(engine) as session:
        with session.begin():
            for metric in METRICS:
                upsert_metric(session, metric)

            entity = get_or_create_entity(session)

            for fiscal_year, facts in FACTS.items():
                period = get_or_create_period(
                    session,
                    entity=entity,
                    fiscal_year=fiscal_year,
                )

                for (
                    metric_code,
                    value,
                    currency,
                    source_page,
                ) in facts:
                    upsert_fact(
                        session,
                        period=period,
                        metric_code=metric_code,
                        value=value,
                        currency=currency,
                        source_page=source_page,
                    )

        fact_count = session.scalar(select(func.count(FinancialFact.id)))

    print(f"financial_facts={fact_count}")


if __name__ == "__main__":
    main()
