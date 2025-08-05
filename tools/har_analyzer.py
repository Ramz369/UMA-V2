"""Extract timing metrics from a HAR file (stub)."""
import json, sys, statistics as stats

def analyze(har_path: str) -> dict:
    entries = json.load(open(har_path))['log']['entries']
    dns = [e['timings']['dns'] for e in entries if e['timings']['dns']>=0]
    tls = [e['timings']['ssl'] for e in entries if e['timings']['ssl']>=0]
    fb  = [e['timings']['wait'] for e in entries]
    return {
        "dns_p95_ms": stats.quantiles(dns, n=20)[18] if dns else None,
        "tls_p95_ms": stats.quantiles(tls, n=20)[18] if tls else None,
        "first_byte_p95_ms": stats.quantiles(fb, n=20)[18]
    }
if __name__ == "__main__":
    print(analyze(sys.argv[1]))