
"""
@cognimap:fingerprint
id: e7779f26-2783-49d2-9d36-59aacc48ff6b
birth: 2025-08-07T07:23:38.060755Z
parent: None
intent: Context Validator - Pre-flight validation for agent startup.
semantic_tags: [testing, model, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.061295Z
hash: feec182a
language: python
type: tool
@end:cognimap
"""

"""Context Validator - Pre-flight validation for agent startup."""
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone

try:
    from tools.session_summarizer import SessionSummarizer
    HAS_SUMMARIZER = True
except ImportError:
    HAS_SUMMARIZER = False


class ContextValidator:
    """Validates session context before agent operations."""
    
    def __init__(self, summary_path: Optional[str] = None):
        self.summary_path = Path(summary_path) if summary_path else Path("schemas/session_summary.yaml")
        self.max_staleness_seconds = 3600  # 1 hour default
    
    def get_current_git_sha(self) -> str:
        """Get current git HEAD SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""
    
    def get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "main"
    
    def validate_context(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate current context against saved summary.
        
        Returns:
            (is_valid, message, context_data)
        """
        # Load summary
        if not HAS_SUMMARIZER:
            return True, "Session summarizer not available, skipping validation", {}
        
        summarizer = SessionSummarizer(self.summary_path)
        summary = summarizer.load_summary()
        
        if not summary:
            return False, "No session summary found - run session_summarizer first", {}
        
        # Check context hash integrity
        computed_hash = summarizer._compute_context_hash(summary)
        if computed_hash != summary.get("context_hash"):
            return False, f"Context hash mismatch - summary may be corrupted", summary
        
        # Check git SHA
        current_sha = self.get_current_git_sha()
        summary_sha = summary.get("repo", {}).get("main_sha", "")
        
        if current_sha and summary_sha and current_sha != summary_sha:
            return False, f"Git HEAD changed: {summary_sha[:7]} -> {current_sha[:7]}", summary
        
        # Check branch
        current_branch = self.get_current_branch()
        summary_branch = summary.get("repo", {}).get("branch", "main")
        
        if current_branch != summary_branch:
            return False, f"Branch changed: {summary_branch} -> {current_branch}", summary
        
        # Check staleness
        try:
            summary_time = datetime.fromisoformat(summary.get("timestamp", ""))
            if summary_time.tzinfo is None:
                summary_time = summary_time.replace(tzinfo=timezone.utc)
            
            age_seconds = (datetime.now(timezone.utc) - summary_time).total_seconds()
            
            if age_seconds > self.max_staleness_seconds:
                hours = age_seconds / 3600
                return False, f"Summary is {hours:.1f} hours old - regenerate with session_summarizer", summary
        except:
            pass
        
        # Check credit limits
        credits_used = summary.get("credits", {}).get("used", 0)
        if credits_used >= 950:  # 95% of 1000 cap
            return False, f"Credit limit nearly exhausted: {credits_used}/1000", summary
        
        # All checks passed
        return True, "Context valid", summary
    
    def require_valid_context(self, agent_name: str) -> Dict[str, Any]:
        """Validate context and abort if invalid.
        
        Args:
            agent_name: Name of agent requesting validation
            
        Returns:
            Valid context dictionary
            
        Raises:
            RuntimeError: If context is invalid
        """
        is_valid, message, context = self.validate_context()
        
        if not is_valid:
            error_msg = f"[{agent_name}] Context validation failed: {message}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        print(f"✅ [{agent_name}] Context validated: {message}")
        return context
    
    def get_safe_context(self) -> Dict[str, Any]:
        """Get context data, regenerating if stale.
        
        Returns:
            Valid context or newly generated summary
        """
        is_valid, message, context = self.validate_context()
        
        if is_valid:
            return context
        
        # Try to regenerate
        print(f"⚠️ {message}")
        print("Regenerating session summary...")
        
        if HAS_SUMMARIZER:
            summarizer = SessionSummarizer()
            new_summary = summarizer.generate_summary()
            
            if summarizer.save_summary(new_summary):
                print("✅ New summary generated")
                return new_summary
        
        # Fallback to empty context
        return {
            "version": "1.0",
            "credits": {"used": 0, "remaining": 1000},
            "agents": {"active": {}, "idle": {}, "aborted": []},
            "warnings": [{"level": "warn", "msg": "Operating without valid context"}]
        }


# Convenience functions for agent bootstrap
def validate_and_get_context(agent_name: str) -> Dict[str, Any]:
    """Standard validation for agent startup.
    
    Usage in agent:
        from tools.context_validator import validate_and_get_context
        context = validate_and_get_context("my-agent")
    """
    validator = ContextValidator()
    return validator.require_valid_context(agent_name)


def check_context_status() -> Tuple[bool, str]:
    """Quick check of context validity.
    
    Returns:
        (is_valid, message)
    """
    validator = ContextValidator()
    is_valid, message, _ = validator.validate_context()
    return is_valid, message


if __name__ == "__main__":
    # CLI interface for testing
    import sys
    
    validator = ContextValidator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            # Just check status
            is_valid, message = check_context_status()
            print(f"{'✅' if is_valid else '❌'} {message}")
            sys.exit(0 if is_valid else 1)
        
        elif sys.argv[1] == "require":
            # Require valid context (will abort if invalid)
            agent_name = sys.argv[2] if len(sys.argv) > 2 else "test-agent"
            try:
                context = validate_and_get_context(agent_name)
                print(f"Credits used: {context.get('credits', {}).get('used', 0)}")
            except RuntimeError as e:
                print(str(e))
                sys.exit(1)
        
        elif sys.argv[1] == "safe":
            # Get safe context (regenerate if needed)
            context = validator.get_safe_context()
            print(f"Session ID: {context.get('session_id', 'unknown')}")
    
    else:
        # Default: validate current context
        is_valid, message, context = validator.validate_context()
        
        if is_valid:
            print(f"✅ {message}")
            print(f"  Session: {context.get('session_id')}")
            print(f"  Credits: {context.get('credits', {}).get('used')}/{context.get('credits', {}).get('remaining')}")
            print(f"  Branch: {context.get('repo', {}).get('branch')}")
        else:
            print(f"❌ {message}")
            sys.exit(1)