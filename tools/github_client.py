"""GitHub Client - Wrapper for GitHub API operations via gh CLI."""
import subprocess
import json
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class MergeMethod(Enum):
    """GitHub merge methods."""
    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass
class PullRequest:
    """Pull request data."""
    number: int
    title: str
    state: str
    head: str
    base: str
    url: str
    mergeable: bool = True
    draft: bool = False


@dataclass
class CIStatus:
    """CI check status."""
    all_passing: bool
    checks: Dict[str, str]
    conclusion: str
    failed_checks: List[str]


class GitHubClient:
    """Client for GitHub operations using gh CLI."""
    
    def __init__(self, repo: Optional[str] = None, token: Optional[str] = None):
        """Initialize GitHub client.
        
        Args:
            repo: Repository in format owner/repo (auto-detected if None)
            token: GitHub token (uses GH_TOKEN env var if None)
        """
        self.repo = repo or self._detect_repo()
        self.token = token or os.environ.get("GH_TOKEN", "")
        self._retry_delays = [1, 2, 4, 8]  # Exponential backoff
    
    def _detect_repo(self) -> str:
        """Detect current repository from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            url = result.stdout.strip()
            # Extract owner/repo from URL
            if "github.com" in url:
                parts = url.split("github.com")[-1].strip(":/")
                if parts.endswith(".git"):
                    parts = parts[:-4]
                return parts.strip("/")
        except subprocess.CalledProcessError:
            pass
        return ""
    
    def _run_gh(self, args: List[str], retries: int = 0) -> Tuple[bool, str, str]:
        """Run gh CLI command with retries.
        
        Returns:
            (success, stdout, stderr)
        """
        if self.token:
            env = os.environ.copy()
            env["GH_TOKEN"] = self.token
        else:
            env = os.environ
        
        for attempt in range(retries + 1):
            try:
                result = subprocess.run(
                    ["gh"] + args,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return True, result.stdout, result.stderr
                
                # Check for rate limiting
                if "rate limit" in result.stderr.lower() and attempt < retries:
                    time.sleep(self._retry_delays[min(attempt, len(self._retry_delays)-1)])
                    continue
                
                return False, result.stdout, result.stderr
                
            except subprocess.TimeoutExpired:
                if attempt < retries:
                    continue
                return False, "", "Command timeout"
            except FileNotFoundError:
                return False, "", "gh CLI not found - install GitHub CLI"
        
        return False, "", "Max retries exceeded"
    
    def create_pr(self, head: str, base: str = "main", 
                  title: str = "", body: str = "",
                  draft: bool = False, labels: List[str] = None) -> Optional[PullRequest]:
        """Create a pull request.
        
        Args:
            head: Source branch
            base: Target branch
            title: PR title (auto-generated if empty)
            body: PR description
            draft: Create as draft PR
            labels: Labels to add
            
        Returns:
            PullRequest object or None if failed
        """
        args = ["pr", "create",
                "--head", head,
                "--base", base]
        
        if title:
            args.extend(["--title", title])
        else:
            args.append("--fill")  # Auto-generate from commits
        
        if body:
            args.extend(["--body", body])
        
        if draft:
            args.append("--draft")
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        success, stdout, stderr = self._run_gh(args, retries=2)
        
        if not success:
            print(f"Failed to create PR: {stderr}")
            return None
        
        # Extract PR number from output
        pr_url = stdout.strip()
        pr_number = int(pr_url.split("/")[-1])
        
        # Add labels if specified
        if labels:
            self.label_pr(pr_number, labels)
        
        # Get PR details
        return self.get_pr(pr_number)
    
    def get_pr(self, pr_number: int) -> Optional[PullRequest]:
        """Get PR details."""
        args = ["pr", "view", str(pr_number), "--json",
                "number,title,state,headRefName,baseRefName,url,mergeable,isDraft"]
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        success, stdout, stderr = self._run_gh(args)
        
        if not success:
            return None
        
        data = json.loads(stdout)
        return PullRequest(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            head=data["headRefName"],
            base=data["baseRefName"],
            url=data["url"],
            mergeable=data.get("mergeable", True),
            draft=data.get("isDraft", False)
        )
    
    def merge_pr(self, pr_number: int, method: MergeMethod = MergeMethod.SQUASH,
                 delete_branch: bool = True) -> bool:
        """Merge a pull request.
        
        Args:
            pr_number: PR number to merge
            method: Merge method (squash, merge, rebase)
            delete_branch: Delete source branch after merge
            
        Returns:
            True if merged successfully
        """
        args = ["pr", "merge", str(pr_number),
                f"--{method.value}"]
        
        if delete_branch:
            args.append("--delete-branch")
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        # Add auto confirmation
        args.append("--yes")
        
        success, stdout, stderr = self._run_gh(args, retries=1)
        
        if not success:
            print(f"Failed to merge PR {pr_number}: {stderr}")
        
        return success
    
    def label_pr(self, pr_number: int, labels: List[str]) -> bool:
        """Add labels to a pull request."""
        if not labels:
            return True
        
        args = ["pr", "edit", str(pr_number),
                "--add-label", ",".join(labels)]
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        success, _, stderr = self._run_gh(args)
        
        if not success:
            print(f"Failed to label PR {pr_number}: {stderr}")
        
        return success
    
    def get_ci_status(self, pr_number: int) -> CIStatus:
        """Get CI check status for a PR.
        
        Returns:
            CIStatus with check details
        """
        args = ["pr", "checks", str(pr_number), "--json",
                "name,status,conclusion"]
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        success, stdout, stderr = self._run_gh(args, retries=1)
        
        if not success:
            return CIStatus(
                all_passing=False,
                checks={},
                conclusion="ERROR",
                failed_checks=["Failed to get status"]
            )
        
        checks_data = json.loads(stdout) if stdout else []
        
        checks = {}
        failed = []
        all_complete = True
        all_passing = True
        
        for check in checks_data:
            name = check.get("name", "unknown")
            status = check.get("status", "pending")
            conclusion = check.get("conclusion", "")
            
            checks[name] = conclusion or status
            
            if status != "completed":
                all_complete = False
                all_passing = False
            elif conclusion not in ["success", "skipped", "neutral"]:
                all_passing = False
                failed.append(name)
        
        overall_conclusion = "success" if (all_complete and all_passing) else \
                           "pending" if not all_complete else "failure"
        
        return CIStatus(
            all_passing=all_passing and all_complete,
            checks=checks,
            conclusion=overall_conclusion,
            failed_checks=failed
        )
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """Delete a branch.
        
        Args:
            branch_name: Branch to delete
            force: Force deletion even if not merged
            
        Returns:
            True if deleted successfully
        """
        # First try remote deletion via gh
        args = ["api", f"repos/{self.repo}/git/refs/heads/{branch_name}",
                "--method", "DELETE"]
        
        success, _, _ = self._run_gh(args)
        
        # Also delete local branch if it exists
        local_args = ["git", "branch", "-D" if force else "-d", branch_name]
        subprocess.run(local_args, capture_output=True)
        
        return success
    
    def comment_pr(self, pr_number: int, comment: str) -> bool:
        """Add a comment to a PR."""
        args = ["pr", "comment", str(pr_number),
                "--body", comment]
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        success, _, stderr = self._run_gh(args)
        
        if not success:
            print(f"Failed to comment on PR {pr_number}: {stderr}")
        
        return success
    
    def list_prs(self, state: str = "open", labels: List[str] = None) -> List[PullRequest]:
        """List pull requests.
        
        Args:
            state: PR state (open, closed, merged, all)
            labels: Filter by labels
            
        Returns:
            List of PullRequest objects
        """
        args = ["pr", "list", "--state", state, "--json",
                "number,title,state,headRefName,baseRefName,url,isDraft"]
        
        if labels:
            args.extend(["--label", ",".join(labels)])
        
        if self.repo:
            args.extend(["--repo", self.repo])
        
        success, stdout, stderr = self._run_gh(args)
        
        if not success:
            print(f"Failed to list PRs: {stderr}")
            return []
        
        pr_list = json.loads(stdout) if stdout else []
        
        return [
            PullRequest(
                number=pr["number"],
                title=pr["title"],
                state=pr["state"],
                head=pr["headRefName"],
                base=pr["baseRefName"],
                url=pr["url"],
                draft=pr.get("isDraft", False)
            )
            for pr in pr_list
        ]


if __name__ == "__main__":
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python github_client.py <command> [args]")
        print("Commands:")
        print("  create <head> <base> <title>")
        print("  merge <pr_number>")
        print("  status <pr_number>")
        print("  list [state]")
        sys.exit(1)
    
    client = GitHubClient()
    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) >= 5:
        pr = client.create_pr(
            head=sys.argv[2],
            base=sys.argv[3],
            title=sys.argv[4]
        )
        if pr:
            print(f"Created PR #{pr.number}: {pr.url}")
    
    elif command == "merge" and len(sys.argv) >= 3:
        pr_num = int(sys.argv[2])
        if client.merge_pr(pr_num):
            print(f"Merged PR #{pr_num}")
    
    elif command == "status" and len(sys.argv) >= 3:
        pr_num = int(sys.argv[2])
        status = client.get_ci_status(pr_num)
        print(f"CI Status: {status.conclusion}")
        print(f"All passing: {status.all_passing}")
        if status.failed_checks:
            print(f"Failed: {', '.join(status.failed_checks)}")
    
    elif command == "list":
        state = sys.argv[2] if len(sys.argv) > 2 else "open"
        prs = client.list_prs(state)
        for pr in prs:
            print(f"#{pr.number}: {pr.title} ({pr.state})")
    
    else:
        print("Invalid command or arguments")
        sys.exit(1)