from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import create_router
from src.core.config import settings
from src.services.data_store import RestaurantStore
from src.services.llm_client import LLMClient
from src.services.metrics import MetricsCollector
from src.services.recommender import RecommenderService

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://milestone-1-zomato-two.vercel.app",
        "https://milestone-1-zomato-29n6axcsk-akshit2821s-projects.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = RestaurantStore()
store.load()
llm_client = LLMClient()
metrics_collector = MetricsCollector()
recommender_service = RecommenderService(
    store=store, llm_client=llm_client, metrics=metrics_collector
)
app.include_router(create_router(recommender_service, store.is_loaded, metrics_collector))
