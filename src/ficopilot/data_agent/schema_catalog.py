from collections.abc import Collection

from sqlalchemy import Engine, inspect, text

from ficopilot.data_agent.sql_executor import (
    DEFAULT_ALLOWED_TABLES,
)


class PostgresSchemaCatalog:
    def __init__(
        self,
        *,
        engine: Engine,
        allowed_tables: Collection[str] = (DEFAULT_ALLOWED_TABLES),
    ) -> None:
        self._engine = engine
        self._allowed_tables = sorted(table.lower() for table in allowed_tables)

    def describe(self) -> str:
        inspector = inspect(self._engine)

        available_tables = set(inspector.get_table_names(schema="public"))

        missing_tables = set(self._allowed_tables) - available_tables

        if missing_tables:
            raise RuntimeError(
                f"Expected database tables are missing: {sorted(missing_tables)}"
            )

        sections: list[str] = []

        for table_name in self._allowed_tables:
            sections.append(
                self._describe_table(
                    inspector,
                    table_name,
                )
            )

        sections.append(self._describe_entities())
        sections.append(self._describe_metrics())

        sections.append(
            """
Business semantics:
- fiscal_quarter 0 represents an annual period.
- percent values are stored as percentage numbers:
  25 means 25%, not 0.25.
- currency_million values are stored in millions.
- Do not compare different currencies without
  exchange-rate data.
- source_document and source_page provide lineage.
            """.strip()
        )

        return "\n\n".join(sections)

    def _describe_table(
        self,
        inspector,
        table_name: str,
    ) -> str:
        columns = inspector.get_columns(
            table_name,
            schema="public",
        )

        primary_key = inspector.get_pk_constraint(
            table_name,
            schema="public",
        )

        primary_columns = set(primary_key.get("constrained_columns") or [])

        lines = [f"Table: {table_name}"]

        for column in columns:
            attributes = [str(column["type"])]

            if column["name"] in primary_columns:
                attributes.append("primary key")

            if not column.get("nullable", True):
                attributes.append("not null")

            lines.append(f"- {column['name']}: " + ", ".join(attributes))

        foreign_keys = inspector.get_foreign_keys(
            table_name,
            schema="public",
        )

        for foreign_key in foreign_keys:
            local_columns = ", ".join(foreign_key["constrained_columns"])
            remote_columns = ", ".join(foreign_key["referred_columns"])

            lines.append(
                f"- foreign key: {local_columns} -> "
                f"{foreign_key['referred_table']}."
                f"{remote_columns}"
            )

        return "\n".join(lines)

    def _describe_entities(self) -> str:
        with self._engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT
                        entity_code,
                        name,
                        entity_type
                    FROM entities
                    ORDER BY entity_code
                    """
                )
            ).mappings()

            values = [
                (f"- {row['entity_code']}: {row['name']} ({row['entity_type']})")
                for row in rows
            ]

        return "\n".join(["Available entities:", *values])

    def _describe_metrics(self) -> str:
        with self._engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT
                        metric_code,
                        display_name,
                        category,
                        unit_type,
                        description
                    FROM metric_definitions
                    ORDER BY metric_code
                    """
                )
            ).mappings()

            values = [
                (
                    f"- {row['metric_code']}: "
                    f"{row['display_name']}; "
                    f"category={row['category']}; "
                    f"unit={row['unit_type']}; "
                    f"{row['description']}"
                )
                for row in rows
            ]

        return "\n".join(["Available metric codes:", *values])
