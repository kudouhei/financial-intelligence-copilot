from ficopilot.config import Settings
from ficopilot.data_agent import models as financial_models
from ficopilot.data_agent.database import (
    create_database_engine,
)
from ficopilot.document_rag import models as document_models
from ficopilot.persistence import Base

REGISTERED_MODEL_MODULES = (
    financial_models,
    document_models,
)


def main() -> None:
    settings = Settings()
    config = settings.require_database_config()
    engine = create_database_engine(config)

    Base.metadata.create_all(engine)

    if not REGISTERED_MODEL_MODULES:
        raise RuntimeError("No database models were registered.")

    table_names = sorted(Base.metadata.tables)

    print("Database schema initialized.")

    for table_name in table_names:
        print(f"- {table_name}")


if __name__ == "__main__":
    main()
