
"""
@cognimap:fingerprint
id: 31e9009e-3331-4717-b856-be0c11b9c8dd
birth: 2025-08-07T07:23:38.064449Z
parent: None
intent: Unit tests for HAR analyzer tool.
semantic_tags: [database, api, testing, ui]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.064951Z
hash: 5051569b
language: python
type: test
@end:cognimap
"""

"""Unit tests for HAR analyzer tool."""
import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.har_analyzer import HARAnalyzer, analyze, TimingMetrics, RequestMetrics


class TestHARAnalyzer:
    """Test suite for HAR analyzer functionality."""
    
    @pytest.fixture
    def sample_har_data(self):
        """Create sample HAR data for testing."""
        return {
            "log": {
                "version": "1.2",
                "creator": {"name": "test", "version": "1.0"},
                "entries": [
                    {
                        "startedDateTime": "2024-01-01T10:00:00.000Z",
                        "time": 150,
                        "request": {
                            "method": "GET",
                            "url": "https://example.com/api/data",
                            "httpVersion": "HTTP/1.1",
                            "headers": [],
                            "queryString": [],
                            "cookies": [],
                            "headersSize": 100,
                            "bodySize": 0
                        },
                        "response": {
                            "status": 200,
                            "statusText": "OK",
                            "httpVersion": "HTTP/1.1",
                            "headers": [
                                {"name": "Content-Type", "value": "application/json"}
                            ],
                            "cookies": [],
                            "content": {
                                "size": 1024,
                                "mimeType": "application/json"
                            },
                            "redirectURL": "",
                            "headersSize": 200,
                            "bodySize": 1024
                        },
                        "cache": {},
                        "timings": {
                            "blocked": 5,
                            "dns": 10,
                            "connect": 20,
                            "send": 5,
                            "wait": 100,
                            "receive": 10,
                            "ssl": 15
                        }
                    },
                    {
                        "startedDateTime": "2024-01-01T10:00:01.000Z",
                        "time": 80,
                        "request": {
                            "method": "GET",
                            "url": "https://example.com/style.css",
                            "httpVersion": "HTTP/1.1",
                            "headers": [],
                            "queryString": [],
                            "cookies": [],
                            "headersSize": 100,
                            "bodySize": 0
                        },
                        "response": {
                            "status": 304,
                            "statusText": "Not Modified",
                            "httpVersion": "HTTP/1.1",
                            "headers": [
                                {"name": "Content-Type", "value": "text/css"}
                            ],
                            "cookies": [],
                            "content": {
                                "size": 0,
                                "mimeType": "text/css"
                            },
                            "redirectURL": "",
                            "headersSize": 150,
                            "bodySize": 0
                        },
                        "cache": {},
                        "timings": {
                            "blocked": 2,
                            "dns": -1,
                            "connect": -1,
                            "send": 3,
                            "wait": 70,
                            "receive": 5,
                            "ssl": -1
                        }
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_har_file(self, sample_har_data):
        """Create a temporary HAR file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
            json.dump(sample_har_data, f)
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    def test_har_analyzer_initialization(self, sample_har_file):
        """Test HARAnalyzer initialization."""
        analyzer = HARAnalyzer(str(sample_har_file))
        
        assert analyzer.har_data is not None
        assert len(analyzer.entries) == 2
        assert analyzer.har_path == sample_har_file
    
    def test_har_analyzer_parse_entries(self, sample_har_file):
        """Test parsing of HAR entries."""
        analyzer = HARAnalyzer(str(sample_har_file))
        
        # Check first entry
        first_entry = analyzer.entries[0]
        assert isinstance(first_entry, RequestMetrics)
        assert first_entry.url == "https://example.com/api/data"
        assert first_entry.method == "GET"
        assert first_entry.status == 200
        assert first_entry.size_bytes == 1024
        assert first_entry.mime_type == "application/json"
        
        # Check timing metrics
        assert first_entry.timing.dns_ms == 10
        assert first_entry.timing.wait_ms == 100
        assert first_entry.timing.tls_ms == 15
    
    def test_cache_status_detection(self, sample_har_file):
        """Test cache status detection."""
        analyzer = HARAnalyzer(str(sample_har_file))
        
        # First request should be cache miss
        assert analyzer.entries[0].cache_status == "miss"
        
        # Second request (304) should be revalidated
        assert analyzer.entries[1].cache_status == "revalidated"
    
    def test_analyze_summary(self, sample_har_file):
        """Test analysis summary generation."""
        result = analyze(str(sample_har_file))
        
        assert "summary" in result
        summary = result["summary"]
        
        assert summary["total_requests"] == 2
        assert summary["failed_requests"] == 0
        assert summary["total_bytes"] == 1024
        assert summary["unique_domains"] == 1
    
    def test_timing_percentiles(self, sample_har_file):
        """Test timing percentile calculations."""
        result = analyze(str(sample_har_file))
        
        assert "timing" in result
        timing = result["timing"]
        
        # DNS times (only one valid: 10ms)
        assert timing["dns"]["p50_ms"] == 10
        assert timing["dns"]["p95_ms"] == 10
        assert timing["dns"]["mean_ms"] == 10
        
        # Wait times (100ms and 70ms)
        assert timing["first_byte"]["mean_ms"] == 85  # (100+70)/2
    
    def test_domain_analysis(self, sample_har_file):
        """Test domain-based analysis."""
        result = analyze(str(sample_har_file))
        
        assert "by_domain" in result
        domains = result["by_domain"]
        
        assert "example.com" in domains
        assert domains["example.com"]["count"] == 2
        assert domains["example.com"]["bytes"] == 1024
    
    def test_content_type_analysis(self, sample_har_file):
        """Test content type categorization."""
        result = analyze(str(sample_har_file))
        
        assert "by_type" in result
        types = result["by_type"]
        
        assert "api" in types  # JSON is categorized as API
        assert "css" in types
        assert types["api"]["count"] == 1
        assert types["css"]["count"] == 1
    
    def test_slowest_requests(self, sample_har_file):
        """Test identification of slowest requests."""
        result = analyze(str(sample_har_file))
        
        assert "slowest_requests" in result
        slowest = result["slowest_requests"]
        
        assert len(slowest) == 2
        # First request (150ms) should be slowest
        assert slowest[0]["total_ms"] == 150
        assert slowest[0]["url"] == "https://example.com/api/data"
    
    def test_invalid_har_file(self):
        """Test handling of invalid HAR file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
            f.write("not valid json")
            temp_path = Path(f.name)
        
        try:
            result = analyze(str(temp_path))
            assert "error" in result
            assert "Invalid HAR file format" in result["error"]
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_missing_har_file(self):
        """Test handling of missing HAR file."""
        result = analyze("/nonexistent/file.har")
        
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    def test_empty_har_entries(self):
        """Test handling of HAR with no entries."""
        har_data = {"log": {"version": "1.2", "entries": []}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
            json.dump(har_data, f)
            temp_path = Path(f.name)
        
        try:
            result = analyze(str(temp_path))
            assert "error" in result
            assert "No valid entries" in result["error"]
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_timing_metrics_safety(self):
        """Test safe handling of timing values."""
        metrics = TimingMetrics()
        
        # Test with None values
        assert metrics.dns_ms is None
        assert metrics.total_ms is None
        
        # Test with negative values (should be filtered)
        analyzer = HARAnalyzer.__new__(HARAnalyzer)
        analyzer.entries = []
        assert analyzer._safe_timing(-1) is None
        assert analyzer._safe_timing(None) is None
        assert analyzer._safe_timing(100) == 100.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])