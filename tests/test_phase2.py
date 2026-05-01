from src.services.data_store import RestaurantStore
from src.services.prompt_builder import build_phase2_prompt
from src.services.response_validator import validate_ranked_output


def test_phase2_fallback_ladder_is_used() -> None:
    store = RestaurantStore()
    store.load()

    result = store.select_candidates(
        location="Delhi",
        budget="low",
        cuisine="japanese",
        min_rating=4.8,
        max_candidates=10,
    )

    assert result.fallback_used is True
    assert len(result.rows) >= 1
    assert result.fallback_reason is not None


def test_phase2_prompt_and_validator() -> None:
    candidates = [
        {
            "name": "Dragon Bowl",
            "city": "delhi",
            "cuisines": "chinese",
            "rating": 4.4,
            "avg_cost_for_two": 1000,
        }
    ]
    prompt = build_phase2_prompt(candidates, "chinese", ["quick service"])
    assert "Candidates:" in prompt
    assert "Dragon Bowl" in prompt

    valid_output = [
        {
            "restaurant_name": "Dragon Bowl",
            "cuisine": "chinese",
            "rating": 4.4,
            "estimated_cost": 1000,
            "explanation": "Good match.",
        }
    ]
    assert validate_ranked_output(valid_output) is True
