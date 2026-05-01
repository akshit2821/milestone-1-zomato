from __future__ import annotations

from typing import List


def build_phase2_prompt(candidates: List[dict], user_cuisine: str, user_preferences: List[str]) -> str:
    """
    Prompt template v2:
    - Keep output concise and factual.
    - Ground claims to known candidate fields only.
    """
    preferences = ", ".join(user_preferences) if user_preferences else "general preferences"
    candidate_lines = []
    for idx, item in enumerate(candidates, start=1):
        candidate_lines.append(
            (
                f"{idx}. name={item.get('name', '')}; city={item.get('city', '')}; "
                f"cuisines={item.get('cuisines', '')}; rating={item.get('rating', 0)}; "
                f"avg_cost_for_two={item.get('avg_cost_for_two', 0)}"
            )
        )

    candidate_block = "\n".join(candidate_lines)
    return (
        "You are a restaurant recommendation assistant.\n"
        "Task:\n"
        "- Rank restaurants for the user query.\n"
        "- Explain each pick in 1-2 short sentences.\n"
        "- Use only provided candidate fields.\n"
        "- Do not invent attributes not present in candidate data.\n\n"
        f"User cuisine preference: {user_cuisine}\n"
        f"Optional preferences: {preferences}\n\n"
        f"Candidates:\n{candidate_block}\n"
    )
