import json
import os
from pathlib import Path
from dotenv import load_dotenv

import requests

# Load environment variables
load_dotenv()


DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"


def request_improvements(symbol_graph_path: Path):
    """Send the symbol graph to DeepSeek V3 for analysis and improvements.
    
    Returns AI-generated improvement suggestions or None if API unavailable.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("DEEPSEEK_API_KEY not set; skipping DeepSeek analysis")
        return None

    # Load symbol graph
    with open(symbol_graph_path, "r", encoding="utf-8") as fh:
        symbol_graph = json.load(fh)
    
    # Create analysis prompt
    prompt = f"""Analyze this software architecture symbol graph and provide improvement suggestions:

Symbol Graph Summary:
- Total Symbols: {len(symbol_graph)}
- Files: {len(set(s.get('file', '') for s in symbol_graph.values()))}

Key Symbols:
{json.dumps(list(symbol_graph.keys())[:20], indent=2)}

Please identify:
1. Architectural patterns and anti-patterns
2. Missing connections between components
3. Potential refactoring opportunities
4. Security or performance concerns
5. Suggested improvements with priority

Provide structured JSON response with 'suggestions' array."""

    # Prepare DeepSeek V3 payload
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an expert software architect analyzing codebases for improvements."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(DEEPSEEK_ENDPOINT, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract suggestions from response
        content = data['choices'][0]['message']['content']
        
        # Try to parse as JSON, or create structured format
        try:
            suggestions = json.loads(content)
            if not isinstance(suggestions, dict):
                suggestions = {"suggestions": suggestions}
        except json.JSONDecodeError:
            # If not JSON, structure the text response
            suggestions = {
                "suggestions": [
                    {"type": "analysis", "content": content, "priority": "medium"}
                ]
            }
        
        # Save suggestions
        suggestions_path = symbol_graph_path.parent / "improvement_suggestions.json"
        with open(suggestions_path, "w", encoding="utf-8") as fh:
            json.dump(suggestions, fh, indent=2)
        
        print(f"✅ DeepSeek analysis complete. Saved to {suggestions_path}")
        return suggestions
        
    except Exception as exc:
        print(f"❌ DeepSeek request failed: {exc}")
        return None
