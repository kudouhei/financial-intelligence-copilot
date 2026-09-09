from sqlalchemy import Engine, create_engine, text

from ficopilot.config import DatabaseConfig


def create_database_engine(
    config: DatabaseConfig,
) -> Engine:
    return create_engine(
        config.url,
        pool_pre_ping=True,
    )


def check_database_connection(
    engine: Engine,
) -> tuple[str, str]:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT
                    current_database(),
                    current_user
                """
            )
        ).one()

    return str(row[0]), str(row[1])
