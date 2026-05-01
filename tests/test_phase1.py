from src.services.data_store import RestaurantStore


def test_phase1_strict_candidate_selection() -> None:
    store = RestaurantStore()
    store.load()

    result = store.select_candidates(
        location="Delhi",
        budget="medium",
        cuisine="chinese",
        min_rating=4.0,
        max_candidates=10,
    )

    assert len(result.rows) >= 1
    assert result.fallback_used is False
