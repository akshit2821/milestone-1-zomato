from __future__ import annotations

import json
from typing import List

import httpx

from src.core.config import settings
from src.services.prompt_builder import build_phase2_prompt
from src.services.response_validator import validate_ranked_output


class LLMClient:
    """
    Phase 1 behavior:
    - If no external LLM is configured, we keep deterministic output.
    - This class is kept as an extension point for Phase 2.
    """

    def rank_with_explanations(
        self,
        candidates: List[dict],
        user_cuisine: str,
        optional_preferences: List[str],
    ) -> List[dict]:
        if not candidates:
            return []

        prompt_text = build_phase2_prompt(candidates, user_cuisine, optional_preferences)
        results = self._llm_rank(prompt_text)
        if validate_ranked_output(results):
            return results

        # Fallback-safe output in case model output is malformed.
        return self._deterministic_rank(candidates, user_cuisine, optional_preferences)

    def _llm_rank(self, prompt_text: str) -> List[dict]:
        if settings.llm_mode.strip().lower() != "remote":
            return []
        api_key = settings.resolved_llm_api_key()
        if not api_key:
            return []

        payload = {
            "model": settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a strict ranking service. Return only JSON array with fields: "
                        "restaurant_name, cuisine, rating, estimated_cost, explanation."
                    ),
                },
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.2,
            "max_tokens": 900,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                settings.llm_base_url,
                headers=headers,
                json=payload,
                timeout=settings.llm_timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            parsed = self._extract_json_array(content)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
        return []

    def _extract_json_array(self, content: str) -> List[dict]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            return []
        return []

    def _deterministic_rank(
        self, candidates: List[dict], user_cuisine: str, optional_preferences: List[str]
    ) -> List[dict]:
        results: List[dict] = []
        pref_text = ", ".join(optional_preferences) if optional_preferences else "general preferences"
        for item in candidates:
            explanation = (
                f"Matches your preference for {user_cuisine} with a strong rating of "
                f"{item.get('rating', 0)} and estimated cost around {item.get('avg_cost_for_two', 0)} "
                f"for two. Considered: {pref_text}."
            )
            results.append(
                {
                    "restaurant_name": item.get("name", "Unknown"),
                    "cuisine": item.get("cuisines", "Not specified"),
                    "rating": float(item.get("rating", 0.0)),
                    "estimated_cost": float(item.get("avg_cost_for_two", 0.0)),
                    "explanation": explanation,
                }
            )
        return results
