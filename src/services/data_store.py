from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from src.core.config import settings
from src.services.fallback_engine import FallbackPolicy, relaxed_rating


BUDGET_BUCKETS = {
    "low": (0, 700),
    "medium": (701, 1800),
    "high": (1801, 100000),
}


@dataclass
class CandidateSelectionResult:
    rows: List[dict]
    fallback_used: bool
    fallback_reason: str | None = None


class RestaurantStore:
    def __init__(self) -> None:
        self._df = pd.DataFrame()

    def load(self) -> None:
        data_path = Path(settings.data_file_path)
        if not data_path.exists():
            self._df = pd.DataFrame()
            return
        self._df = pd.read_csv(data_path)
        self._normalize()

    def is_loaded(self) -> bool:
        return not self._df.empty

    def _normalize(self) -> None:
        if self._df.empty:
            return
        self._df.columns = [col.strip().lower() for col in self._df.columns]
        required_columns = ["name", "city", "locality", "cuisines", "rating", "avg_cost_for_two"]
        for column in required_columns:
            if column not in self._df.columns:
                self._df[column] = ""
        self._df["name"] = self._df["name"].astype(str).str.strip()
        self._df["city"] = self._df["city"].astype(str).str.strip().str.lower()
        self._df["locality"] = self._df["locality"].astype(str).str.strip().str.lower()
        self._df["cuisines"] = self._df["cuisines"].astype(str).str.strip().str.lower()
        self._df["rating"] = pd.to_numeric(self._df["rating"], errors="coerce").fillna(0.0)
        self._df["avg_cost_for_two"] = pd.to_numeric(
            self._df["avg_cost_for_two"], errors="coerce"
        ).fillna(0.0)
        self._df = self._df.dropna(subset=["name"])

    def _apply_budget_filter(self, frame: pd.DataFrame, budget: str) -> pd.DataFrame:
        budget_key = budget.strip().lower()
        if budget_key in BUDGET_BUCKETS:
            min_cost, max_cost = BUDGET_BUCKETS[budget_key]
            return frame[
                (frame["avg_cost_for_two"] >= min_cost)
                & (frame["avg_cost_for_two"] <= max_cost)
            ]
        # Numeric range format like "500-1500"
        if "-" in budget_key:
            parts = budget_key.split("-", maxsplit=1)
            try:
                min_cost = float(parts[0].strip())
                max_cost = float(parts[1].strip())
                return frame[
                    (frame["avg_cost_for_two"] >= min_cost)
                    & (frame["avg_cost_for_two"] <= max_cost)
                ]
            except ValueError:
                return frame
        return frame

    def select_candidates(
        self,
        location: str,
        budget: str,
        cuisine: str,
        min_rating: float,
        max_candidates: int,
    ) -> CandidateSelectionResult:
        if self._df.empty:
            return CandidateSelectionResult(rows=[], fallback_used=False, fallback_reason=None)

        city_or_locality = location.strip().lower()
        cuisine_key = cuisine.strip().lower()

        # More flexible location matching - try exact matches first, then contains
        city_exact = self._df[self._df["city"].str.lower() == city_or_locality]
        locality_exact = self._df[self._df["locality"].str.lower() == city_or_locality]
        city_contains = self._df[self._df["city"].str.contains(city_or_locality, case=False, na=False)]
        locality_contains = self._df[self._df["locality"].str.contains(city_or_locality, case=False, na=False)]
        
        strict = pd.concat([city_exact, locality_exact, city_contains, locality_contains]).drop_duplicates()
        strict = self._apply_budget_filter(strict, budget)
        strict = strict[strict["cuisines"].str.contains(cuisine_key, case=False, na=False)]
        strict = strict[strict["rating"] >= min_rating]

        if not strict.empty:
            strict = strict.sort_values(
                by=["rating", "avg_cost_for_two"], ascending=[False, True]
            )
            return CandidateSelectionResult(
                rows=strict.head(max_candidates).to_dict(orient="records"),
                fallback_used=False,
                fallback_reason=None,
            )

        # Controlled fallback ladder using configurable policy.
        policy = FallbackPolicy()
        for step in range(1, policy.max_steps + 1):
            min_rating_for_step = relaxed_rating(min_rating, step, policy)
            fallback = self._df[
                (self._df["city"].str.contains(city_or_locality, na=False))
                | (self._df["locality"].str.contains(city_or_locality, na=False))
            ]
            fallback = self._apply_budget_filter(fallback, budget)
            fallback = fallback[fallback["rating"] >= min_rating_for_step]
            if not fallback.empty:
                fallback = fallback.sort_values(
                    by=["rating", "avg_cost_for_two"], ascending=[False, True]
                )
                return CandidateSelectionResult(
                    rows=fallback.head(max_candidates).to_dict(orient="records"),
                    fallback_used=True,
                    fallback_reason=(
                        "Fallback applied: relaxed rating and cuisine strictness "
                        f"(step {step}, min_rating={min_rating_for_step})."
                    ),
                )

        # Last-resort fallback to keep UX graceful when location has no matches.
        last_resort = self._apply_budget_filter(self._df.copy(), budget)
        last_resort = last_resort[last_resort["rating"] >= relaxed_rating(min_rating, policy.max_steps, policy)]
        last_resort = last_resort.sort_values(by=["rating", "avg_cost_for_two"], ascending=[False, True])
        if not last_resort.empty:
            return CandidateSelectionResult(
                rows=last_resort.head(max_candidates).to_dict(orient="records"),
                fallback_used=True,
                fallback_reason=(
                    "Fallback applied: no location match; returned city-agnostic best matches "
                    "within budget and relaxed rating."
                ),
            )

        return CandidateSelectionResult(
            rows=[],
            fallback_used=True,
            fallback_reason="No candidates found after all fallback steps.",
        )
