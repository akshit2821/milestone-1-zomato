from __future__ import annotations

import json
from pathlib import Path


class RankingSignalStore:
    def __init__(self, file_path: str = "data/ranking_signals.json") -> None:
        self.file_path = Path(file_path)
        self._signals: dict = {}
        self._load()

    def _load(self) -> None:
        if self.file_path.exists():
            self._signals = json.loads(self.file_path.read_text(encoding="utf-8"))
        else:
            self._signals = {}

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(self._signals, indent=2), encoding="utf-8")

    def get_score(self, restaurant_name: str) -> float:
        return float(self._signals.get(restaurant_name, 0.0))

    def record_feedback(self, restaurant_name: str, score_delta: float) -> None:
        current = float(self._signals.get(restaurant_name, 0.0))
        self._signals[restaurant_name] = current + score_delta
        self._save()
