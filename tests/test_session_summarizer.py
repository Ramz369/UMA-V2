"""Unit tests for session summarizer and context validator."""
import pytest
import json
import yaml
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.session_summarizer import SessionSummarizer, GLOBAL_CREDIT_CAP
from tools.context_validator import ContextValidator


class TestSessionSummarizer:
    """Test suite for session summarizer."""
    
    @pytest.fixture
    def temp_paths(self):
        """Create temporary file paths."""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as summary_file:
            summary_path = Path(summary_file.name)
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as schema_file:
            schema_path = Path(schema_file.name)
        
        yield summary_path, schema_path
        
        # Cleanup
        if summary_path.exists():
            summary_path.unlink()
        if schema_path.exists():
            schema_path.unlink()
    
    @pytest.fixture
    def summarizer(self, temp_paths):
        """Create test summarizer."""
        summary_path, schema_path = temp_paths
        return SessionSummarizer(summary_path=str(summary_path), schema_path=str(schema_path))
    
    def test_session_number_generation(self, summarizer):
        """Test session number increments correctly."""
        # First session of the day
        assert summarizer.session_counter == 1
        
        # Save a summary
        summary = summarizer.generate_summary()
        summarizer.save_summary(summary)
        
        # Create new summarizer - should increment
        summarizer2 = SessionSummarizer(summary_path=summarizer.summary_path)
        assert summarizer2.session_counter == 2
    
    @patch('subprocess.run')
    def test_git_info_collection(self, mock_run, summarizer):
        """Test git information collection."""
        # Mock git commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="abc123def456789012345678901234567890abc\n"),  # HEAD
            Mock(returncode=0, stdout="feature/test-branch\n"),  # branch
            Mock(returncode=0, stdout="M tools/test.py\n")  # dirty status
        ]
        
        git_info = summarizer._get_git_info()
        
        assert git_info["main_sha"] == "abc123def456789012345678901234567890abc"
        assert git_info["branch"] == "feature/test-branch"
        assert git_info["dirty"] is True
    
    def test_summary_generation(self, summarizer):
        """Test complete summary generation."""
        with patch.object(summarizer, '_get_git_info') as mock_git:
            mock_git.return_value = {
                "main_sha": "a" * 40,
                "branch": "main",
                "dirty": False,
                "open_prs": []
            }
            
            summary = summarizer.generate_summary()
        
        # Check required fields
        assert summary["version"] == "1.0"
        assert "timestamp" in summary
        assert "session_id" in summary
        assert "build_id" in summary
        assert summary["tooling_version"] == "uma-tooling-v0.7.0"
        assert "context_hash" in summary
        
        # Check structure
        assert "credits" in summary
        assert "agents" in summary
        assert "locks" in summary
        assert "next_tasks" in summary
        assert "warnings" in summary
        assert "extensions" in summary
    
    def test_context_hash_reproducibility(self, summarizer):
        """Test context hash is reproducible."""
        summary1 = {
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "credits": {"used": 100, "remaining": 900}
        }
        
        hash1 = summarizer._compute_context_hash(summary1)
        hash2 = summarizer._compute_context_hash(summary1)
        
        assert hash1 == hash2
        assert hash1.startswith("sha256:")
        assert len(hash1) == 71  # "sha256:" + 64 hex chars
    
    def test_credit_arithmetic_validation(self, summarizer):
        """Test credit remaining calculation."""
        summary = summarizer.generate_summary()
        
        # Credits should add up to cap
        used = summary["credits"]["used"]
        remaining = summary["credits"]["remaining"]
        
        assert used + remaining == GLOBAL_CREDIT_CAP
    
    def test_warning_generation(self, summarizer):
        """Test warning generation for high credit usage."""
        # Test high credit warning
        warnings = summarizer._generate_warnings(850, {"aborted": []})
        
        assert len(warnings) == 1
        assert warnings[0]["level"] == "warn"
        assert "credit_high" in warnings[0].get("code", "")
        
        # Test critical credit warning
        warnings = summarizer._generate_warnings(950, {"aborted": []})
        
        assert len(warnings) == 1
        assert warnings[0]["level"] == "error"
        assert "credit_limit" in warnings[0].get("code", "")
        
        # Test aborted agent warning
        warnings = summarizer._generate_warnings(100, {"aborted": ["test-agent"]})
        
        assert any(w["code"] == "agent_aborted" for w in warnings)
    
    def test_schema_validation(self, summarizer):
        """Test schema validation logic."""
        summary = summarizer.generate_summary()
        
        # Should pass with valid summary
        valid, errors = summarizer.validate_schema(summary)
        assert valid or "Schema file not found" in errors[0]
        
        # Test with invalid summary
        bad_summary = summary.copy()
        bad_summary["version"] = "2.0"  # Wrong version
        
        valid, errors = summarizer.validate_schema(bad_summary)
        assert not valid
        assert any("version" in e.lower() for e in errors)
    
    def test_save_and_load(self, summarizer):
        """Test saving and loading summary."""
        original = summarizer.generate_summary()
        
        # Save
        assert summarizer.save_summary(original)
        assert summarizer.summary_path.exists()
        
        # Load
        loaded = summarizer.load_summary()
        
        assert loaded is not None
        assert loaded["version"] == original["version"]
        assert loaded["session_id"] == original["session_id"]
        assert loaded["context_hash"] == original["context_hash"]


