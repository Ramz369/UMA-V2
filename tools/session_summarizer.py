"""Session Summarizer - Generates canonical YAML summaries for agent coordination."""
import json
import hashlib
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time

# Try to import tools that might not be installed yet
try:
    from tools.credit_sentinel_v2 import get_sentinel
    HAS_SENTINEL = True
except ImportError:
    HAS_SENTINEL = False

try:
    from tools.github_client import GitHubClient
    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False


TOOLING_VERSION = "uma-tooling-v0.7.0"
GLOBAL_CREDIT_CAP = 1000


class SessionSummarizer:
    """Generates and validates session summaries."""
    
    def __init__(self, summary_path: Optional[str] = None, schema_path: Optional[str] = None):
        self.summary_path = Path(summary_path) if summary_path else Path("schemas/session_summary.yaml")
        self.schema_path = Path(schema_path) if schema_path else Path("schemas/session_summary.schema.json")
        self.session_counter = self._get_next_session_number()
    
    def _get_next_session_number(self) -> int:
        """Get next session number for today."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Check existing summary for today's sessions
        if self.summary_path.exists():
            try:
                with open(self.summary_path, 'r') as f:
                    existing = yaml.safe_load(f)
                    if existing and 'session_id' in existing:
                        session_id = existing['session_id']
                        if today in session_id:
                            # Extract sequence number
                            seq = int(session_id.split('-')[-1])
                            return seq + 1
            except:
                pass
        
        return 1
    
    def _get_git_info(self) -> Dict[str, Any]:
        """Get current git repository state."""
        repo_info = {
            "main_sha": "",
            "branch": "main",
            "dirty": False,
            "open_prs": []
        }
        
        try:
            # Get HEAD SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                repo_info["main_sha"] = result.stdout.strip()
            
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                repo_info["branch"] = result.stdout.strip()
            
            # Check for dirty state
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                repo_info["dirty"] = bool(result.stdout.strip())
        
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        # Get open PRs if GitHub client available
        if HAS_GITHUB:
            try:
                client = GitHubClient()
                prs = client.list_prs(state="open")
                repo_info["open_prs"] = [
                    {
                        "number": pr.number,
                        "title": pr.title,
                        "head": pr.head,
                        "url": pr.url
                    }
                    for pr in prs[:10]  # Limit to 10 most recent
                ]
            except:
                pass
        
        return repo_info
    
    def _get_credit_metrics(self) -> Dict[str, Any]:
        """Get credit metrics from Credit Sentinel."""
        credits = {
            "used": 0,
            "remaining": GLOBAL_CREDIT_CAP,
            "checkpoint_saved": None,
            "max_per_agent": {}
        }
        
        if HAS_SENTINEL:
            try:
                sentinel = get_sentinel()
                metrics = sentinel.get_metrics()
                
                # Global metrics
                credits["used"] = metrics["global"]["total_credits"]
                credits["remaining"] = GLOBAL_CREDIT_CAP - credits["used"]
                
                # Per-agent high-water marks
                for agent_name, agent_metrics in metrics.get("agents", {}).items():
                    credits["max_per_agent"][agent_name] = agent_metrics.get("credits_used", 0)
                
                # Last checkpoint time (from any agent)
                for agent_name, agent_metrics in sentinel.agent_metrics.items():
                    if agent_metrics.last_checkpoint:
                        checkpoint_time = agent_metrics.last_checkpoint.isoformat()
                        if not credits["checkpoint_saved"] or checkpoint_time > credits["checkpoint_saved"]:
                            credits["checkpoint_saved"] = checkpoint_time
            except:
                pass
        
        return credits
    
    def _get_agent_states(self) -> Dict[str, Any]:
        """Get current agent states."""
        agents = {
            "active": {},
            "idle": {},
            "aborted": []
        }
        
        if HAS_SENTINEL:
            try:
                sentinel = get_sentinel()
                
                for agent_name, metrics in sentinel.agent_metrics.items():
                    if metrics.status == "aborted":
                        agents["aborted"].append(agent_name)
                    elif metrics.status == "active":
                        agents["active"][agent_name] = {
                            "credits": metrics.credits_used,
                            "wall_time_ms": metrics.wall_time_ms,
                            "last_action": "tool_call"  # Default, could be enhanced
                        }
                    else:
                        # Idle
                        last_active = metrics.start_time.isoformat() if metrics.start_time else datetime.now(timezone.utc).isoformat()
                        agents["idle"][agent_name] = {
                            "credits": metrics.credits_used,
                            "last_active": last_active
                        }
            except:
                pass
        
        return agents
    
    def _get_lock_states(self) -> Dict[str, Any]:
        """Get current file lock states."""
        locks = {
            "held": {},
            "waiting": {}
        }
        
        if HAS_SENTINEL:
            try:
                sentinel = get_sentinel()
                
                # Current locks
                for file_path, (holder, _) in sentinel.locks.items():
                    locks["held"][file_path] = holder
                
                # No direct API for waiting locks in current implementation
                # Could be enhanced later
            except:
                pass
        
        return locks
    
    def _get_next_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks from todo list or defaults."""
        # Default roadmap tasks if no other source
        return [
            {"id": "4", "task": "Set up nightly meta-analyst GitHub Action", "status": "pending"},
            {"id": "5", "task": "Run PILOT-001 end-to-end test", "status": "pending"},
            {"id": "6", "task": "Create README with architecture diagram", "status": "pending"}
        ]
    
    def _generate_warnings(self, credits_used: int, agents: Dict) -> List[Dict[str, str]]:
        """Generate warnings based on current state."""
        warnings = []
        
        # Credit usage warnings
        usage_pct = (credits_used / GLOBAL_CREDIT_CAP) * 100
        if usage_pct >= 90:
            warnings.append({
                "level": "error",
                "msg": f"Credit usage critical: {usage_pct:.1f}%",
                "code": "credit_limit"
            })
        elif usage_pct >= 80:
            warnings.append({
                "level": "warn",
                "msg": f"Credit usage high: {usage_pct:.1f}%",
                "code": "credit_high"
            })
        
        # Aborted agents warning
        if agents.get("aborted"):
            warnings.append({
                "level": "error",
                "msg": f"Agents aborted: {', '.join(agents['aborted'])}",
                "code": "agent_aborted"
            })
        
        return warnings
    
    def _compute_context_hash(self, summary: Dict[str, Any]) -> str:
        """Compute SHA256 hash of canonical fields."""
        # Create a copy without the hash field itself
        canonical = summary.copy()
        canonical.pop("context_hash", None)
        canonical.pop("extensions", None)  # Extensions don't affect hash
        
        # Sort keys for reproducibility
        canonical_json = json.dumps(canonical, sort_keys=True, default=str)
        
        # Compute SHA256
        hash_obj = hashlib.sha256(canonical_json.encode('utf-8'))
        return f"sha256:{hash_obj.hexdigest()}"
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate complete session summary."""
        now = datetime.now(timezone.utc)
        session_date = now.strftime("%Y-%m-%d")
        
        # Get git info for build_id
        git_info = self._get_git_info()
        short_sha = git_info["main_sha"][:7] if git_info["main_sha"] else "0000000"
        
        # Build the summary
        summary = {
            "version": "1.0",
            "timestamp": now.isoformat(),
            "session_id": f"uma-v2-{session_date}-{self.session_counter:03d}",
            "build_id": f"{short_sha}-{int(time.time())}",
            "tooling_version": TOOLING_VERSION,
            "repo": git_info,
            "credits": self._get_credit_metrics(),
            "agents": self._get_agent_states(),
            "locks": self._get_lock_states(),
            "next_tasks": self._get_next_tasks(),
            "warnings": [],
            "extensions": {},
            "context_hash": ""
        }
        
        # Add warnings
        summary["warnings"] = self._generate_warnings(
            summary["credits"]["used"],
            summary["agents"]
        )
        
        # Add git dirty warning if applicable
        if git_info["dirty"]:
            summary["warnings"].append({
                "level": "warn",
                "msg": "Working tree has uncommitted changes",
                "code": "git_dirty"
            })
        
        # Validate arithmetic: remaining = cap - used
        expected_remaining = GLOBAL_CREDIT_CAP - summary["credits"]["used"]
        if summary["credits"]["remaining"] != expected_remaining:
            summary["credits"]["remaining"] = expected_remaining
            summary["warnings"].append({
                "level": "info",
                "msg": f"Corrected credit arithmetic: {expected_remaining} remaining"
            })
        
        # Compute context hash
        summary["context_hash"] = self._compute_context_hash(summary)
        
        return summary
    
    def validate_schema(self, summary: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate summary against JSON schema."""
        errors = []
        
        # Load schema if available
        if not self.schema_path.exists():
            return True, ["Schema file not found, skipping validation"]
        
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)
            
            # Basic validation without jsonschema library
            # Check required fields
            required = schema.get("required", [])
            for field in required:
                if field not in summary:
                    errors.append(f"Missing required field: {field}")
            
            # Validate version
            if summary.get("version") != "1.0":
                errors.append("Invalid version, expected '1.0'")
            
            # Validate context hash format
            context_hash = summary.get("context_hash", "")
            if not context_hash.startswith("sha256:") or len(context_hash) != 71:
                errors.append("Invalid context_hash format")
            
            # Validate credit arithmetic
            if "credits" in summary:
                used = summary["credits"].get("used", 0)
                remaining = summary["credits"].get("remaining", 0)
                if used + remaining != GLOBAL_CREDIT_CAP:
                    errors.append(f"Credit arithmetic mismatch: {used} + {remaining} != {GLOBAL_CREDIT_CAP}")
            
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def save_summary(self, summary: Dict[str, Any]) -> bool:
        """Save summary to YAML file."""
        try:
            # Ensure directory exists
            self.summary_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write YAML
            with open(self.summary_path, 'w') as f:
                yaml.dump(summary, f, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            print(f"Failed to save summary: {e}")
            return False
    
    def load_summary(self) -> Optional[Dict[str, Any]]:
        """Load existing summary."""
        if not self.summary_path.exists():
            return None
        
        try:
            with open(self.summary_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return None


def generate_session_summary() -> Dict[str, Any]:
    """Convenience function to generate summary."""
    summarizer = SessionSummarizer()
    return summarizer.generate_summary()


def save_session_summary(summary: Optional[Dict[str, Any]] = None) -> bool:
    """Convenience function to generate and save summary."""
    summarizer = SessionSummarizer()
    
    if summary is None:
        summary = summarizer.generate_summary()
    
    # Validate before saving
    valid, errors = summarizer.validate_schema(summary)
    if not valid:
        print(f"Validation errors: {errors}")
        return False
    
    return summarizer.save_summary(summary)


if __name__ == "__main__":
    # CLI interface
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        # Validate existing summary
        summarizer = SessionSummarizer()
        summary = summarizer.load_summary()
        if summary:
            valid, errors = summarizer.validate_schema(summary)
            if valid:
                print("✅ Summary is valid")
            else:
                print("❌ Validation errors:")
                for error in errors:
                    print(f"  - {error}")
            sys.exit(0 if valid else 1)
        else:
            print("No summary found")
            sys.exit(1)
    else:
        # Generate and save new summary
        if save_session_summary():
            print("✅ Session summary saved")
        else:
            print("❌ Failed to save summary")
            sys.exit(1)