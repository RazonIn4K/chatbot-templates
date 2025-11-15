#!/usr/bin/env python3
"""Ingest internal handbook docs into a dedicated Chroma collection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ingest import ingest_documents, load_documents_from_directory  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest docs/internal/ into Chroma")
    parser.add_argument(
        "--docs-dir",
        default=str(PROJECT_ROOT / "docs" / "internal"),
        help="Folder with internal Markdown docs"
    )
    parser.add_argument(
        "--collection",
        default="internal_handbook",
        help="Chroma collection name for internal knowledge"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the collection before ingesting"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = load_documents_from_directory(args.docs_dir)
    if not documents:
        raise SystemExit("No internal docs found. Add Markdown files to docs/internal/ or pass --docs-dir.")

    ingest_documents(
        documents=documents,
        collection_name=args.collection,
        reset=args.reset
    )

    print(f"\n✓ Ingested internal docs into collection '{args.collection}'.\n")
if __name__ == "__main__":
    main()
