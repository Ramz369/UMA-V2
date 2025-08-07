#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: 74d811af-c305-4f7c-964c-a94d4875ce22
birth: 2025-08-07T07:23:38.071806Z
parent: None
intent: SemLoop stack health check script.
semantic_tags: [authentication, database, api, service, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.072068Z
hash: ef0ae530
language: python
type: component
@end:cognimap
"""

"""SemLoop stack health check script."""
import asyncio
import sys
import socket
import subprocess
from typing import Tuple, List


def check_port(host: str, port: int) -> bool:
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except:
        return False
    finally:
        sock.close()


def get_host(service: str, default: str = "localhost") -> str:
    """Get hostname for service (supports container networking)."""
    import os
    # If running in container, use service name
    if os.path.exists("/.dockerenv"):
        return service
    return default


async def check_minio() -> Tuple[str, bool, str]:
    """Check MinIO health."""
    host = get_host("minio")
    if not check_port(host, 9000):
        return "MinIO", False, "Port 9000 not accessible"
    
    # Try health endpoint
    proc = await asyncio.create_subprocess_exec(
        "curl", "-f", "-s", f"http://{host}:9000/minio/health/ready",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    
    if proc.returncode == 0:
        return "MinIO", True, "Ready on port 9000"
    else:
        return "MinIO", False, "Health check failed"


async def check_redpanda() -> Tuple[str, bool, str]:
    """Check Redpanda health."""
    host = get_host("redpanda")
    if not check_port(host, 9092):
        return "Redpanda", False, "Port 9092 not accessible"
    
    # Check admin API
    if check_port(host, 9644):
        return "Redpanda", True, "Kafka on 9092, Admin on 9644"
    else:
        return "Redpanda", True, "Kafka on 9092 (admin port not checked)"


async def check_postgres() -> Tuple[str, bool, str]:
    """Check PostgreSQL health."""
    host = get_host("postgres")
    if not check_port(host, 5432):
        return "PostgreSQL", False, "Port 5432 not accessible"
    
    # Try pg_isready
    proc = await asyncio.create_subprocess_exec(
        "pg_isready", "-h", host, "-p", "5432", "-U", "semloop",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    
    if proc.returncode == 0:
        # Check pgvector extension
        check_vector = await asyncio.create_subprocess_shell(
            f"PGPASSWORD=semloop123 psql -h {host} -U semloop -d semloop -t -c \"SELECT extname FROM pg_extension WHERE extname='vector';\" 2>/dev/null",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await check_vector.communicate()
        
        if b"vector" in stdout:
            return "PostgreSQL", True, "Ready with pgvector extension"
        else:
            return "PostgreSQL", True, "Ready (pgvector not confirmed)"
    else:
        return "PostgreSQL", False, "pg_isready check failed"


async def check_redis() -> Tuple[str, bool, str]:
    """Check Redis health."""
    host = get_host("redis")
    if not check_port(host, 6379):
        return "Redis", False, "Port 6379 not accessible"
    
    # Try redis-cli ping
    proc = await asyncio.create_subprocess_exec(
        "redis-cli", "-h", host, "ping",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    
    if proc.returncode == 0 and b"PONG" in stdout:
        return "Redis", True, "Ready on port 6379"
    else:
        return "Redis", False, "PING command failed"


async def run_health_checks() -> List[Tuple[str, bool, str]]:
    """Run all health checks concurrently."""
    tasks = [
        check_minio(),
        check_redpanda(),
        check_postgres(),
        check_redis()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            service_names = ["MinIO", "Redpanda", "PostgreSQL", "Redis"]
            processed_results.append((service_names[i], False, f"Error: {str(result)}"))
        else:
            processed_results.append(result)
    
    return processed_results


def main():
    """Main health check routine."""
    print("🔍 SemLoop Stack Health Check")
    print("=" * 40)
    
    # Run checks
    results = asyncio.run(run_health_checks())
    
    # Display results
    all_healthy = True
    for service, healthy, message in results:
        status = "✅" if healthy else "❌"
        print(f"{status} {service:12} : {message}")
        if not healthy:
            all_healthy = False
    
    print("=" * 40)
    
    if all_healthy:
        print("✅ All services healthy!")
        return 0
    else:
        print("❌ Some services are unhealthy")
        print("\nTroubleshooting:")
        print("1. Ensure Docker is running")
        print("2. Run: docker compose -f infra/semloop-stack.yml up -d")
        print("3. Wait 30 seconds for services to initialize")
        print("4. Check logs: docker compose -f infra/semloop-stack.yml logs")
        return 1


if __name__ == "__main__":
    # Check required tools
    required_tools = ["curl", "pg_isready", "redis-cli"]
    missing_tools = []
    
    for tool in required_tools:
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("Install with: apt-get install curl postgresql-client redis-tools")
        sys.exit(1)
    
    sys.exit(main())