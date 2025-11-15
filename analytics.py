"""Utility helpers for anonymized support-bot analytics."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


ANALYTICS_FILE = Path(os.getenv('SUPPORT_ANALYTICS_FILE', 'analytics/support_metrics.json'))

INTENT_KEYWORDS = {
    'billing': {'invoice', 'price', 'pricing', 'bill', 'payment'},
    'deployment': {'deploy', 'docker', 'kubernetes', 'cloud', 'server'},
    'usage': {'use', 'run', 'setup', 'install', 'configure', 'start'},
    'support': {'help', 'issue', 'bug', 'error', 'broken'},
}


def categorize_intent(message: str) -> str:
    """Map a raw message to a simple intent bucket via keyword heuristics."""

    normalized = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return intent
    return 'other'


def _load_metrics() -> Dict[str, object]:
    if ANALYTICS_FILE.exists():
        try:
            with ANALYTICS_FILE.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'total_queries': 0,
        'fallback_count': 0,
        'intent_counts': {},
        'total_response_time_ms': 0.0,
        'last_updated': None,
        'tenant_breakdown': {}
    }


def _save_metrics(metrics: Dict[str, object]) -> None:
    ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with ANALYTICS_FILE.open('w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)


def record_support_interaction(
    message: str,
    fallback_used: bool,
    tenant_id: Optional[str] = None,
    response_time_ms: Optional[float] = None
) -> Dict[str, object]:
    """Persist anonymized metrics for support bot traffic."""

    metrics = _load_metrics()
    metrics['total_queries'] = metrics.get('total_queries', 0) + 1
    metrics['fallback_count'] = metrics.get('fallback_count', 0) + (1 if fallback_used else 0)
    metrics['total_response_time_ms'] = metrics.get('total_response_time_ms', 0.0) + float(response_time_ms or 0.0)

    intent_counts = metrics.get('intent_counts') or {}
    intent = categorize_intent(message)
    intent_counts[intent] = intent_counts.get(intent, 0) + 1
    metrics['intent_counts'] = intent_counts
    metrics['last_updated'] = datetime.utcnow().isoformat() + 'Z'

    tenant_key = tenant_id or 'default'
    tenant_breakdown = metrics.get('tenant_breakdown') or {}
    tenant_stats = tenant_breakdown.get(tenant_key) or {
        'queries': 0,
        'fallbacks': 0,
        'intent_counts': {},
        'total_response_time_ms': 0.0
    }
    tenant_stats['queries'] += 1
    tenant_stats['fallbacks'] += 1 if fallback_used else 0
    tenant_intents = tenant_stats.get('intent_counts') or {}
    intent = categorize_intent(message)
    tenant_intents[intent] = tenant_intents.get(intent, 0) + 1
    tenant_stats['intent_counts'] = tenant_intents
    tenant_stats['total_response_time_ms'] = tenant_stats.get('total_response_time_ms', 0.0) + float(response_time_ms or 0.0)
    tenant_breakdown[tenant_key] = tenant_stats
    metrics['tenant_breakdown'] = tenant_breakdown

    _save_metrics(metrics)
    return metrics


def compute_fallback_rate(metrics: Dict[str, object]) -> float:
    total = metrics.get('total_queries', 0)
    if not total:
        return 0.0
    return metrics.get('fallback_count', 0) / total


def compute_average_response_time_ms(metrics: Dict[str, object]) -> float:
    total = metrics.get('total_queries', 0)
    if not total:
        return 0.0
    return metrics.get('total_response_time_ms', 0.0) / total


def compute_tenant_summaries(metrics: Dict[str, object]) -> Dict[str, Dict[str, float]]:
    summaries: Dict[str, Dict[str, float]] = {}
    tenant_breakdown = metrics.get('tenant_breakdown') or {}
    for tenant_id, stats in tenant_breakdown.items():
        queries = stats.get('queries', 0) or 0
        fallbacks = stats.get('fallbacks', 0) or 0
        total_rt = stats.get('total_response_time_ms', 0.0) or 0.0
        summaries[tenant_id] = {
            'queries': queries,
            'fallback_rate': (fallbacks / queries) if queries else 0.0,
            'average_response_time_ms': (total_rt / queries) if queries else 0.0
        }
    return summaries
