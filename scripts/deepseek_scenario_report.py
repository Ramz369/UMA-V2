import os
import json
from pathlib import Path
import subprocess

try:
    import requests
except ImportError as exc:
    raise SystemExit("The 'requests' package is required to run this script") from exc

API_URL = "https://api.deepseek.com/chat/completions"  # V3 endpoint
MODEL = "deepseek-chat"
OUTPUT_PATH = Path("reports/cognimap/deepseek_scenario_report.md")


def collect_repo_context() -> str:
    """Return a high level snapshot of the repository structure."""
    # Use git to list top level directories and file counts
    result = subprocess.run(
        ["git", "ls-tree", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    entries = result.stdout.strip().splitlines()
    categories = {"core": [], "docs": [], "tests": [], "scripts": [], "other": []}
    for entry in entries:
        path = Path(entry)
        if not path.is_dir():
            continue
        name = path.name.lower()
        if name in {"src", "services", "core"}:
            categories["core"].append(entry)
        elif name in {"docs", "documentation"}:
            categories["docs"].append(entry)
        elif name in {"tests", "test"}:
            categories["tests"].append(entry)
        elif name in {"scripts", "tools"}:
            categories["scripts"].append(entry)
        else:
            categories["other"].append(entry)
    return json.dumps(categories, indent=2)


def generate_report(context: str, api_key: str) -> str:
    """Call DeepSeek API to create an architecture scenario report."""
    headers = {"Authorization": f"Bearer {api_key}"}
    prompt = (
        "You are an expert software architect. Given the repository snapshot below, "
        "identify core architectural elements, categorize them, highlight gaps, and "
        "suggest semantic linkages. Return a concise report.\n\n" + context
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You analyze repository structures."},
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def main() -> None:
    context = collect_repo_context()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY environment variable not set")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = generate_report(context, api_key)
    OUTPUT_PATH.write_text(report)
    print(f"Report written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
