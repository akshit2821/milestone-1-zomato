from __future__ import annotations

import time
import uuid

from src.core.config import settings
from src.models.schemas import RecommendationMeta, RecommendationRequest, RecommendationResponse
from src.phases.phase1.candidate_selector import Phase1CandidateSelector
from src.phases.phase2.quality_guardrails import Phase2QualityGuardrails
from src.phases.phase3.hybrid_ranker import HybridRanker
from src.phases.phase3.ranking_signals import RankingSignalStore
from src.phases.phase3.user_memory import UserMemoryStore
from src.services.data_store import RestaurantStore
from src.services.llm_client import LLMClient
from src.services.metrics import MetricsCollector


class RecommenderService:
    def __init__(
        self, store: RestaurantStore, llm_client: LLMClient, metrics: MetricsCollector
    ) -> None:
        self.store = store
        self.llm_client = llm_client
        self.metrics = metrics
        self.phase1_selector = Phase1CandidateSelector(store)
        self.phase2_guardrails = Phase2QualityGuardrails()
        self.user_memory = UserMemoryStore(settings.phase3_user_memory_path)
        self.signal_store = RankingSignalStore(settings.phase3_signal_store_path)
        self.hybrid_ranker = HybridRanker(self.signal_store)

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        start = time.perf_counter()

        merged_preferences = list(request.optional_preferences or [])
        if request.user_id:
            memory = self.user_memory.get_preferences(request.user_id)
            remembered = memory.get("optional_preferences", [])
            for pref in remembered:
                if pref not in merged_preferences:
                    merged_preferences.append(pref)

        selection = self.phase1_selector.select(
            location=request.location,
            budget=request.budget,
            cuisine=request.cuisine,
            min_rating=request.min_rating,
            max_candidates=settings.max_candidate_pool,
        )

        _ = self.phase2_guardrails.build_prompt(selection.rows, request.cuisine, merged_preferences)
        ranked = self.llm_client.rank_with_explanations(
            candidates=selection.rows,
            user_cuisine=request.cuisine,
            optional_preferences=merged_preferences,
        )
        if self.phase2_guardrails.is_valid_output(ranked):
            ranked = self.hybrid_ranker.rerank(ranked, request.cuisine)

        top_n = ranked[: request.top_n]
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        if request.user_id:
            self.user_memory.update_preferences(
                request.user_id,
                {
                    "last_location": request.location,
                    "last_budget": request.budget,
                    "last_cuisine": request.cuisine,
                    "optional_preferences": merged_preferences,
                },
            )

        response = RecommendationResponse(
            request_id=str(uuid.uuid4()),
            recommendations=top_n,
            meta=RecommendationMeta(
                candidate_count=len(selection.rows),
                processing_time_ms=elapsed_ms,
                fallback_used=selection.fallback_used,
                fallback_reason=selection.fallback_reason,
            ),
        )
        self.metrics.record_success(
            latency_ms=response.meta.processing_time_ms, fallback_used=response.meta.fallback_used
        )
        return response

    def record_feedback(self, user_id: str, restaurant_name: str, score_delta: float) -> None:
        self.signal_store.record_feedback(restaurant_name=restaurant_name, score_delta=score_delta)
        memory = self.user_memory.get_preferences(user_id)
        memory["last_feedback_restaurant"] = restaurant_name
        self.user_memory.update_preferences(user_id, memory)
