
"""
@cognimap:fingerprint
id: a74b8f33-465b-47ae-ac98-87abba239dc4
birth: 2025-08-07T07:23:38.058544Z
parent: None
intent: Credit Sentinel v2 - Real-time token and wall-time throttling with metrics.
semantic_tags: [authentication, api, testing, model, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.059284Z
hash: ee97b767
language: python
type: tool
@end:cognimap
"""

"""Credit Sentinel v2 - Real-time token and wall-time throttling with metrics."""
import json
import time
import threading
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import csv
import yaml


class ThrottleAction(Enum):
    """Actions the sentinel can take."""
    ALLOW = "allow"
    WARN = "warn"
    CHECKPOINT = "checkpoint"
    THROTTLE = "throttle"
    ABORT = "abort"


@dataclass
class AgentMetrics:
    """Metrics for a single agent."""
    name: str
    credits_used: int = 0
    tokens_used: int = 0
    wall_time_ms: int = 0
    tool_calls: int = 0
    checkpoints: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    last_checkpoint: Optional[datetime] = None
    status: str = "active"


@dataclass
class GlobalMetrics:
    """Global system metrics."""
    total_credits: int = 0
    total_tokens: int = 0
    total_wall_time_ms: int = 0
    active_agents: int = 0
    throttled_agents: int = 0
    aborted_agents: int = 0
    total_tool_calls: int = 0


