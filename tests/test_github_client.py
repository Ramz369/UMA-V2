"""Unit tests for GitHub client."""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import subprocess
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.github_client import (
    GitHubClient, PullRequest, CIStatus, MergeMethod
)


class TestGitHubClient:
    """Test suite for GitHub client."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return GitHubClient(repo="test/repo")
    
    @pytest.fixture
    def mock_run(self):
        """Mock subprocess.run."""
        with patch('subprocess.run') as mock:
            yield mock
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = GitHubClient(repo="owner/repo", token="test-token")
        assert client.repo == "owner/repo"
        assert client.token == "test-token"
    
    def test_detect_repo(self, mock_run):
        """Test automatic repo detection."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="https://github.com/owner/repo.git\n",
            stderr=""
        )
        
        client = GitHubClient()
        assert client.repo == "owner/repo"
    
    def test_create_pr_success(self, client, mock_run):
        """Test successful PR creation."""
        # Mock gh pr create output
        mock_run.side_effect = [
            Mock(returncode=0, stdout="https://github.com/test/repo/pull/42\n", stderr=""),
            Mock(returncode=0, stdout=json.dumps({
                "number": 42,
                "title": "Test PR",
                "state": "OPEN",
                "headRefName": "feature/test",
                "baseRefName": "main",
                "url": "https://github.com/test/repo/pull/42",
                "mergeable": True,
                "isDraft": False
            }), stderr="")
        ]
        
        pr = client.create_pr(
            head="feature/test",
            base="main",
            title="Test PR",
            body="Test description"
        )
        
        assert pr is not None
        assert pr.number == 42
        assert pr.title == "Test PR"
        assert pr.head == "feature/test"
        assert pr.base == "main"
    
    def test_create_pr_with_labels(self, client, mock_run):
        """Test PR creation with labels."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="https://github.com/test/repo/pull/42\n", stderr=""),
            Mock(returncode=0, stdout="", stderr=""),  # label command
            Mock(returncode=0, stdout=json.dumps({
                "number": 42,
                "title": "Test PR",
                "state": "OPEN",
                "headRefName": "feature/test",
                "baseRefName": "main",
                "url": "https://github.com/test/repo/pull/42",
                "mergeable": True,
                "isDraft": False
            }), stderr="")
        ]
        
        pr = client.create_pr(
            head="feature/test",
            base="main",
            title="Test PR",
            labels=["enhancement", "auto-merge"]
        )
        
        assert pr is not None
        assert pr.number == 42
        
        # Verify label command was called
        label_call = mock_run.call_args_list[1]
        assert "--add-label" in label_call[0][0]
        assert "enhancement,auto-merge" in label_call[0][0]
    
    def test_create_pr_failure(self, client, mock_run):
        """Test PR creation failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: PR already exists"
        )
        
        pr = client.create_pr(head="feature/test", base="main")
        assert pr is None
    
    def test_get_ci_status_all_passing(self, client, mock_run):
        """Test CI status when all checks pass."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps([
                {"name": "boundary-check", "status": "completed", "conclusion": "success"},
                {"name": "sandbox-test", "status": "completed", "conclusion": "success"},
                {"name": "sentinel-test", "status": "completed", "conclusion": "success"}
            ]),
            stderr=""
        )
        
        status = client.get_ci_status(42)
        
        assert status.all_passing is True
        assert status.conclusion == "success"
        assert len(status.failed_checks) == 0
        assert status.checks["boundary-check"] == "success"
    
    def test_get_ci_status_with_failures(self, client, mock_run):
        """Test CI status with failing checks."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps([
                {"name": "boundary-check", "status": "completed", "conclusion": "success"},
                {"name": "sandbox-test", "status": "completed", "conclusion": "failure"},
                {"name": "sentinel-test", "status": "pending", "conclusion": ""}
            ]),
            stderr=""
        )
        
        status = client.get_ci_status(42)
        
        assert status.all_passing is False
        assert status.conclusion == "pending"  # Has pending checks
        assert "sandbox-test" in status.failed_checks
        assert status.checks["sentinel-test"] == "pending"
    
    def test_get_ci_status_error(self, client, mock_run):
        """Test CI status retrieval error."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: PR not found"
        )
        
        status = client.get_ci_status(42)
        
        assert status.all_passing is False
        assert status.conclusion == "ERROR"
        assert len(status.failed_checks) > 0
    
    def test_merge_pr_success(self, client, mock_run):
        """Test successful PR merge."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="✓ Merged pull request #42",
            stderr=""
        )
        
        result = client.merge_pr(42, method=MergeMethod.SQUASH, delete_branch=True)
        
        assert result is True
        
        # Verify correct arguments
        call_args = mock_run.call_args[0][0]
        assert "pr" in call_args
        assert "merge" in call_args
        assert "42" in call_args
        assert "--squash" in call_args
        assert "--delete-branch" in call_args
        assert "--yes" in call_args
    
    def test_merge_pr_failure(self, client, mock_run):
        """Test PR merge failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Merge conflict"
        )
        
        result = client.merge_pr(42)
        assert result is False
    
    def test_label_pr(self, client, mock_run):
        """Test adding labels to PR."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="✓ Added labels",
            stderr=""
        )
        
        result = client.label_pr(42, ["bug", "priority-high"])
        
        assert result is True
        
        call_args = mock_run.call_args[0][0]
        assert "pr" in call_args
        assert "edit" in call_args
        assert "--add-label" in call_args
        assert "bug,priority-high" in call_args
    
    def test_delete_branch(self, client, mock_run):
        """Test branch deletion."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # Remote delete
            Mock(returncode=0, stdout="", stderr="")   # Local delete
        ]
        
        result = client.delete_branch("feature/test")
        
        assert result is True
        
        # Check remote delete call
        remote_call = mock_run.call_args_list[0][0][0]
        assert "api" in remote_call
        assert "DELETE" in remote_call
    
    def test_comment_pr(self, client, mock_run):
        """Test adding comment to PR."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="✓ Comment added",
            stderr=""
        )
        
        result = client.comment_pr(42, "CI checks passed!")
        
        assert result is True
        
        call_args = mock_run.call_args[0][0]
        assert "pr" in call_args
        assert "comment" in call_args
        assert "42" in call_args
        assert "--body" in call_args
    
    def test_list_prs(self, client, mock_run):
        """Test listing PRs."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps([
                {
                    "number": 1,
                    "title": "First PR",
                    "state": "OPEN",
                    "headRefName": "feature/one",
                    "baseRefName": "main",
                    "url": "https://github.com/test/repo/pull/1",
                    "isDraft": False
                },
                {
                    "number": 2,
                    "title": "Second PR",
                    "state": "OPEN",
                    "headRefName": "feature/two",
                    "baseRefName": "main",
                    "url": "https://github.com/test/repo/pull/2",
                    "isDraft": True
                }
            ]),
            stderr=""
        )
        
        prs = client.list_prs(state="open")
        
        assert len(prs) == 2
        assert prs[0].number == 1
        assert prs[0].title == "First PR"
        assert prs[1].draft is True
    
    def test_retry_on_rate_limit(self, client, mock_run):
        """Test retry mechanism for rate limiting."""
        mock_run.side_effect = [
            Mock(returncode=1, stdout="", stderr="API rate limit exceeded"),
            Mock(returncode=0, stdout=json.dumps({"number": 42}), stderr="")
        ]
        
        with patch('time.sleep'):  # Speed up test
            success, stdout, _ = client._run_gh(["test"], retries=1)
        
        assert success is True
        assert mock_run.call_count == 2
    
    def test_timeout_handling(self, client, mock_run):
        """Test command timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["gh"], timeout=30)
        
        success, stdout, stderr = client._run_gh(["test"], retries=0)
        
        assert success is False
        assert "timeout" in stderr.lower()
    
    def test_gh_not_found(self, client, mock_run):
        """Test handling when gh CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        success, stdout, stderr = client._run_gh(["test"])
        
        assert success is False
        assert "gh CLI not found" in stderr
    
    def test_merge_method_enum(self):
        """Test MergeMethod enum values."""
        assert MergeMethod.MERGE.value == "merge"
        assert MergeMethod.SQUASH.value == "squash"
        assert MergeMethod.REBASE.value == "rebase"
    
    def test_pull_request_dataclass(self):
        """Test PullRequest dataclass."""
        pr = PullRequest(
            number=42,
            title="Test PR",
            state="OPEN",
            head="feature/test",
            base="main",
            url="https://github.com/test/repo/pull/42"
        )
        
        assert pr.number == 42
        assert pr.mergeable is True  # Default value
        assert pr.draft is False  # Default value
    
    def test_ci_status_dataclass(self):
        """Test CIStatus dataclass."""
        status = CIStatus(
            all_passing=True,
            checks={"test": "success"},
            conclusion="success",
            failed_checks=[]
        )
        
        assert status.all_passing is True
        assert status.checks["test"] == "success"
        assert len(status.failed_checks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])