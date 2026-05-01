from typing import Callable

from fastapi import APIRouter, HTTPException

from src.models.schemas import (
    FeedbackRequest,
    GenericMessageResponse,
    HealthResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from src.services.metrics import MetricsCollector
from src.services.recommender import RecommenderService


def create_router(
    service: RecommenderService, data_loaded: Callable[[], bool], metrics: MetricsCollector
) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app="restaurant-recommendation-api",
            version="0.1.0",
            data_loaded=data_loaded(),
        )

    @router.post("/recommendations", response_model=RecommendationResponse)
    def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
        if not data_loaded():
            metrics.record_failure()
            raise HTTPException(
                status_code=503,
                detail="Dataset is not loaded. Run ingestion and ensure data file exists.",
            )
        return service.recommend(payload)

    @router.get("/metrics")
    def get_metrics() -> dict:
        return metrics.snapshot()

    @router.post("/feedback", response_model=GenericMessageResponse)
    def feedback(payload: FeedbackRequest) -> GenericMessageResponse:
        service.record_feedback(
            user_id=payload.user_id,
            restaurant_name=payload.restaurant_name,
            score_delta=payload.score_delta,
        )
        return GenericMessageResponse(
            status="ok",
            message="Feedback recorded for phase 3 ranking signals.",
        )

    return router
