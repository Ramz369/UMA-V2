"""Extract comprehensive timing metrics from HAR files - Production Implementation."""
import json
import sys
import statistics as stats
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import urllib.parse
from pathlib import Path


@dataclass
class TimingMetrics:
    """Container for detailed timing metrics."""
    dns_ms: Optional[float] = None
    connect_ms: Optional[float] = None
    tls_ms: Optional[float] = None
    wait_ms: Optional[float] = None
    receive_ms: Optional[float] = None
    total_ms: Optional[float] = None
    blocked_ms: Optional[float] = None


@dataclass
class RequestMetrics:
    """Metrics for a single HTTP request."""
    url: str
    method: str
    status: int
    size_bytes: int
    timing: TimingMetrics
    cache_status: str
    mime_type: str
    timestamp: str


class HARAnalyzer:
    """Comprehensive HAR file analyzer for performance metrics."""
    
    def __init__(self, har_path: str):
        self.har_path = Path(har_path)
        self.har_data = None
        self.entries: List[RequestMetrics] = []
        self._load_har()
    
    def _load_har(self) -> None:
        """Load and validate HAR file."""
        if not self.har_path.exists():
            raise FileNotFoundError(f"HAR file not found: {self.har_path}")
        
        try:
            with open(self.har_path, 'r', encoding='utf-8') as f:
                self.har_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid HAR file format: {e}")
        
        if 'log' not in self.har_data or 'entries' not in self.har_data['log']:
            raise ValueError("HAR file missing required 'log.entries' structure")
        
        self._parse_entries()
    
    def _parse_entries(self) -> None:
        """Parse HAR entries into structured metrics."""
        for entry in self.har_data['log']['entries']:
            try:
                timing = entry.get('timings', {})
                request = entry.get('request', {})
                response = entry.get('response', {})
                
                # Extract timing metrics
                timing_metrics = TimingMetrics(
                    dns_ms=self._safe_timing(timing.get('dns')),
                    connect_ms=self._safe_timing(timing.get('connect')),
                    tls_ms=self._safe_timing(timing.get('ssl')),
                    wait_ms=self._safe_timing(timing.get('wait')),
                    receive_ms=self._safe_timing(timing.get('receive')),
                    total_ms=entry.get('time'),
                    blocked_ms=self._safe_timing(timing.get('blocked'))
                )
                
                # Determine cache status
                cache_status = "miss"
                if response.get('status') == 304:
                    cache_status = "revalidated"
                elif any(h['name'].lower() == 'x-cache' and 'hit' in h['value'].lower() 
                        for h in response.get('headers', [])):
                    cache_status = "hit"
                
                # Create request metrics
                metrics = RequestMetrics(
                    url=request.get('url', ''),
                    method=request.get('method', 'GET'),
                    status=response.get('status', 0),
                    size_bytes=response.get('bodySize', 0),
                    timing=timing_metrics,
                    cache_status=cache_status,
                    mime_type=response.get('content', {}).get('mimeType', 'unknown'),
                    timestamp=entry.get('startedDateTime', '')
                )
                
                self.entries.append(metrics)
            except Exception as e:
                # Skip malformed entries
                continue
    
    def _safe_timing(self, value: Any) -> Optional[float]:
        """Safely convert timing value to float."""
        if value is None or value < 0:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    
    def get_percentile(self, values: List[float], percentile: int) -> Optional[float]:
        """Calculate percentile from list of values."""
        if not values:
            return None
        if len(values) == 1:
            return values[0]
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of HAR data."""
        if not self.entries:
            return {"error": "No valid entries found in HAR file"}
        
        # Extract timing lists
        dns_times = [e.timing.dns_ms for e in self.entries if e.timing.dns_ms is not None]
        tls_times = [e.timing.tls_ms for e in self.entries if e.timing.tls_ms is not None]
        wait_times = [e.timing.wait_ms for e in self.entries if e.timing.wait_ms is not None]
        total_times = [e.timing.total_ms for e in self.entries if e.timing.total_ms is not None]
        
        # Calculate percentiles
        result = {
            "summary": {
                "total_requests": len(self.entries),
                "failed_requests": len([e for e in self.entries if e.status >= 400]),
                "cached_requests": len([e for e in self.entries if e.cache_status == "hit"]),
                "total_bytes": sum(e.size_bytes for e in self.entries),
                "unique_domains": len(set(urllib.parse.urlparse(e.url).netloc for e in self.entries))
            },
            "timing": {
                "dns": {
                    "p50_ms": self.get_percentile(dns_times, 50),
                    "p95_ms": self.get_percentile(dns_times, 95),
                    "p99_ms": self.get_percentile(dns_times, 99),
                    "mean_ms": stats.mean(dns_times) if dns_times else None
                },
                "tls": {
                    "p50_ms": self.get_percentile(tls_times, 50),
                    "p95_ms": self.get_percentile(tls_times, 95),
                    "p99_ms": self.get_percentile(tls_times, 99),
                    "mean_ms": stats.mean(tls_times) if tls_times else None
                },
                "first_byte": {
                    "p50_ms": self.get_percentile(wait_times, 50),
                    "p95_ms": self.get_percentile(wait_times, 95),
                    "p99_ms": self.get_percentile(wait_times, 99),
                    "mean_ms": stats.mean(wait_times) if wait_times else None
                },
                "total": {
                    "p50_ms": self.get_percentile(total_times, 50),
                    "p95_ms": self.get_percentile(total_times, 95),
                    "p99_ms": self.get_percentile(total_times, 99),
                    "mean_ms": stats.mean(total_times) if total_times else None,
                    "sum_ms": sum(total_times) if total_times else 0
                }
            },
            "by_domain": self._analyze_by_domain(),
            "by_type": self._analyze_by_type(),
            "slowest_requests": self._get_slowest_requests(5)
        }
        
        return result
    
    def _analyze_by_domain(self) -> Dict[str, Any]:
        """Analyze metrics grouped by domain."""
        domain_metrics = {}
        
        for entry in self.entries:
            domain = urllib.parse.urlparse(entry.url).netloc
            if domain not in domain_metrics:
                domain_metrics[domain] = {
                    "count": 0,
                    "bytes": 0,
                    "total_time_ms": 0
                }
            
            domain_metrics[domain]["count"] += 1
            domain_metrics[domain]["bytes"] += entry.size_bytes
            if entry.timing.total_ms:
                domain_metrics[domain]["total_time_ms"] += entry.timing.total_ms
        
        return domain_metrics
    
    def _analyze_by_type(self) -> Dict[str, Any]:
        """Analyze metrics grouped by content type."""
        type_metrics = {}
        
        for entry in self.entries:
            content_type = entry.mime_type.split(';')[0].strip()
            category = self._categorize_content_type(content_type)
            
            if category not in type_metrics:
                type_metrics[category] = {
                    "count": 0,
                    "bytes": 0,
                    "total_time_ms": 0
                }
            
            type_metrics[category]["count"] += 1
            type_metrics[category]["bytes"] += entry.size_bytes
            if entry.timing.total_ms:
                type_metrics[category]["total_time_ms"] += entry.timing.total_ms
        
        return type_metrics
    
    def _categorize_content_type(self, mime_type: str) -> str:
        """Categorize MIME type into broader categories."""
        if 'javascript' in mime_type or 'ecmascript' in mime_type:
            return 'javascript'
        elif 'css' in mime_type:
            return 'css'
        elif 'html' in mime_type:
            return 'html'
        elif 'json' in mime_type or 'xml' in mime_type:
            return 'api'
        elif 'image' in mime_type:
            return 'image'
        elif 'font' in mime_type:
            return 'font'
        else:
            return 'other'
    
    def _get_slowest_requests(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the slowest requests by total time."""
        sorted_entries = sorted(
            [e for e in self.entries if e.timing.total_ms is not None],
            key=lambda x: x.timing.total_ms,
            reverse=True
        )[:count]
        
        return [
            {
                "url": e.url,
                "method": e.method,
                "total_ms": e.timing.total_ms,
                "wait_ms": e.timing.wait_ms,
                "size_bytes": e.size_bytes
            }
            for e in sorted_entries
        ]


def analyze(har_path: str) -> Dict[str, Any]:
    """Main entry point for HAR analysis."""
    try:
        analyzer = HARAnalyzer(har_path)
        return analyzer.analyze()
    except Exception as e:
        return {
            "error": str(e),
            "har_path": har_path
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python har_analyzer.py <har_file>")
        sys.exit(1)
    
    har_file = sys.argv[1]
    result = analyze(har_file)
    print(json.dumps(result, indent=2))