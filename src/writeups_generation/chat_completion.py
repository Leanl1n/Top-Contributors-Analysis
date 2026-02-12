"""
Chat completion module: generates sample writeups from the user's uploaded dataframe.
Uses the DeepSeek service and prompts from prompts.json (sankey / quadrant).
"""
import json
import os
from typing import Optional

import pandas as pd

from service.deepseek import DeepSeekService

_PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts.json")

_DEFAULT_PROMPTS = {
    "sankey": "",
    "quadrant": "",
}


def _load_prompts() -> dict:
    """Load prompts from prompts.json. Falls back to empty strings if file missing."""
    if not os.path.isfile(_PROMPTS_PATH):
        return _DEFAULT_PROMPTS.copy()
    try:
        with open(_PROMPTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "sankey": data.get("sankey", ""),
            "quadrant": data.get("quadrant", ""),
        }
    except Exception:
        return _DEFAULT_PROMPTS.copy()


def _get_prompt_for_analysis(analysis_type: str) -> str:
    """Return the prompt text for the given analysis type ('sankey' or 'quadrant')."""
    prompts = _load_prompts()
    key = analysis_type.strip().lower() if analysis_type else "sankey"
    if key not in prompts:
        key = "sankey"
    return prompts[key] or "Generate a professional analysis summary based on the provided data."


def _dataframe_context(df: pd.DataFrame, max_sample_rows: int = 30) -> str:
    """Build a concise text summary of the dataframe for the model."""
    lines = [
        f"Shape: {df.shape[0]} rows, {df.shape[1]} columns",
        f"Columns: {list(df.columns)}",
        "",
        "Sample rows (first rows):",
        df.head(max_sample_rows).to_string(),
    ]
    return "\n".join(lines)


def generate_writeups(
    df: pd.DataFrame,
    *,
    analysis_type: Optional[str] = None,
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    max_sample_rows: int = 30,
    **kwargs,
) -> str:
    """Generate writeups from the dataframe. Uses the prompt for analysis_type from prompts.json unless prompt is provided."""
    context = _dataframe_context(df, max_sample_rows=max_sample_rows)
    instruction = prompt if prompt is not None else _get_prompt_for_analysis(analysis_type or "sankey")
    user_content = (
        "Here is the dataframe summary and sample data:\n\n"
        f"{context}\n\n"
        f"{instruction}"
    )
    svc = DeepSeekService(api_key=api_key)
    return svc.complete(user_content, **kwargs)
