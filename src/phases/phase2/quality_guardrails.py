from typing import List

from src.services.prompt_builder import build_phase2_prompt
from src.services.response_validator import validate_ranked_output


class Phase2QualityGuardrails:
    def build_prompt(self, candidates: List[dict], cuisine: str, preferences: List[str]) -> str:
        return build_phase2_prompt(candidates, cuisine, preferences)

    def is_valid_output(self, items: List[dict]) -> bool:
        return validate_ranked_output(items)
