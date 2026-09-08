from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from io import BytesIO
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from pypdf import PdfReader

from ficopilot.contracts import (
    DocumentChunk,
    DocumentIngestionResult,
    DocumentRecord,
)


@dataclass(frozen=True, slots=True)
class DocumentIdentity:
    filename: str
    sha256: str
    document_id: str


# 读取 PDF
# → 计算 SHA-256
# → 提取每一页文本
# → 保存页码 metadata
# → 切成 chunks
# → 生成 DocumentIngestionResult
class PdfIngestionService:
    def __init__(
        self,
        *,
        chunk_size: int = 1_000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must not be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )

    def ingest(
        self,
        path: Path,
    ) -> DocumentIngestionResult:
        if not path.is_file():
            raise FileNotFoundError(path)

        return self.ingest_bytes(
            filename=path.name,
            file_bytes=path.read_bytes(),
        )

    def ingest_bytes(
        self,
        *,
        filename: str,
        file_bytes: bytes,
    ) -> DocumentIngestionResult:

        identity = self.identify(
            filename=filename,
            file_bytes=file_bytes,
        )

        safe_filename = identity.filename
        file_hash = identity.sha256
        document_id = identity.document_id

        reader = PdfReader(BytesIO(file_bytes))

        pages: list[Document] = []
        empty_page_count = 0

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            content = (page.extract_text() or "").strip()

            if not content:
                empty_page_count += 1
                continue

            pages.append(
                Document(
                    page_content=content,
                    metadata={
                        "document_id": document_id,
                        "page_number": page_number,
                    },
                )
            )

        splits = self._splitter.split_documents(pages)
        chunks: list[DocumentChunk] = []

        for split in splits:
            page_number = int(split.metadata["page_number"])
            start_index = int(split.metadata.get("start_index", 0))

            chunk_key = (
                f"{document_id}:{page_number}:{start_index}:{split.page_content}"
            )
            chunk_hash = sha256(chunk_key.encode("utf-8")).hexdigest()[:16]

            chunks.append(
                DocumentChunk(
                    chunk_id=f"chunk-{chunk_hash}",
                    document_id=document_id,
                    page_number=page_number,
                    start_index=start_index,
                    content=split.page_content,
                )
            )

        warnings: list[str] = []

        if empty_page_count:
            warnings.append(
                f"{empty_page_count} page(s) contained no extractable text."
            )

        if not chunks:
            warnings.append(
                "No text chunks were created. "
                "The PDF may be scanned or image-based "
                "and require OCR."
            )

        document = DocumentRecord(
            document_id=document_id,
            filename=safe_filename,
            media_type="application/pdf",
            sha256=file_hash,
            page_count=len(reader.pages),
            ingested_at=datetime.now(UTC),
        )

        return DocumentIngestionResult(
            document=document,
            chunks=chunks,
            warnings=warnings,
        )

    @staticmethod
    def identify(
        *,
        filename: str,
        file_bytes: bytes,
    ) -> DocumentIdentity:
        safe_filename = Path(filename).name

        if Path(safe_filename).suffix.lower() != ".pdf":
            raise ValueError("Only PDF documents are supported.")

        if not file_bytes:
            raise ValueError("The uploaded PDF is empty.")

        file_hash = sha256(file_bytes).hexdigest()

        return DocumentIdentity(
            filename=safe_filename,
            sha256=file_hash,
            document_id=f"doc-{file_hash[:16]}",
        )
