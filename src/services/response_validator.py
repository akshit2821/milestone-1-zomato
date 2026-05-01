from __future__ import annotations

from typing import List


REQUIRED_KEYS = {"restaurant_name", "cuisine", "rating", "estimated_cost", "explanation"}


def validate_ranked_output(items: List[dict]) -> bool:
    if not isinstance(items, list):
        return False
    if len(items) == 0:
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        if not REQUIRED_KEYS.issubset(item.keys()):
            return False
        if not isinstance(item["explanation"], str) or len(item["explanation"].strip()) == 0:
            return False
    return True
