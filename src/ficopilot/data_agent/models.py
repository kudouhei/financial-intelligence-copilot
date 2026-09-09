from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    entity_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200))
    entity_type: Mapped[str] = mapped_column(
        String(32),
    )
    country: Mapped[str] = mapped_column(String(100))
    reporting_currency: Mapped[str] = mapped_column(
        String(3),
    )

    periods: Mapped[list[ReportingPeriod]] = relationship(
        back_populates="entity",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ReportingPeriod(Base):
    __tablename__ = "reporting_periods"
    __table_args__ = (
        UniqueConstraint(
            "entity_id",
            "fiscal_year",
            "period_type",
            "fiscal_quarter",
            name="uq_reporting_period",
        ),
        CheckConstraint(
            "period_type IN ('annual', 'quarterly')",
            name="ck_period_type",
        ),
        CheckConstraint(
            "fiscal_quarter BETWEEN 0 AND 4",
            name="ck_fiscal_quarter",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    entity_id: Mapped[int] = mapped_column(
        ForeignKey(
            "entities.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    fiscal_year: Mapped[int] = mapped_column(Integer)
    period_type: Mapped[str] = mapped_column(
        String(16),
    )
    fiscal_quarter: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    period_end: Mapped[date] = mapped_column(Date)
    source_document: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    entity: Mapped[Entity] = relationship(
        back_populates="periods",
    )
    facts: Mapped[list[FinancialFact]] = relationship(
        back_populates="period",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MetricDefinition(Base):
    __tablename__ = "metric_definitions"

    metric_code: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(150),
    )
    category: Mapped[str] = mapped_column(String(50))
    unit_type: Mapped[str] = mapped_column(
        String(30),
    )
    description: Mapped[str] = mapped_column(
        String(500),
    )

    facts: Mapped[list[FinancialFact]] = relationship(
        back_populates="metric",
    )


class FinancialFact(Base):
    __tablename__ = "financial_facts"
    __table_args__ = (
        UniqueConstraint(
            "period_id",
            "metric_code",
            name="uq_financial_fact",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    period_id: Mapped[int] = mapped_column(
        ForeignKey(
            "reporting_periods.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    metric_code: Mapped[str] = mapped_column(
        ForeignKey("metric_definitions.metric_code"),
        index=True,
    )
    metric_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 4),
    )
    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
    )
    source_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    period: Mapped[ReportingPeriod] = relationship(
        back_populates="facts",
    )
    metric: Mapped[MetricDefinition] = relationship(
        back_populates="facts",
    )
