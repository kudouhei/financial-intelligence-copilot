from argparse import ArgumentParser
from pathlib import Path

from ficopilot.document_rag.ingestion import (
    PdfIngestionService,
)


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
        matches = [
            chunk for chunk in result.chunks if query in chunk.content.casefold()
        ]

        print(f"\nquery={args.find}")
        print(f"matches={len(matches)}")

        for chunk in matches[:5]:
            preview = " ".join(chunk.content.split())
            print(
                f"\n{chunk.chunk_id} page={chunk.page_number} start={chunk.start_index}"
            )
            print(preview[:500])
        return

    for chunk in result.chunks[:3]:
        print(f"\n{chunk.chunk_id} page={chunk.page_number} start={chunk.start_index}")
        print(chunk.content[:500])


if __name__ == "__main__":
    main()
