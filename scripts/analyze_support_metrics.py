#!/usr/bin/env python3
"""Summarize support bot analytics with SLA-style metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analytics import (
    compute_fallback_rate,
    compute_average_response_time_ms,
    compute_tenant_summaries,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print per-tenant support quality metrics")
    parser.add_argument(
        "--metrics-file",
        default="analytics/support_metrics.json",
        help="Path to the analytics JSON file"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics_path = Path(args.metrics_file)
    if not metrics_path.exists():
        raise SystemExit(f"Metrics file not found: {metrics_path}")

    with metrics_path.open() as f:
        metrics = json.load(f)

    overall_avg = compute_average_response_time_ms(metrics)
    overall_fallback = compute_fallback_rate(metrics)

    print("Overall Support Quality")
    print("------------------------")
    print(f"Total queries: {metrics.get('total_queries', 0)}")
    print(f"Fallback rate: {overall_fallback*100:.1f}%")
    print(f"Avg response time: {overall_avg:.1f} ms")
    print()

    tenant_summaries = compute_tenant_summaries(metrics)
    if not tenant_summaries:
        print("No tenant-specific data yet.")
        return

    print("Per-Tenant Metrics")
    print("-------------------")
    for tenant_id, stats in tenant_summaries.items():
        print(f"Tenant: {tenant_id}")
        print(f"  Queries: {stats['queries']}")
        print(f"  Fallback rate: {stats['fallback_rate']*100:.1f}%")
        print(f"  Avg response time: {stats['average_response_time_ms']:.1f} ms")
        print()

if __name__ == "__main__":
    main()
