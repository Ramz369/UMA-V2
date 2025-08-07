
"""
@cognimap:fingerprint
id: f004cb7b-696f-4574-9fd8-48d3b53d1d1d
birth: 2025-08-07T07:23:38.065062Z
parent: None
intent: Unit tests for credit sentinel v2.
semantic_tags: [authentication, api, testing, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.065800Z
hash: 9a892dc4
language: python
type: test
@end:cognimap
"""

"""Unit tests for credit sentinel v2."""
import pytest
import json
import time
import tempfile
import csv
from pathlib import Path
from datetime import datetime, timedelta
import sys
import threading

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.credit_sentinel_v2 import (
    CreditSentinel, ThrottleAction, AgentMetrics, GlobalMetrics,
    get_sentinel, track_tool_call, get_metrics_json
)


class TestCreditSentinel:
    """Test suite for credit sentinel functionality."""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config file."""
        config = {
            "global_hard_cap": 100,
            "checkpoint_interval": 10,
            "agent_caps": {
                "test-agent": 50,
                "small-agent": 20
            },
            "wall_time_limits": {
                "default": 5000,  # 5 seconds for testing
                "test-agent": 10000  # 10 seconds
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config, f)
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def sentinel(self, temp_config):
        """Create a test sentinel instance."""
        sentinel = CreditSentinel(config_path=str(temp_config))
        sentinel.start_monitoring()
        yield sentinel
        sentinel.stop_monitoring()
    
    def test_sentinel_initialization(self, sentinel):
        """Test sentinel initialization."""
        assert sentinel.config["global_hard_cap"] == 100
        assert sentinel.config["checkpoint_interval"] == 10
        assert "test-agent" in sentinel.config["agent_caps"]
        assert sentinel.config["agent_caps"]["test-agent"] == 50
    
    def test_track_agent_start(self, sentinel):
        """Test tracking agent start."""
        result = sentinel.track_agent_start("test-agent")
        
        assert result == ThrottleAction.ALLOW
        assert "test-agent" in sentinel.agent_metrics
        assert sentinel.agent_metrics["test-agent"].status == "active"
        assert sentinel.global_metrics.active_agents == 1
    
    def test_track_tool_call(self, sentinel):
        """Test tracking tool calls."""
        # First call
        result = sentinel.track_tool_call("test-agent", "tool1", 5, 500)
        assert result == ThrottleAction.ALLOW
        
        metrics = sentinel.agent_metrics["test-agent"]
        assert metrics.credits_used == 5
        assert metrics.tokens_used == 500
        assert metrics.tool_calls == 1
    
    def test_checkpoint_creation(self, sentinel):
        """Test checkpoint creation at intervals."""
        # Track calls to reach checkpoint interval (10 credits)
        sentinel.track_tool_call("test-agent", "tool1", 9, 900)
        result = sentinel.track_tool_call("test-agent", "tool2", 1, 100)
        
        assert result == ThrottleAction.CHECKPOINT
        
        metrics = sentinel.agent_metrics["test-agent"]
        assert len(metrics.checkpoints) == 1
        assert metrics.credits_used == 10
    
    def test_credit_limit_warnings(self, sentinel):
        """Test credit limit warning levels."""
        # Test agent has 50 credit cap
        
        # Below 80% - should allow
        result = sentinel.track_tool_call("test-agent", "tool1", 35, 3500)
        assert result == ThrottleAction.ALLOW
        
        # At 80% - should warn
        result = sentinel.track_tool_call("test-agent", "tool2", 5, 500)
        assert result == ThrottleAction.WARN
        
        # At 90% - should throttle
        result = sentinel.track_tool_call("test-agent", "tool3", 5, 500)
        assert result == ThrottleAction.THROTTLE
        
        # At 100% - should abort
        result = sentinel.track_tool_call("test-agent", "tool4", 5, 500)
        assert result == ThrottleAction.ABORT
        assert sentinel.agent_metrics["test-agent"].status == "aborted"
    
    def test_global_hard_cap(self, sentinel):
        """Test global hard cap enforcement."""
        # Global cap is 100
        sentinel.track_tool_call("agent1", "tool1", 60, 6000)
        sentinel.track_tool_call("agent2", "tool2", 35, 3500)
        
        # Next call would exceed global cap
        result = sentinel.track_tool_call("agent3", "tool3", 10, 1000)
        assert result == ThrottleAction.ABORT
    
    def test_wall_time_monitoring(self, sentinel):
        """Test wall-time limit monitoring."""
        # Start agent with 5-second limit
        sentinel.track_agent_start("fast-agent")
        
        # Should be active initially
        assert sentinel.agent_metrics["fast-agent"].status == "active"
        
        # Manually set start time to past to simulate timeout
        sentinel.agent_metrics["fast-agent"].start_time = datetime.now() - timedelta(seconds=6)
        
        # Give monitor thread time to detect
        time.sleep(2)
        
        # Should be aborted for exceeding wall-time
        assert sentinel.agent_metrics["fast-agent"].status == "aborted"
    
    def test_lock_acquisition(self, sentinel):
        """Test file lock acquisition."""
        # Agent1 acquires lock
        assert sentinel.acquire_lock("agent1", "file1.py") == True
        
        # Agent2 tries to acquire same lock
        assert sentinel.acquire_lock("agent2", "file1.py") == False
        
        # Agent1 can re-acquire its own lock
        assert sentinel.acquire_lock("agent1", "file1.py") == True
        
        # Release and re-acquire
        sentinel.release_lock("agent1", "file1.py")
        assert sentinel.acquire_lock("agent2", "file1.py") == True
    
    def test_lock_release_on_abort(self, sentinel):
        """Test that locks are released when agent is aborted."""
        sentinel.acquire_lock("test-agent", "file1.py")
        sentinel.acquire_lock("test-agent", "file2.py")
        
        # Abort the agent
        sentinel._abort_agent("test-agent", "Test abort")
        
        # Locks should be released
        assert sentinel.acquire_lock("other-agent", "file1.py") == True
        assert sentinel.acquire_lock("other-agent", "file2.py") == True
    
    def test_metrics_export(self, sentinel):
        """Test metrics export functionality."""
        # Generate some activity
        sentinel.track_agent_start("agent1")
        sentinel.track_tool_call("agent1", "tool1", 10, 1000)
        sentinel.track_tool_call("agent1", "tool2", 5, 500)
        
        # Get metrics
        metrics = sentinel.get_metrics()
        
        assert "global" in metrics
        assert "agents" in metrics
        assert "locks" in metrics
        assert "config" in metrics
        
        # Check global metrics
        assert metrics["global"]["total_credits"] == 15
        assert metrics["global"]["total_tokens"] == 1500
        assert metrics["global"]["total_tool_calls"] == 2
        
        # Check agent metrics
        assert "agent1" in metrics["agents"]
        assert metrics["agents"]["agent1"]["credits_used"] == 15
        assert metrics["agents"]["agent1"]["tokens_used"] == 1500
    
    def test_metrics_json_export(self, sentinel):
        """Test JSON metrics export."""
        sentinel.track_agent_start("test-agent")
        sentinel.track_tool_call("test-agent", "tool1", 5, 500)
        
        json_str = sentinel.export_metrics_endpoint()
        metrics = json.loads(json_str)
        
        assert isinstance(metrics, dict)
        assert "global" in metrics
        assert "agents" in metrics
    
    def test_csv_logging(self, sentinel):
        """Test CSV metrics logging."""
        # Track some calls
        sentinel.track_tool_call("agent1", "tool1", 10, 1000)
        sentinel.track_tool_call("agent2", "tool2", 5, 500)
        
        # Check CSV file was created
        assert sentinel.metrics_path.exists()
        
        # Read and verify CSV
        with open(sentinel.metrics_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]["agent"] == "agent1"
        assert rows[0]["credits"] == "10"
        assert rows[1]["agent"] == "agent2"
        assert rows[1]["credits"] == "5"
    
    def test_singleton_pattern(self):
        """Test singleton pattern for get_sentinel."""
        sentinel1 = get_sentinel()
        sentinel2 = get_sentinel()
        
        assert sentinel1 is sentinel2
    
    def test_track_tool_call_function(self):
        """Test the track_tool_call convenience function."""
        # Reset singleton
        import tools.credit_sentinel_v2
        tools.credit_sentinel_v2._sentinel_instance = None
        
        result = track_tool_call("test-agent", "test-tool", 5, 500)
        assert result in ["allow", "warn", "checkpoint", "throttle", "abort"]
    
    def test_get_metrics_json_function(self):
        """Test the get_metrics_json convenience function."""
        # Reset singleton
        import tools.credit_sentinel_v2
        tools.credit_sentinel_v2._sentinel_instance = None
        
        track_tool_call("test-agent", "test-tool", 5, 500)
        
        json_str = get_metrics_json()
        metrics = json.loads(json_str)
        
        assert "global" in metrics
        assert metrics["global"]["total_credits"] == 5
    
    def test_concurrent_access(self, sentinel):
        """Test thread-safe concurrent access."""
        results = []
        
        def track_calls(agent_name):
            for i in range(10):
                result = sentinel.track_tool_call(agent_name, f"tool{i}", 1, 100)
                results.append(result)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=track_calls, args=(f"agent{i}",))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify consistency
        assert sentinel.global_metrics.total_credits == 50  # 5 agents * 10 calls * 1 credit
        assert sentinel.global_metrics.total_tool_calls == 50
    
    def test_agent_metrics_dataclass(self):
        """Test AgentMetrics dataclass."""
        metrics = AgentMetrics(name="test")
        assert metrics.name == "test"
        assert metrics.credits_used == 0
        assert metrics.status == "active"
        assert isinstance(metrics.checkpoints, list)
    
    def test_global_metrics_dataclass(self):
        """Test GlobalMetrics dataclass."""
        metrics = GlobalMetrics()
        assert metrics.total_credits == 0
        assert metrics.active_agents == 0
        assert metrics.aborted_agents == 0
    
    def test_throttle_action_enum(self):
        """Test ThrottleAction enum."""
        assert ThrottleAction.ALLOW.value == "allow"
        assert ThrottleAction.WARN.value == "warn"
        assert ThrottleAction.CHECKPOINT.value == "checkpoint"
        assert ThrottleAction.THROTTLE.value == "throttle"
        assert ThrottleAction.ABORT.value == "abort"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])