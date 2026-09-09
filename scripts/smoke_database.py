from ficopilot.config import Settings
from ficopilot.data_agent.database import (
    check_database_connection,
    create_database_engine,
)


def main() -> None:
    settings = Settings()
    config = settings.require_database_config()

    engine = create_database_engine(config)

    database, user = check_database_connection(engine)

    print(f"database={database}")
    print(f"user={user}")


if __name__ == "__main__":
    main()
