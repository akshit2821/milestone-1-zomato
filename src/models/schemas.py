from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    user_id: Optional[str] = Field(default=None, min_length=2, max_length=64)
    location: str = Field(..., min_length=2, max_length=80)
    budget: str = Field(..., min_length=2, max_length=30)
    cuisine: str = Field(..., min_length=2, max_length=60)
    min_rating: float = Field(..., ge=0.0, le=5.0)
    optional_preferences: Optional[List[str]] = Field(default_factory=list)
    top_n: int = Field(default=5, ge=1, le=10)

    @field_validator("location", "budget", "cuisine")
    @classmethod
    def trim_and_lower(cls, value: str) -> str:
        return value.strip()


class RecommendationItem(BaseModel):
    restaurant_name: str
    cuisine: str
    rating: float
    estimated_cost: float
    explanation: str


class RecommendationMeta(BaseModel):
    candidate_count: int
    processing_time_ms: int
    fallback_used: bool
    fallback_reason: Optional[str] = None


class RecommendationResponse(BaseModel):
    request_id: str
    recommendations: List[RecommendationItem]
    meta: RecommendationMeta


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    data_loaded: bool


class FeedbackRequest(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=64)
    restaurant_name: str = Field(..., min_length=2, max_length=120)
    score_delta: float = Field(default=0.5, ge=-2.0, le=2.0)


class GenericMessageResponse(BaseModel):
    status: str
    message: str
