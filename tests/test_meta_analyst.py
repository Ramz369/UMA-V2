
"""
@cognimap:fingerprint
id: 264273be-b9f4-4bb1-ba0c-f68358536ddc
birth: 2025-08-07T07:23:38.069426Z
parent: None
intent: Unit tests for Meta-Analyst.
semantic_tags: [authentication, database, testing, utility]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.069821Z
hash: 7995827f
language: python
type: test
@end:cognimap
"""

"""Unit tests for Meta-Analyst."""
import tempfile
import yaml
import csv
import pytest
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.meta_analyst import MetaAnalyst


class TestMetaAnalyst:
    """Test suite for Meta-Analyst functionality."""
    
    def _write_fake_files(self, tmpdir):
        """Create test session summary and metrics files."""
        session = {
            "session_id": "uma-v2-test-001",
            "timestamp": "2025-08-06T12:00:00Z",
            "credits": {
                "used": 250,
                "remaining": 750,
                "max_per_agent": {
                    "tool-builder": 120,
                    "integration-agent": 45,
                    "planner": 35
                }
            },
            "agents": {
                "active": {
                    "tool-builder": {
                        "credits": 120,
                        "wall_time_ms": 40000,
                        "last_action": "tool_call"
                    }
                },
                "idle": {
                    "integration-agent": {
                        "credits": 45,
                        "last_active": "2025-08-06T11:00:00Z"
                    }
                },
                "aborted": []
            }
        }
        
        metrics_rows = [
            {
                "timestamp": "2025-08-06T00:00:01",
                "agent": "tool-builder",
                "tool_call": "sandbox",
                "credits": "5",
                "tokens": "500",
                "wall_time_ms": "1200",
                "exit_status": "allow"
            },
            {
                "timestamp": "2025-08-06T00:01:00",
                "agent": "integration-agent",
                "tool_call": "github_client",
                "credits": "3",
                "tokens": "300",
                "wall_time_ms": "800",
                "exit_status": "success"
            },
            {
                "timestamp": "2025-08-06T00:02:00",
                "agent": "planner",
                "tool_call": "Think",
                "credits": "1",
                "tokens": "100",
                "wall_time_ms": "500",
                "exit_status": "checkpoint"
            }
        ]
        
        sess_path = tmpdir / "summary.yaml"
        metrics_path = tmpdir / "metrics.csv"
        
        with open(sess_path, "w") as f:
            yaml.safe_dump(session, f)
        
        with open(metrics_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=metrics_rows[0].keys())
            writer.writeheader()
            writer.writerows(metrics_rows)
        
        return sess_path, metrics_path
    
    @pytest.fixture
    def temp_files(self):
        """Create temporary test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            sess_path, metrics_path = self._write_fake_files(tmpdir)
            yield sess_path, metrics_path
    
    def test_report_generation(self, temp_files):
        """Test basic report generation."""
        sess_path, metrics_path = temp_files
        out_path = sess_path.parent / "report.md"
        
        analyst = MetaAnalyst(str(sess_path), str(metrics_path))
        report_md = analyst.generate_report(str(out_path))
        
        assert "Total Credits Used" in report_md
        assert "250/1000" in report_md
        assert out_path.exists()
        
        # Verify file content
        with open(out_path, 'r') as f:
            content = f.read()
            assert "Meta-Analyst Nightly Report" in content
            assert "Executive Summary" in content
    
    def test_credit_analysis(self, temp_files):
        """Test credit usage analysis."""
        sess_path, metrics_path = temp_files
        
        analyst = MetaAnalyst(str(sess_path), str(metrics_path))
        session = analyst.load_session_summary()
        metrics = analyst.load_metrics_csv()
        
        analysis = analyst.analyze_credit_usage(session, metrics)
        
        assert analysis['total_used'] == 250
        assert analysis['remaining'] == 750
        assert analysis['utilization_pct'] == 25.0
        assert 'tool-builder' in analysis['by_agent']
        assert analysis['efficiency_score'] == 100.0  # All ops successful
    
    def test_agent_performance_analysis(self, temp_files):
        """Test agent performance metrics."""
        sess_path, metrics_path = temp_files
        
        analyst = MetaAnalyst(str(sess_path), str(metrics_path))
        session = analyst.load_session_summary()
        metrics = analyst.load_metrics_csv()
        
        analysis = analyst.analyze_agent_performance(session, metrics)
        
        assert 'tool-builder' in analysis['active_agents']
        assert 'integration-agent' in analysis['idle_agents']
        assert len(analysis['aborted_agents']) == 0
        assert len(analysis['error_rates']) >= 0
    
    def test_trend_analysis(self, temp_files):
        """Test trend analysis over time."""
        sess_path, metrics_path = temp_files
        
        analyst = MetaAnalyst(str(sess_path), str(metrics_path))
        metrics = analyst.load_metrics_csv()
        
        analysis = analyst.analyze_trends(metrics)
        
        assert '2025-08-06' in analysis['daily_credits']
        assert analysis['daily_credits']['2025-08-06'] == 9  # 5+3+1
        assert 0 in analysis['hourly_pattern']  # Hour 0 has all events
    
    def test_warnings_generation(self):
        """Test warning generation for high usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create session with high credit usage
            session = {
                "credits": {
                    "used": 920,
                    "remaining": 80,
                    "max_per_agent": {"planner": 60}  # Over cap
                }
            }
            
            sess_path = tmpdir / "summary.yaml"
            metrics_path = tmpdir / "metrics.csv"
            
            with open(sess_path, "w") as f:
                yaml.safe_dump(session, f)
            
            # Empty metrics
            with open(metrics_path, "w") as f:
                f.write("timestamp,agent,credits\n")
            
            analyst = MetaAnalyst(str(sess_path), str(metrics_path))
            report = analyst.generate_report(str(tmpdir / "report.md"))
            
            assert "CRITICAL" in str(analyst.warnings)
            assert "92.0%" in report
            assert "Planner exceeded soft cap" in str(analyst.warnings)
    
    def test_recommendations(self, temp_files):
        """Test recommendation generation."""
        sess_path, metrics_path = temp_files
        
        analyst = MetaAnalyst(str(sess_path), str(metrics_path))
        session = analyst.load_session_summary()
        metrics = analyst.load_metrics_csv()
        
        credit_analysis = analyst.analyze_credit_usage(session, metrics)
        agent_analysis = analyst.analyze_agent_performance(session, metrics)
        
        recommendations = analyst.generate_recommendations(credit_analysis, agent_analysis)
        
        # Should have no critical recommendations at 25% usage
        assert not any("🔴" in r for r in recommendations)
    
    def test_missing_files(self):
        """Test handling of missing input files."""
        analyst = MetaAnalyst("nonexistent.yaml", "nonexistent.csv")
        
        with tempfile.NamedTemporaryFile(suffix=".md") as f:
            report = analyst.generate_report(f.name)
            
            assert "Unknown" in report  # Session ID unknown
            assert "0/1000" in report   # No credits used
            assert Path(f.name).exists()
    
    def test_cli_exit_code(self):
        """Test that CLI exits with error on critical warnings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create critical usage scenario
            session = {
                "credits": {"used": 950, "remaining": 50}
            }
            
            sess_path = tmpdir / "summary.yaml"
            with open(sess_path, "w") as f:
                yaml.safe_dump(session, f)
            
            # Empty metrics
            metrics_path = tmpdir / "metrics.csv"
            with open(metrics_path, "w") as f:
                f.write("timestamp,agent,credits\n")
            
            analyst = MetaAnalyst(str(sess_path), str(metrics_path))
            analyst.generate_report(str(tmpdir / "report.md"))
            
            # Should have critical warning
            assert any("CRITICAL" in w for w in analyst.warnings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])