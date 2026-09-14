from collections.abc import Sequence

from sqlalchemy import Engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ficopilot.contracts import (
    FinancialFactInput,
    FinancialFactLoadResult,
)
from ficopilot.data_agent.models import (
    Entity,
    FinancialFact,
    MetricDefinition,
    ReportingPeriod,
)


class ReferenceDataError(ValueError):
    """Raised when required entity or metric metadata is missing."""


class FinancialFactLoader:
    def __init__(
        self,
        *,
        engine: Engine,
    ) -> None:
        self._engine = engine

    def load(
        self,
        records: Sequence[FinancialFactInput],
        *,
        source_name: str,
    ) -> FinancialFactLoadResult:
        if not records:
            return FinancialFactLoadResult(
                source_name=source_name,
                rows_read=0,
                periods_created=0,
                facts_upserted=0,
            )

        with Session(self._engine) as session, session.begin():
            entities = self._load_entities(
                session,
                records,
            )
            metrics = self._load_metrics(
                session,
                records,
            )

            self._validate_units(
                records,
                metrics,
            )

            periods, periods_created = self._resolve_periods(
                session,
                records,
                entities,
            )

            fact_rows = [
                {
                    "period_id": periods[
                        (
                            record.entity_code,
                            record.fiscal_year,
                            record.period_type,
                            record.fiscal_quarter,
                        )
                    ].id,
                    "metric_code": record.metric_code,
                    "metric_value": record.metric_value,
                    "currency": record.currency,
                    "source_page": record.source_page,
                }
                for record in records
            ]

            insert_statement = insert(FinancialFact).values(fact_rows)

            upsert_statement = insert_statement.on_conflict_do_update(
                constraint="uq_financial_fact",
                set_={
                    "metric_value": (insert_statement.excluded.metric_value),
                    "currency": (insert_statement.excluded.currency),
                    "source_page": (insert_statement.excluded.source_page),
                },
            )

            session.execute(upsert_statement)

        return FinancialFactLoadResult(
            source_name=source_name,
            rows_read=len(records),
            periods_created=periods_created,
            facts_upserted=len(records),
        )

    def _load_entities(
        self,
        session: Session,
        records: Sequence[FinancialFactInput],
    ) -> dict[str, Entity]:
        requested_codes = {record.entity_code for record in records}

        entities = session.scalars(
            select(Entity).where(Entity.entity_code.in_(requested_codes))
        ).all()

        entities_by_code = {entity.entity_code: entity for entity in entities}

        missing_codes = requested_codes - set(entities_by_code)

        if missing_codes:
            raise ReferenceDataError(f"Unknown entity codes: {sorted(missing_codes)}")

        return entities_by_code

    def _load_metrics(
        self,
        session: Session,
        records: Sequence[FinancialFactInput],
    ) -> dict[str, MetricDefinition]:
        requested_codes = {record.metric_code for record in records}

        metrics = session.scalars(
            select(MetricDefinition).where(
                MetricDefinition.metric_code.in_(requested_codes)
            )
        ).all()

        metrics_by_code = {metric.metric_code: metric for metric in metrics}

        missing_codes = requested_codes - set(metrics_by_code)

        if missing_codes:
            raise ReferenceDataError(f"Unknown metric codes: {sorted(missing_codes)}")

        return metrics_by_code

    def _validate_units(
        self,
        records: Sequence[FinancialFactInput],
        metrics: dict[str, MetricDefinition],
    ) -> None:
        for record in records:
            metric = metrics[record.metric_code]

            if metric.unit_type == "percent" and record.currency is not None:
                raise ReferenceDataError(
                    f"{record.metric_code} is a percentage "
                    "and must not specify currency."
                )

            if metric.unit_type == "currency_million" and record.currency is None:
                raise ReferenceDataError(f"{record.metric_code} requires currency.")

    def _resolve_periods(
        self,
        session: Session,
        records: Sequence[FinancialFactInput],
        entities: dict[str, Entity],
    ) -> tuple[
        dict[tuple[str, int, str, int], ReportingPeriod],
        int,
    ]:
        periods: dict[
            tuple[str, int, str, int],
            ReportingPeriod,
        ] = {}

        periods_created = 0

        for record in records:
            key = (
                record.entity_code,
                record.fiscal_year,
                record.period_type,
                record.fiscal_quarter,
            )

            if key in periods:
                continue

            entity = entities[record.entity_code]

            period = session.scalar(
                select(ReportingPeriod).where(
                    ReportingPeriod.entity_id == entity.id,
                    ReportingPeriod.fiscal_year == record.fiscal_year,
                    ReportingPeriod.period_type == record.period_type,
                    ReportingPeriod.fiscal_quarter == record.fiscal_quarter,
                )
            )

            if period is None:
                period = ReportingPeriod(
                    entity_id=entity.id,
                    fiscal_year=record.fiscal_year,
                    period_type=record.period_type,
                    fiscal_quarter=record.fiscal_quarter,
                    period_end=record.period_end,
                    source_document=record.source_document,
                )

                session.add(period)
                session.flush()
                periods_created += 1
            else:
                period.period_end = record.period_end
                period.source_document = record.source_document

            periods[key] = period

        return periods, periods_created
