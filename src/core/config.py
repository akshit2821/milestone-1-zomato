from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Restaurant Recommendation API"
    app_version: str = "0.1.0"
    data_file_path: str = "data/restaurants_clean.csv"
    llm_mode: str = "deterministic"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1/chat/completions"
    llm_model: str = "llama-3.1-8b-instant"
    llm_timeout_seconds: float = 12.0
    max_candidate_pool: int = 30
    top_n_default: int = 5
    fallback_rating_step: float = 0.5
    fallback_max_steps: int = 3
    phase3_user_memory_path: str = "data/user_profiles.json"
    phase3_signal_store_path: str = "data/ranking_signals.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def resolved_llm_api_key(self) -> str:
        return self.llm_api_key.strip()


settings = Settings()
