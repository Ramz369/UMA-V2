
"""
@cognimap:fingerprint
id: eab608ac-719f-45c9-afc5-2e5f257cef47
birth: 2025-08-07T07:23:38.062022Z
parent: None
intent: AST-aware diff for JSON / YAML / SQL - Production Implementation.
semantic_tags: [authentication, database, testing, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.062321Z
hash: affecaba
language: python
type: tool
@end:cognimap
"""

"""AST-aware diff for JSON / YAML / SQL - Production Implementation."""
from __future__ import annotations
import json
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional

# Make sqlparse optional for testing
try:
    import sqlparse
except ImportError:
    sqlparse = None
from dataclasses import dataclass
from enum import Enum
import hashlib


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class DiffNode:
    path: str
    change_type: ChangeType
    old_value: Any = None
    new_value: Any = None
    
    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "type": self.change_type.value,
            "old": self.old_value,
            "new": self.new_value
        }


class SemanticDiffer:
    """AST-aware differ for structured data formats."""
    
    def __init__(self):
        self.changes: List[DiffNode] = []
    
    def diff(self, old_text: str, new_text: str, lang: str) -> dict:
        """Generate semantic diff based on language type."""
        self.changes = []
        
        try:
            if lang.lower() in ["json", "yaml", "yml"]:
                return self._diff_structured(old_text, new_text, lang)
            elif lang.lower() == "sql":
                return self._diff_sql(old_text, new_text)
            else:
                return self._diff_text(old_text, new_text, lang)
        except Exception as e:
            return {
                "lang": lang,
                "error": str(e),
                "fallback": self._diff_text(old_text, new_text, lang)
            }
    
    def _diff_structured(self, old_text: str, new_text: str, lang: str) -> dict:
        """Diff JSON or YAML as nested structures."""
        # Parse based on format
        if lang.lower() == "json":
            old_data = json.loads(old_text) if old_text else {}
            new_data = json.loads(new_text) if new_text else {}
        else:  # YAML
            old_data = yaml.safe_load(old_text) if old_text else {}
            new_data = yaml.safe_load(new_text) if new_text else {}
        
        # Perform recursive diff
        self._recursive_diff(old_data, new_data, "")
        
        return {
            "lang": lang,
            "changes": [c.to_dict() for c in self.changes],
            "summary": {
                "added": len([c for c in self.changes if c.change_type == ChangeType.ADDED]),
                "removed": len([c for c in self.changes if c.change_type == ChangeType.REMOVED]),
                "modified": len([c for c in self.changes if c.change_type == ChangeType.MODIFIED])
            }
        }
    
    def _recursive_diff(self, old_data: Any, new_data: Any, path: str) -> None:
        """Recursively compare nested structures."""
        if type(old_data) != type(new_data):
            self.changes.append(DiffNode(
                path=path or "root",
                change_type=ChangeType.MODIFIED,
                old_value=old_data,
                new_value=new_data
            ))
            return
        
        if isinstance(old_data, dict):
            all_keys = set(old_data.keys()) | set(new_data.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key not in old_data:
                    self.changes.append(DiffNode(
                        path=new_path,
                        change_type=ChangeType.ADDED,
                        new_value=new_data[key]
                    ))
                elif key not in new_data:
                    self.changes.append(DiffNode(
                        path=new_path,
                        change_type=ChangeType.REMOVED,
                        old_value=old_data[key]
                    ))
                else:
                    self._recursive_diff(old_data[key], new_data[key], new_path)
        
        elif isinstance(old_data, list):
            # Compare lists by index (could be enhanced with sequence matching)
            max_len = max(len(old_data), len(new_data))
            for i in range(max_len):
                new_path = f"{path}[{i}]"
                if i >= len(old_data):
                    self.changes.append(DiffNode(
                        path=new_path,
                        change_type=ChangeType.ADDED,
                        new_value=new_data[i]
                    ))
                elif i >= len(new_data):
                    self.changes.append(DiffNode(
                        path=new_path,
                        change_type=ChangeType.REMOVED,
                        old_value=old_data[i]
                    ))
                else:
                    self._recursive_diff(old_data[i], new_data[i], new_path)
        
        elif old_data != new_data:
            self.changes.append(DiffNode(
                path=path or "root",
                change_type=ChangeType.MODIFIED,
                old_value=old_data,
                new_value=new_data
            ))
    
    def _diff_sql(self, old_text: str, new_text: str) -> dict:
        """Parse and diff SQL statements."""
        if sqlparse is None:
            # Fallback to text diff if sqlparse not available
            return self._diff_text(old_text, new_text)
        
        old_parsed = sqlparse.parse(old_text)
        new_parsed = sqlparse.parse(new_text)
        
        changes = []
        
        # Compare number of statements
        if len(old_parsed) != len(new_parsed):
            changes.append({
                "type": "statement_count",
                "old": len(old_parsed),
                "new": len(new_parsed)
            })
        
        # Compare each statement
        for i, (old_stmt, new_stmt) in enumerate(zip(old_parsed, new_parsed)):
            old_tokens = [str(t) for t in old_stmt.tokens if not t.is_whitespace]
            new_tokens = [str(t) for t in new_stmt.tokens if not t.is_whitespace]
            
            if old_tokens != new_tokens:
                changes.append({
                    "type": "statement_modified",
                    "index": i,
                    "old_hash": hashlib.md5(str(old_stmt).encode()).hexdigest()[:8],
                    "new_hash": hashlib.md5(str(new_stmt).encode()).hexdigest()[:8]
                })
        
        return {
            "lang": "sql",
            "changes": changes,
            "statement_count": {
                "old": len(old_parsed),
                "new": len(new_parsed)
            }
        }
    
    def _diff_text(self, old_text: str, new_text: str, lang: str) -> dict:
        """Fallback line-based diff."""
        import difflib
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        
        differ = difflib.unified_diff(old_lines, new_lines, lineterm='')
        hunks = list(differ)
        
        return {
            "lang": lang,
            "type": "text_diff",
            "hunks": hunks,
            "lines_added": sum(1 for h in hunks if h.startswith('+')),
            "lines_removed": sum(1 for h in hunks if h.startswith('-'))
        }


def diff(old_text: str, new_text: str, lang: str) -> dict:
    """Main entry point for semantic diff."""
    differ = SemanticDiffer()
    return differ.diff(old_text, new_text, lang)


if __name__ == "__main__":
    # CLI usage example
    if len(sys.argv) < 2:
        print("Usage: python semantic_diff.py <lang> < old_file > new_file")
        sys.exit(1)
    
    lang = sys.argv[1]
    print("Enter old content (Ctrl+D to end):")
    old = sys.stdin.read()
    print("Enter new content (Ctrl+D to end):")
    new = sys.stdin.read()
    
    result = diff(old, new, lang)
    print(json.dumps(result, indent=2))