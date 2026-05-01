from __future__ import annotations

from typing import List

from src.phases.phase3.ranking_signals import RankingSignalStore


class HybridRanker:
    """
    Hybrid ranking for Phase 3:
    final_score = base_rating + learned_signal + preference_match_bonus
    """

    def __init__(self, signal_store: RankingSignalStore) -> None:
        self.signal_store = signal_store

    def rerank(self, items: List[dict], preferred_cuisine: str) -> List[dict]:
        cuisine_key = preferred_cuisine.strip().lower()

        def final_score(item: dict) -> float:
            base = float(item.get("rating", 0.0))
            signal = self.signal_store.get_score(item.get("restaurant_name", ""))
            cuisine_text = str(item.get("cuisine", "")).lower()
            cuisine_bonus = 0.3 if cuisine_key and cuisine_key in cuisine_text else 0.0
            return base + signal + cuisine_bonus

        return sorted(items, key=final_score, reverse=True)
