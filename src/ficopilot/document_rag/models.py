from datetime import datetime

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from ficopilot.persistence import Base


class StoredDocument(Base):
    __tablename__ = "document_records"
    __table_args__ = (
        CheckConstraint(
            "page_count >= 1",
            name="ck_document_page_count",
        ),
        CheckConstraint(
            "chunk_count >= 0",
            name="ck_document_chunk_count",
        ),
        CheckConstraint(
            "media_type = 'application/pdf'",
            name="ck_document_media_type",
        ),
    )

    document_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(500),
    )
    media_type: Mapped[str] = mapped_column(
        String(64),
    )
    page_count: Mapped[int] = mapped_column(
        Integer,
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
    )
    warnings: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
