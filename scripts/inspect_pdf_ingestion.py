from argparse import ArgumentParser
from pathlib import Path

from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)

# 终端命令
#    ↓
# 解析 pdf_path 和 --find
#    ↓
# 调用 PdfIngestionService
#    ↓
# 得到 DocumentIngestionResult
#    ├── document：文档信息
#    ├── chunks：文本块
#    └── warnings：非致命问题
#    ↓
# 有 --find？── Yes → 查找并展示匹配 chunk
#    │
#    No
#    ↓
# 展示前三个 chunk


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "pdf_path",
        type=Path,
    )
    parser.add_argument(
        "--find",
        help="Find chunks containing this text.",
    )
    args = parser.parse_args()

    result = PdfIngestionService().ingest(args.pdf_path)

    print(f"document_id={result.document.document_id}")
    print(f"filename={result.document.filename}")
    print(f"pages={result.document.page_count}")
    print(f"chunks={len(result.chunks)}")

    for warning in result.warnings:
        print(f"warning={warning}")

    if args.find:
        query = args.find.casefold()
        normalized_chunks = [
            (chunk, " ".join(chunk.content.split())) for chunk in result.chunks
        ]

        matches = [
            (chunk, content)
            for chunk, content in normalized_chunks
            if query in content.casefold()
        ]

        print(f"\nquery={args.find}")
        print(f"matches={len(matches)}")

        for chunk, content in matches[:5]:
            match_index = content.casefold().find(query)
            context_start = max(0, match_index - 150)
            context_end = min(
                len(content),
                match_index + len(query) + 350,
            )
            preview = content[context_start:context_end]

            print(
                f"\n{chunk.chunk_id} page={chunk.page_number} start={chunk.start_index}"
            )
            print(f"...{preview}...")
        return

    for chunk in result.chunks[:3]:
        print(f"\n{chunk.chunk_id} page={chunk.page_number} start={chunk.start_index}")
        print(chunk.content[:500])


if __name__ == "__main__":
    main()
