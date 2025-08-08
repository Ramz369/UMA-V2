#!/usr/bin/env python3
"""
DeepSeek Scenario Report Generator
Generates architectural analysis reports using DeepSeek API
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import requests
from datetime import datetime


def collect_repo_context(root_path: Path) -> str:
    """Collect repository context for analysis"""
    context_parts = []
    
    # Collect basic project info
    project_name = root_path.name
    context_parts.append(f"Project: {project_name}")
    
    # Look for README
    readme_path = root_path / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            readme_content = f.read()[:1000]  # First 1000 chars
            context_parts.append(f"README:\n{readme_content}")
    
    # Collect file structure
    py_files = list(root_path.rglob("*.py"))
    js_files = list(root_path.rglob("*.js"))
    ts_files = list(root_path.rglob("*.ts"))
    
    context_parts.append(f"\nProject Structure:")
    context_parts.append(f"- Python files: {len(py_files)}")
    context_parts.append(f"- JavaScript files: {len(js_files)}")
    context_parts.append(f"- TypeScript files: {len(ts_files)}")
    
    # Sample some key files
    key_files = []
    for pattern in ["**/main.py", "**/app.py", "**/index.js", "**/package.json"]:
        matches = list(root_path.glob(pattern))
        if matches:
            key_files.extend(matches[:2])
    
    if key_files:
        context_parts.append("\nKey Files Found:")
        for file in key_files[:5]:
            context_parts.append(f"- {file.relative_to(root_path)}")
    
    # Check for architecture graph
    graph_path = root_path / "cognimap/visualizer/output/architecture_graph_enhanced.json"
    if graph_path.exists():
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)
            context_parts.append(f"\nArchitecture Graph:")
            context_parts.append(f"- Nodes: {len(graph_data.get('nodes', []))}")
            context_parts.append(f"- Edges: {len(graph_data.get('edges', []))}")
    
    return "\n".join(context_parts)


def generate_report(context: str, api_key: str) -> str:
    """Generate a scenario report using DeepSeek API"""
    
    prompt = f"""
    Based on the following codebase context, generate a comprehensive scenario report:
    
    {context}
    
    Please provide:
    1. Executive Summary
    2. Architecture Overview
    3. Component Analysis
    4. Identified Patterns
    5. Potential Issues/Gaps
    6. Recommendations for Improvement
    7. Implementation Priority
    
    Format the response as a structured markdown report.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert software architect conducting a comprehensive codebase analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        report = data['choices'][0]['message']['content']
        
        # Add metadata
        full_report = f"""# CogniMap Scenario Report
Generated: {datetime.now().isoformat()}

{report}

---
*Generated with DeepSeek AI Analysis*
"""
        
        return full_report
        
    except Exception as e:
        return f"# Error Generating Report\n\nFailed to generate scenario report: {str(e)}"


if __name__ == "__main__":
    # Test standalone
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        context = collect_repo_context(Path.cwd())
        report = generate_report(context, api_key)
        
        output_path = Path("reports/cognimap/scenario_report.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        
        print(f"Report saved to {output_path}")
    else:
        print("DEEPSEEK_API_KEY not found in environment")