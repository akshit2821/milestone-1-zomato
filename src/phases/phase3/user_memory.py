from __future__ import annotations

import json
from pathlib import Path


class UserMemoryStore:
    def __init__(self, file_path: str = "data/user_profiles.json") -> None:
        self.file_path = Path(file_path)
        self._state: dict = {}
        self._load()

    def _load(self) -> None:
        if self.file_path.exists():
            self._state = json.loads(self.file_path.read_text(encoding="utf-8"))
        else:
            self._state = {}

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def get_preferences(self, user_id: str) -> dict:
        return self._state.get(user_id, {})

    def update_preferences(self, user_id: str, payload: dict) -> None:
        current = self._state.get(user_id, {})
        current.update(payload)
        self._state[user_id] = current
        self._save()
