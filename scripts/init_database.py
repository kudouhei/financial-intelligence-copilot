from ficopilot.config import Settings
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.data_agent.models import Base


def main() -> None:
    settings = Settings()
    config = settings.require_database_config()
    engine = create_database_engine(config)

    Base.metadata.create_all(engine)

    table_names = sorted(Base.metadata.tables)

    print("Database schema initialized.")

    for table_name in table_names:
        print(f"- {table_name}")


if __name__ == "__main__":
    main()