class CreditSentinel:
    """Real-time monitoring and throttling of agent credit/token usage."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/sentinel.yaml")
        self.metrics_path = Path("schemas/metrics_v2.csv")
        self.lock_graph_path = Path("config/lock_graph.yaml")
        
        self.config = self._load_config()
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.global_metrics = GlobalMetrics()
        self.locks: Dict[str, Tuple[str, datetime]] = {}  # file -> (agent, time)
        self._lock = threading.Lock()
        
        # Wall-time monitor thread
        self._monitor_thread = None
        self._running = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load sentinel configuration."""
        default_config = {
            "global_hard_cap": 1000,
            "checkpoint_interval": 50,
            "max_wall_time_ms": 120000,  # 2 minutes
            "agent_caps": {
                "planner": 50,
                "codegen": 150,
                "backend-tester": 200,
                "frontend-tester": 150,
                "tool-builder": 180,
                "credit-sentinel": 40,
                "meta-analyst-v2": 120
            },
            "wall_time_limits": {
                "default": 45000,  # 45 seconds
                "container_runner": 60000,  # 60 seconds
                "stress-tester": 120000  # 2 minutes
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    default_config.update(loaded)
        
        return default_config
    
    def start_monitoring(self):
        """Start the wall-time monitoring thread."""
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Background thread to check wall-time limits."""
        while self._running:
            with self._lock:
                now = datetime.now()
                for agent_name, metrics in self.agent_metrics.items():
                    if metrics.status != "active":
                        continue
                    
                    if metrics.start_time:
                        elapsed_ms = int((now - metrics.start_time).total_seconds() * 1000)
                        metrics.wall_time_ms = elapsed_ms
                        
                        # Check wall-time limit
                        limit = self.config["wall_time_limits"].get(
                            agent_name, 
                            self.config["wall_time_limits"]["default"]
                        )
                        
                        if elapsed_ms > limit:
                            self._abort_agent(agent_name, f"Wall-time limit exceeded: {elapsed_ms}ms > {limit}ms")
            
            time.sleep(1)  # Check every second
    
    def track_agent_start(self, agent_name: str) -> ThrottleAction:
        """Track when an agent starts."""
        with self._lock:
            if agent_name not in self.agent_metrics:
                self.agent_metrics[agent_name] = AgentMetrics(
                    name=agent_name,
                    start_time=datetime.now()
                )
                self.global_metrics.active_agents += 1
            
            # Check if agent should be allowed to start
            if self.global_metrics.total_credits >= self.config["global_hard_cap"]:
                return ThrottleAction.ABORT
            
            return ThrottleAction.ALLOW
    
    def track_tool_call(self, agent_name: str, tool_name: str, credits: int, tokens: int) -> ThrottleAction:
        """Track a tool call and determine throttle action."""
        with self._lock:
            if agent_name not in self.agent_metrics:
                self.track_agent_start(agent_name)
            
            metrics = self.agent_metrics[agent_name]
            metrics.credits_used += credits
            metrics.tokens_used += tokens
            metrics.tool_calls += 1
            
            self.global_metrics.total_credits += credits
            self.global_metrics.total_tokens += tokens
            self.global_metrics.total_tool_calls += 1
            
            # Check limits
            action = self._check_limits(agent_name, metrics)
            
            # Log to CSV
            self._log_to_csv(agent_name, tool_name, credits, tokens, action)
            
            # Handle checkpointing
            if action == ThrottleAction.CHECKPOINT:
                self._create_checkpoint(agent_name, metrics)
            elif action == ThrottleAction.ABORT:
                self._abort_agent(agent_name, "Credit limit exceeded")
            
            return action
    
    def _check_limits(self, agent_name: str, metrics: AgentMetrics) -> ThrottleAction:
        """Check if limits are exceeded."""
        # Global hard cap
        if self.global_metrics.total_credits >= self.config["global_hard_cap"]:
            return ThrottleAction.ABORT
        
        # Agent soft cap
        agent_cap = self.config["agent_caps"].get(agent_name, 200)
        
        if metrics.credits_used >= agent_cap:
            return ThrottleAction.ABORT
        elif metrics.credits_used >= agent_cap * 0.9:
            return ThrottleAction.THROTTLE
        elif metrics.credits_used >= agent_cap * 0.8:
            return ThrottleAction.WARN
        
        # Checkpoint interval
        checkpoint_interval = self.config["checkpoint_interval"]
        if metrics.credits_used > 0 and metrics.credits_used % checkpoint_interval == 0:
            return ThrottleAction.CHECKPOINT
        
        return ThrottleAction.ALLOW
    
    def _create_checkpoint(self, agent_name: str, metrics: AgentMetrics):
        """Create a checkpoint for an agent."""
        checkpoint = {
            "time": datetime.now().isoformat(),
            "credits": metrics.credits_used,
            "tokens": metrics.tokens_used,
            "wall_time_ms": metrics.wall_time_ms,
            "tool_calls": metrics.tool_calls
        }
        metrics.checkpoints.append(json.dumps(checkpoint))
        metrics.last_checkpoint = datetime.now()
    
    def _abort_agent(self, agent_name: str, reason: str):
        """Abort an agent."""
        if agent_name in self.agent_metrics:
            self.agent_metrics[agent_name].status = "aborted"
            self.global_metrics.active_agents -= 1
            self.global_metrics.aborted_agents += 1
            
            # Release any locks held by this agent
            self._release_agent_locks(agent_name)
            
            print(f"ABORT: Agent {agent_name} - {reason}")
    
    def _log_to_csv(self, agent_name: str, tool_name: str, credits: int, tokens: int, action: ThrottleAction):
        """Log metrics to CSV file."""
        # Ensure directory exists
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists to write header
        write_header = not self.metrics_path.exists()
        
        with open(self.metrics_path, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if write_header:
                writer.writerow([
                    "team_id", "timestamp", "agent", "tokens", "credits",
                    "wall_time_ms", "model", "tool_call", "exit_status"
                ])
            
            metrics = self.agent_metrics[agent_name]
            writer.writerow([
                "default",  # team_id
                datetime.now().isoformat(),
                agent_name,
                tokens,
                credits,
                metrics.wall_time_ms,
                "claude-3",  # model
                tool_name,
                action.value
            ])
    
    def acquire_lock(self, agent_name: str, file_path: str) -> bool:
        """Acquire a file lock for an agent."""
        with self._lock:
            if file_path in self.locks:
                holder, lock_time = self.locks[file_path]
                if holder != agent_name:
                    # Check for deadlock using lock graph
                    if self._detect_deadlock(agent_name, file_path):
                        self._resolve_deadlock(agent_name, file_path)
                    return False
            
            self.locks[file_path] = (agent_name, datetime.now())
            return True
    
    def release_lock(self, agent_name: str, file_path: str):
        """Release a file lock."""
        with self._lock:
            if file_path in self.locks and self.locks[file_path][0] == agent_name:
                del self.locks[file_path]
    
    def _release_agent_locks(self, agent_name: str):
        """Release all locks held by an agent."""
        to_release = [f for f, (holder, _) in self.locks.items() if holder == agent_name]
        for file_path in to_release:
            del self.locks[file_path]
    
    def _detect_deadlock(self, requesting_agent: str, requested_file: str) -> bool:
        """Detect if acquiring this lock would cause a deadlock."""
        # Simple cycle detection in lock graph
        visited = set()
        
        def has_cycle(agent, path):
            if agent in path:
                return True
            if agent in visited:
                return False
            
            visited.add(agent)
            
            # Find what this agent is waiting for
            for file, (holder, _) in self.locks.items():
                if holder == agent:
                    # This agent holds this file
                    # Check who wants it
                    for other_file, (other_holder, _) in self.locks.items():
                        if other_holder != agent and other_file == file:
                            if has_cycle(other_holder, path | {agent}):
                                return True
            
            return False
        
        current_holder = self.locks.get(requested_file, (None, None))[0]
        if current_holder:
            return has_cycle(current_holder, {requesting_agent})
        
        return False
    
    def _resolve_deadlock(self, agent1: str, file_path: str):
        """Resolve a deadlock by aborting the younger lock holder."""
        # Load lock graph config
        if self.lock_graph_path.exists():
            with open(self.lock_graph_path, 'r') as f:
                lock_config = yaml.safe_load(f) or {}
        else:
            lock_config = {}
        
        strategy = lock_config.get("abort_strategy", "youngest_holder")
        
        if strategy == "youngest_holder":
            # Find the youngest lock holder
            current_holder, lock_time = self.locks.get(file_path, (None, None))
            if current_holder:
                # Compare lock times
                agent1_locks = [(f, t) for f, (h, t) in self.locks.items() if h == agent1]
                if agent1_locks:
                    oldest_agent1 = min(agent1_locks, key=lambda x: x[1])[1]
                    if lock_time > oldest_agent1:
                        # Current holder is younger, abort it
                        self._abort_agent(current_holder, "Deadlock resolution - youngest holder")
                    else:
                        # Requesting agent is younger, deny request
                        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics as JSON."""
        with self._lock:
            return {
                "global": asdict(self.global_metrics),
                "agents": {
                    name: {
                        "credits_used": m.credits_used,
                        "tokens_used": m.tokens_used,
                        "wall_time_ms": m.wall_time_ms,
                        "tool_calls": m.tool_calls,
                        "status": m.status,
                        "checkpoints": len(m.checkpoints)
                    }
                    for name, m in self.agent_metrics.items()
                },
                "locks": {
                    file: {"holder": holder, "since": lock_time.isoformat()}
                    for file, (holder, lock_time) in self.locks.items()
                },
                "config": {
                    "global_hard_cap": self.config["global_hard_cap"],
                    "checkpoint_interval": self.config["checkpoint_interval"]
                }
            }
    
    def export_metrics_endpoint(self, output_path: Optional[str] = None) -> str:
        """Export metrics as JSON to file or return as string."""
        metrics = self.get_metrics()
        metrics_json = json.dumps(metrics, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(metrics_json)
        
        return metrics_json


# Singleton instance
_sentinel_instance: Optional[CreditSentinel] = None


def get_sentinel() -> CreditSentinel:
    """Get or create the singleton sentinel instance."""
    global _sentinel_instance
    if _sentinel_instance is None:
        _sentinel_instance = CreditSentinel()
        _sentinel_instance.start_monitoring()
    return _sentinel_instance


def track_tool_call(agent_name: str, tool_name: str, credits: int = 1, tokens: int = 100) -> str:
    """Track a tool call and return the action taken."""
    sentinel = get_sentinel()
    action = sentinel.track_tool_call(agent_name, tool_name, credits, tokens)
    return action.value


def get_metrics_json() -> str:
    """Get current metrics as JSON string."""
    sentinel = get_sentinel()
    return sentinel.export_metrics_endpoint()


if __name__ == "__main__":
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python credit_sentinel_v2.py <command> [args]")
        print("Commands:")
        print("  track <agent> <tool> <credits> <tokens>")
        print("  metrics")
        print("  start <agent>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "track" and len(sys.argv) >= 6:
        agent = sys.argv[2]
        tool = sys.argv[3]
        credits = int(sys.argv[4])
        tokens = int(sys.argv[5])
        result = track_tool_call(agent, tool, credits, tokens)
        print(f"Action: {result}")
    
    elif command == "metrics":
        print(get_metrics_json())
    
    elif command == "start" and len(sys.argv) >= 3:
        agent = sys.argv[2]
        sentinel = get_sentinel()
        result = sentinel.track_agent_start(agent)
        print(f"Agent {agent} start: {result.value}")
    
    else:
        print("Invalid command or arguments")
        sys.exit(1)