class TestContextValidator:
    """Test suite for context validator."""
    
    @pytest.fixture
    def temp_summary(self):
        """Create temporary summary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            summary = {
                "version": "1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": "uma-v2-2024-01-01-001",
                "build_id": "abc1234-1234567890",
                "tooling_version": "uma-tooling-v0.7.0",
                "repo": {
                    "main_sha": "a" * 40,
                    "branch": "main",
                    "dirty": False,
                    "open_prs": []
                },
                "credits": {
                    "used": 100,
                    "remaining": 900,
                    "checkpoint_saved": None,
                    "max_per_agent": {}
                },
                "agents": {"active": {}, "idle": {}, "aborted": []},
                "locks": {"held": {}, "waiting": {}},
                "next_tasks": [],
                "warnings": [],
                "extensions": {},
                "context_hash": ""
            }
            
            # Compute hash
            import hashlib
            canonical_json = json.dumps(summary, sort_keys=True, default=str)
            hash_value = f"sha256:{hashlib.sha256(canonical_json.encode()).hexdigest()}"
            summary["context_hash"] = hash_value
            
            yaml.dump(summary, f)
            temp_path = Path(f.name)
        
        yield temp_path
        
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def validator(self, temp_summary):
        """Create test validator."""
        return ContextValidator(summary_path=str(temp_summary))
    
    @patch('subprocess.run')
    def test_validate_matching_context(self, mock_run, validator):
        """Test validation with matching context."""
        # Mock git commands to match summary
        mock_run.side_effect = [
            Mock(returncode=0, stdout="a" * 40 + "\n"),  # HEAD
            Mock(returncode=0, stdout="main\n")  # branch
        ]
        
        is_valid, message, context = validator.validate_context()
        
        assert is_valid
        assert "valid" in message.lower()
        assert context["version"] == "1.0"
    
    @patch('subprocess.run')
    def test_validate_changed_sha(self, mock_run, validator):
        """Test validation detects SHA change."""
        # Mock different SHA
        mock_run.side_effect = [
            Mock(returncode=0, stdout="b" * 40 + "\n"),  # Different HEAD
            Mock(returncode=0, stdout="main\n")
        ]
        
        is_valid, message, context = validator.validate_context()
        
        assert not is_valid
        assert "Git HEAD changed" in message
    
    @patch('subprocess.run')
    def test_validate_changed_branch(self, mock_run, validator):
        """Test validation detects branch change."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="a" * 40 + "\n"),  # Same HEAD
            Mock(returncode=0, stdout="feature/different\n")  # Different branch
        ]
        
        is_valid, message, context = validator.validate_context()
        
        assert not is_valid
        assert "Branch changed" in message
    
    def test_validate_stale_summary(self, temp_summary):
        """Test validation detects stale summary."""
        # Modify summary to be old
        with open(temp_summary, 'r') as f:
            summary = yaml.safe_load(f)
        
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        summary["timestamp"] = old_time.isoformat()
        
        # Recompute hash
        import hashlib
        summary_copy = summary.copy()
        summary_copy.pop("context_hash", None)
        canonical_json = json.dumps(summary_copy, sort_keys=True, default=str)
        summary["context_hash"] = f"sha256:{hashlib.sha256(canonical_json.encode()).hexdigest()}"
        
        with open(temp_summary, 'w') as f:
            yaml.dump(summary, f)
        
        validator = ContextValidator(summary_path=str(temp_summary))
        validator.max_staleness_seconds = 3600  # 1 hour
        
        is_valid, message, context = validator.validate_context()
        
        assert not is_valid
        assert "hours old" in message
    
    def test_validate_credit_limit(self, temp_summary):
        """Test validation detects credit exhaustion."""
        # Modify summary to have high credit usage
        with open(temp_summary, 'r') as f:
            summary = yaml.safe_load(f)
        
        summary["credits"]["used"] = 960
        summary["credits"]["remaining"] = 40
        
        # Recompute hash
        import hashlib
        summary_copy = summary.copy()
        summary_copy.pop("context_hash", None)
        canonical_json = json.dumps(summary_copy, sort_keys=True, default=str)
        summary["context_hash"] = f"sha256:{hashlib.sha256(canonical_json.encode()).hexdigest()}"
        
        with open(temp_summary, 'w') as f:
            yaml.dump(summary, f)
        
        validator = ContextValidator(summary_path=str(temp_summary))
        
        is_valid, message, context = validator.validate_context()
        
        assert not is_valid
        assert "Credit limit" in message
    
    def test_require_valid_context(self, validator):
        """Test require_valid_context raises on invalid."""
        with patch.object(validator, 'validate_context') as mock_validate:
            mock_validate.return_value = (False, "Test failure", {})
            
            with pytest.raises(RuntimeError) as exc_info:
                validator.require_valid_context("test-agent")
            
            assert "Context validation failed" in str(exc_info.value)
    
    def test_get_safe_context(self, validator):
        """Test safe context generation."""
        with patch.object(validator, 'validate_context') as mock_validate:
            # First call fails
            mock_validate.return_value = (False, "Invalid", {})
            
            with patch('tools.context_validator.HAS_SUMMARIZER', False):
                # Without summarizer, should return fallback
                context = validator.get_safe_context()
                
                assert context["version"] == "1.0"
                assert len(context["warnings"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])