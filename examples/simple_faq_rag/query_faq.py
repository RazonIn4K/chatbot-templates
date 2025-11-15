#!/usr/bin/env python3
"""Run a single FAQ query from the command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from support_bot import run_support_bot_flow  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the support FAQ knowledge base")
    parser.add_argument("message", help="Question for the support bot")
    parser.add_argument(
        "--user-id",
        default="demo-user",
        help="User identifier for logging purposes"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_support_bot_flow(user_id=args.user_id, message=args.message)

    print("\nSupportBot Response\n--------------------")
    print(result["answer"])

    if result.get("sources"):
        print("\nSources:")
        for source in result["sources"]:
            print(f" - {source}")

    if result["fallback_used"]:
        print("\n(Fallback message used — consider adding this FAQ to docs/faq)")


if __name__ == "__main__":
    main()
