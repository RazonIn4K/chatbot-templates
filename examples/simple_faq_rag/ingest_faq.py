#!/usr/bin/env python3
"""Minimal ingestion script for the docs/faq support demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow importing project modules when script is run from the example folder
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ingest import ingest_documents, load_documents_from_directory  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest docs/faq into ChromaDB")
    parser.add_argument(
        "--docs-dir",
        default=str(PROJECT_ROOT / "docs" / "faq"),
        help="Folder containing Markdown FAQ entries"
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Optional override for the Chroma collection"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the target collection before ingesting"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = load_documents_from_directory(args.docs_dir)
    if not documents:
        raise SystemExit("No FAQ documents found. Add Markdown files to docs/faq.")

    ingest_documents(
        documents=documents,
        collection_name=args.collection or None,
        reset=args.reset
    )

    print("\n✓ FAQ documents ingested. The support bot can now answer questions!\n")


if __name__ == "__main__":
    main()
