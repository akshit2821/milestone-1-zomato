import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.schemas import RecommendationRequest
from src.services.data_store import RestaurantStore
from src.services.llm_client import LLMClient
from src.services.metrics import MetricsCollector
from src.services.recommender import RecommenderService


CASES_PATH = Path("tests/evaluation_cases.json")


def main() -> None:
    if not CASES_PATH.exists():
        raise FileNotFoundError("Missing tests/evaluation_cases.json")

    store = RestaurantStore()
    store.load()
    service = RecommenderService(store=store, llm_client=LLMClient(), metrics=MetricsCollector())

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    passed = 0
    for case in cases:
        payload = RecommendationRequest(**case["request"])
        response = service.recommend(payload)
        if len(response.recommendations) >= int(case["expected_min_results"]):
            passed += 1

    total = len(cases)
    score = (passed / total) * 100 if total else 0
    print(f"Phase 2 evaluation score: {score:.2f}% ({passed}/{total})")


if __name__ == "__main__":
    main()
