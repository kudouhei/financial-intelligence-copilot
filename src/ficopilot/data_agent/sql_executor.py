from collections.abc import Collection

from sqlalchemy import Engine
from sqlalchemy.exc import DBAPIError
from sqlglot import exp, parse
from sqlglot.errors import ParseError
from sqlglot.optimizer.scope import build_scope

from ficopilot.contracts import SqlQueryResult

DEFAULT_ALLOWED_TABLES = frozenset(
    {
        "entities",
        "reporting_periods",
        "metric_definitions",
        "financial_facts",
    }
)

FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Merge,
    exp.Command,
)


class UnsafeSqlError(ValueError):
    pass


class SqlExecutionError(RuntimeError):
    pass


class SafeSqlExecutor:
    def __init__(
        self,
        *,
        engine: Engine,
        allowed_tables: Collection[str] = (DEFAULT_ALLOWED_TABLES),
        max_rows: int = 100,
    ) -> None:
        if max_rows <= 0:
            raise ValueError("max_rows must be positive.")

        self._engine = engine
        self._allowed_tables = {table.lower() for table in allowed_tables}
        self._max_rows = max_rows

    def validate_sql(self, sql: str) -> str:
        clean_sql = sql.strip()

        if not clean_sql:
            raise UnsafeSqlError("SQL must not be blank.")

        try:
            statements = [
                statement
                for statement in parse(
                    clean_sql,
                    read="postgres",
                )
                if statement is not None
            ]
        except ParseError as error:
            raise UnsafeSqlError(f"Invalid PostgreSQL SQL: {error}") from error

        if len(statements) != 1:
            raise UnsafeSqlError("Exactly one SQL statement is allowed.")

        statement = statements[0]

        if not isinstance(statement, exp.Query):
            raise UnsafeSqlError("Only read-only query statements are allowed.")

        for expression_type in FORBIDDEN_EXPRESSIONS:
            if statement.find(expression_type) is not None:
                raise UnsafeSqlError("SQL contains a forbidden operation.")

        root_scope = build_scope(statement)

        if root_scope is None:
            raise UnsafeSqlError("Unable to analyse SQL scope.")

        referenced_tables: set[str] = set()

        for scope in root_scope.traverse():
            for _, source in scope.selected_sources.values():
                if not isinstance(source, exp.Table):
                    continue

                schema_name = source.db.lower() if source.db else "public"

                if schema_name != "public":
                    raise UnsafeSqlError("Only the public schema is allowed.")

                referenced_tables.add(source.name.lower())

        forbidden_tables = referenced_tables - self._allowed_tables

        if forbidden_tables:
            raise UnsafeSqlError(
                f"SQL references forbidden tables: {sorted(forbidden_tables)}"
            )

        return statement.sql(dialect="postgres")

    def execute(self, sql: str) -> SqlQueryResult:
        validated_sql = self.validate_sql(sql)

        limited_sql = (
            "SELECT * FROM ("
            f"{validated_sql}"
            ") AS generated_query "
            f"LIMIT {self._max_rows + 1}"
        )

        try:
            with self._engine.connect() as connection, connection.begin():
                connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                connection.exec_driver_sql("SET LOCAL statement_timeout = '5s'")

                result = connection.exec_driver_sql(limited_sql)

                rows = [dict(row._mapping) for row in result]
                columns = list(result.keys())

        except DBAPIError as error:
            database_message = str(error.orig)[:1000]

            raise SqlExecutionError(
                f"PostgreSQL rejected the generated query: {database_message}"
            ) from error

        truncated = len(rows) > self._max_rows
        visible_rows = rows[: self._max_rows]

        return SqlQueryResult(
            sql=validated_sql,
            columns=columns,
            rows=visible_rows,
            row_count=len(visible_rows),
            truncated=truncated,
        )
