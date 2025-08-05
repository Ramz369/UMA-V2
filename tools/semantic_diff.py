"""AST-aware diff for JSON / YAML / SQL (stub)."""
from __future__ import annotations
import json, sys, difflib, pathlib, yaml, sqlparse

def diff(old_text: str, new_text: str, lang: str) -> dict:
    """Return structured diff (added, removed, modified)."""
    # TODO: full AST parsing - placeholder line-based diff
    old, new = old_text.splitlines(), new_text.splitlines()
    hunks = list(difflib.unified_diff(old, new))
    return {"lang": lang, "hunks": hunks}

if __name__ == "__main__":
    print(diff(sys.stdin.read(), sys.stdin.read(), "json"))