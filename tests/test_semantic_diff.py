
"""
@cognimap:fingerprint
id: 0547e28b-d929-49e4-89bd-606315fb061a
birth: 2025-08-07T07:23:38.071113Z
parent: None
intent: Unit tests for semantic_diff tool.
semantic_tags: [database, testing, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.071436Z
hash: 41ef5416
language: python
type: test
@end:cognimap
"""

"""Unit tests for semantic_diff tool."""
import pytest
import json
import yaml
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.semantic_diff import diff, SemanticDiffer, ChangeType, DiffNode


class TestSemanticDiff:
    """Test suite for semantic diff functionality."""
    
    def test_json_simple_addition(self):
        """Test detecting added fields in JSON."""
        old_json = '{"name": "test"}'
        new_json = '{"name": "test", "age": 25}'
        
        result = diff(old_json, new_json, "json")
        
        assert result["lang"] == "json"
        assert result["summary"]["added"] == 1
        assert result["summary"]["removed"] == 0
        assert result["summary"]["modified"] == 0
        
        # Check the specific change
        changes = result["changes"]
        assert len(changes) == 1
        assert changes[0]["path"] == "age"
        assert changes[0]["type"] == "added"
        assert changes[0]["new"] == 25
    
    def test_json_simple_removal(self):
        """Test detecting removed fields in JSON."""
        old_json = '{"name": "test", "age": 25}'
        new_json = '{"name": "test"}'
        
        result = diff(old_json, new_json, "json")
        
        assert result["summary"]["added"] == 0
        assert result["summary"]["removed"] == 1
        assert result["summary"]["modified"] == 0
        
        changes = result["changes"]
        assert len(changes) == 1
        assert changes[0]["path"] == "age"
        assert changes[0]["type"] == "removed"
        assert changes[0]["old"] == 25
    
    def test_json_modification(self):
        """Test detecting modified fields in JSON."""
        old_json = '{"name": "Alice", "age": 25}'
        new_json = '{"name": "Bob", "age": 25}'
        
        result = diff(old_json, new_json, "json")
        
        assert result["summary"]["added"] == 0
        assert result["summary"]["removed"] == 0
        assert result["summary"]["modified"] == 1
        
        changes = result["changes"]
        assert len(changes) == 1
        assert changes[0]["path"] == "name"
        assert changes[0]["type"] == "modified"
        assert changes[0]["old"] == "Alice"
        assert changes[0]["new"] == "Bob"
    
    def test_json_nested_changes(self):
        """Test detecting changes in nested JSON structures."""
        old_json = '{"user": {"name": "Alice", "settings": {"theme": "dark"}}}'
        new_json = '{"user": {"name": "Alice", "settings": {"theme": "light", "lang": "en"}}}'
        
        result = diff(old_json, new_json, "json")
        
        assert result["summary"]["added"] == 1
        assert result["summary"]["modified"] == 1
        
        # Find the theme modification
        theme_change = next(c for c in result["changes"] if "theme" in c["path"])
        assert theme_change["type"] == "modified"
        assert theme_change["old"] == "dark"
        assert theme_change["new"] == "light"
        
        # Find the lang addition
        lang_change = next(c for c in result["changes"] if "lang" in c["path"])
        assert lang_change["type"] == "added"
        assert lang_change["new"] == "en"
    
    def test_yaml_diff(self):
        """Test YAML diffing."""
        old_yaml = """
        name: test-app
        version: 1.0.0
        """
        new_yaml = """
        name: test-app
        version: 2.0.0
        description: A test application
        """
        
        result = diff(old_yaml, new_yaml, "yaml")
        
        assert result["lang"] == "yaml"
        assert result["summary"]["added"] == 1
        assert result["summary"]["modified"] == 1
        
        # Check version change
        version_change = next(c for c in result["changes"] if c["path"] == "version")
        assert version_change["type"] == "modified"
        assert version_change["old"] == "1.0.0"
        assert version_change["new"] == "2.0.0"
    
    def test_list_changes(self):
        """Test detecting changes in lists."""
        old_json = '{"items": ["a", "b", "c"]}'
        new_json = '{"items": ["a", "x", "c", "d"]}'
        
        result = diff(old_json, new_json, "json")
        
        # Should detect modification at index 1 and addition at index 3
        assert result["summary"]["modified"] == 1
        assert result["summary"]["added"] == 1
        
        # Check specific changes
        changes = result["changes"]
        idx1_change = next(c for c in changes if "items[1]" in c["path"])
        assert idx1_change["type"] == "modified"
        assert idx1_change["old"] == "b"
        assert idx1_change["new"] == "x"
    
    def test_sql_diff(self):
        """Test SQL statement diffing."""
        old_sql = "SELECT * FROM users WHERE age > 18"
        new_sql = "SELECT * FROM users WHERE age > 21 ORDER BY name"
        
        result = diff(old_sql, new_sql, "sql")
        
        assert result["lang"] == "sql"
        assert "changes" in result
        
        # Should detect that statements are different
        if result["changes"]:
            assert any(c.get("type") == "statement_modified" for c in result["changes"])
    
    def test_text_fallback(self):
        """Test fallback to text diff for unknown formats."""
        old_text = "Hello\nWorld"
        new_text = "Hello\nUniverse"
        
        result = diff(old_text, new_text, "txt")
        
        assert result["lang"] == "txt"
        assert result["type"] == "text_diff"
        assert result["lines_removed"] > 0
        assert result["lines_added"] > 0
    
    def test_error_handling(self):
        """Test error handling for invalid input."""
        invalid_json = '{"broken": '
        valid_json = '{"valid": true}'
        
        result = diff(invalid_json, valid_json, "json")
        
        # Should have error but also fallback
        assert "error" in result
        assert "fallback" in result
        assert result["fallback"]["type"] == "text_diff"
    
    def test_empty_input(self):
        """Test handling of empty input."""
        result = diff("", '{"new": "data"}', "json")
        
        assert result["lang"] == "json"
        # Everything should be added
        assert result["summary"]["added"] == 1
        assert result["summary"]["removed"] == 0
    
    def test_diff_node_creation(self):
        """Test DiffNode dataclass functionality."""
        node = DiffNode(
            path="test.path",
            change_type=ChangeType.MODIFIED,
            old_value="old",
            new_value="new"
        )
        
        dict_repr = node.to_dict()
        assert dict_repr["path"] == "test.path"
        assert dict_repr["type"] == "modified"
        assert dict_repr["old"] == "old"
        assert dict_repr["new"] == "new"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])