from __future__ import annotations

from dataclasses import dataclass

from src.core.config import settings


@dataclass
class FallbackPolicy:
    rating_step: float = settings.fallback_rating_step
    max_steps: int = settings.fallback_max_steps


def relaxed_rating(min_rating: float, step_index: int, policy: FallbackPolicy) -> float:
    reduction = policy.rating_step * step_index
    return max(0.0, min_rating - reduction)
