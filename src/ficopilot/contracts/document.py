from typing import Annotated, Literal, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

NonBlankText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


# 整份文件的身份和元数据
class DocumentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: NonBlankText
    filename: NonBlankText
    media_type: Literal["application/pdf"]
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    page_count: int = Field(ge=1)
    ingested_at: AwareDatetime


# 未来向量检索的最小单位
class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: NonBlankText
    document_id: NonBlankText
    page_number: int = Field(ge=1)
    start_index: int = Field(ge=0)
    content: NonBlankText


# 一次摄取操作的完整结果
class DocumentIngestionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: DocumentRecord
    chunks: list[DocumentChunk]
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_chunks(self) -> Self:
        chunk_ids = [chunk.chunk_id for chunk in self.chunks]

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("Chunk IDs must be unique.")

        for chunk in self.chunks:
            if chunk.document_id != self.document.document_id:
                raise ValueError("Every chunk must belong to the ingested document.")

            if chunk.page_number > self.document.page_count:
                raise ValueError("Chunk page number exceeds document page count.")

        return self
