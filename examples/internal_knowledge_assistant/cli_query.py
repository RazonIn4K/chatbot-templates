#!/usr/bin/env python3
"""CLI for querying the internal knowledge assistant."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from llm_client import get_llm_client  # noqa: E402
from retriever import retrieve_relevant_context  # noqa: E402

DEFAULT_COLLECTION = "internal_handbook"
SYSTEM_PROMPT = "You are InternalAssistant, a concise helper for employee handbook questions."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask questions against the internal knowledge base")
    parser.add_argument("message", help="Question to ask")
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="Chroma collection name (default: internal_handbook)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of documents to retrieve"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = retrieve_relevant_context(
        query=args.message,
        top_k=args.top_k,
        collection_name=args.collection
    )

    llm = get_llm_client()
    response = llm.generate(
        system_prompt=SYSTEM_PROMPT,
        user_message=args.message,
        context=context
    )

    print("\nAnswer:\n-------")
    print(response)
    print("\nContext (truncated):\n--------------------")
    print(context[:750])


if __name__ == "__main__":
    main()
