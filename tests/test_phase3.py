import json
from pathlib import Path

from src.phases.phase3.hybrid_ranker import HybridRanker
from src.phases.phase3.ranking_signals import RankingSignalStore
from src.phases.phase3.user_memory import UserMemoryStore


def test_phase3_user_memory_store(tmp_path: Path) -> None:
    memory_path = tmp_path / "user_profiles.json"
    store = UserMemoryStore(str(memory_path))
    store.update_preferences("user-1", {"last_cuisine": "chinese"})

    loaded = json.loads(memory_path.read_text(encoding="utf-8"))
    assert loaded["user-1"]["last_cuisine"] == "chinese"
    assert store.get_preferences("user-1")["last_cuisine"] == "chinese"


def test_phase3_hybrid_ranker_uses_signal_boost(tmp_path: Path) -> None:
    signal_path = tmp_path / "signals.json"
    signal_store = RankingSignalStore(str(signal_path))
    signal_store.record_feedback("Restaurant A", 1.0)

    ranker = HybridRanker(signal_store)
    ranked = ranker.rerank(
        [
            {"restaurant_name": "Restaurant B", "cuisine": "chinese", "rating": 4.5},
            {"restaurant_name": "Restaurant A", "cuisine": "chinese", "rating": 4.0},
        ],
        preferred_cuisine="chinese",
    )
    assert ranked[0]["restaurant_name"] == "Restaurant A"
