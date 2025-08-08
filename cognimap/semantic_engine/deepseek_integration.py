import json
import os
from pathlib import Path

import requests


DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/analyze"


def request_improvements(symbol_graph_path: Path):
    """Send the symbol graph to DeepSeek for further analysis.

    If the DEEPSEEK_API_KEY environment variable is missing the function will
    simply return without making a network request.  This keeps the analyzer
    usable in offline environments while still documenting how to integrate
    with the API."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("DEEPSEEK_API_KEY not set; skipping DeepSeek analysis")
        return None

    with open(symbol_graph_path, "r", encoding="utf-8") as fh:
        payload = {"symbol_graph": json.load(fh)}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        resp = requests.post(DEEPSEEK_ENDPOINT, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"DeepSeek request failed: {exc}")
        return None

    suggestions = data.get("suggestions", [])
    with open(symbol_graph_path.parent / "improvement_suggestions.json", "w", encoding="utf-8") as fh:
        json.dump(suggestions, fh, indent=2)

    return suggestions
