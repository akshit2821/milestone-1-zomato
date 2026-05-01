from src.services.data_store import CandidateSelectionResult, RestaurantStore


class Phase1CandidateSelector:
    def __init__(self, store: RestaurantStore) -> None:
        self.store = store

    def select(
        self,
        location: str,
        budget: str,
        cuisine: str,
        min_rating: float,
        max_candidates: int,
    ) -> CandidateSelectionResult:
        return self.store.select_candidates(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=min_rating,
            max_candidates=max_candidates,
        )
