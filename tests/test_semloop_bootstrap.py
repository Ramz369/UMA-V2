"""Integration tests for SemLoop stack bootstrap."""
import pytest
import subprocess
import time
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.integration
class TestSemLoopBootstrap:
    """Test suite for SemLoop stack bootstrap."""
    
    @pytest.fixture(scope="class")
    def stack_up(self):
        """Start the SemLoop stack for tests."""
        # Check if Docker is available
        docker_check = subprocess.run(
            ["docker", "version"],
            capture_output=True
        )
        if docker_check.returncode != 0:
            pytest.skip("Docker not available")
        
        # Start stack
        compose_file = Path(__file__).parent.parent / "infra" / "semloop-stack.yml"
        if not compose_file.exists():
            pytest.skip("Compose file not found")
        
        print("\nStarting SemLoop stack...")
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"Failed to start stack: {result.stderr}")
        
        # Wait for services
        print("Waiting for services to initialize...")
        time.sleep(30)
        
        yield
        
        # Teardown
        print("\nTearing down SemLoop stack...")
        subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "down", "-v"],
            capture_output=True
        )
    
    def test_health_script_exists(self):
        """Test that health check script exists."""
        health_script = Path(__file__).parent.parent / "scripts" / "semloop_health.py"
        assert health_script.exists(), "Health check script not found"
        assert health_script.stat().st_size > 0, "Health check script is empty"
    
    @pytest.mark.integration
    def test_health_check_passes(self, stack_up):
        """Test that health check passes when stack is running."""
        health_script = Path(__file__).parent.parent / "scripts" / "semloop_health.py"
        
        result = subprocess.run(
            ["python3", str(health_script)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"\nHealth check output:\n{result.stdout}")
        
        assert result.returncode == 0, f"Health check failed:\n{result.stdout}\n{result.stderr}"
        assert "All services healthy" in result.stdout
    
    @pytest.mark.integration
    def test_minio_accessible(self, stack_up):
        """Test MinIO is accessible."""
        result = subprocess.run(
            ["curl", "-f", "-s", "http://localhost:9000/minio/health/ready"],
            capture_output=True,
            timeout=5
        )
        assert result.returncode == 0, "MinIO health endpoint not accessible"
    
    @pytest.mark.integration
    def test_redis_accessible(self, stack_up):
        """Test Redis is accessible."""
        result = subprocess.run(
            ["redis-cli", "-h", "localhost", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, "Redis not accessible"
        assert "PONG" in result.stdout, "Redis did not respond with PONG"
    
    @pytest.mark.integration
    def test_postgres_accessible(self, stack_up):
        """Test PostgreSQL is accessible."""
        result = subprocess.run(
            ["pg_isready", "-h", "localhost", "-p", "5432", "-U", "semloop"],
            capture_output=True,
            timeout=5
        )
        assert result.returncode == 0, "PostgreSQL not ready"
    
    def test_compose_file_valid(self):
        """Test that compose file is valid."""
        compose_file = Path(__file__).parent.parent / "infra" / "semloop-stack.yml"
        
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "config"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Invalid compose file: {result.stderr}"
    
    def test_health_check_without_stack(self):
        """Test health check behavior when stack is not running."""
        # First ensure stack is down
        compose_file = Path(__file__).parent.parent / "infra" / "semloop-stack.yml"
        subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "down", "-v"],
            capture_output=True
        )
        
        health_script = Path(__file__).parent.parent / "scripts" / "semloop_health.py"
        
        result = subprocess.run(
            ["python3", str(health_script)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 1, "Health check should fail when stack is down"
        assert "unhealthy" in result.stdout.lower() or "not accessible" in result.stdout.lower()


if __name__ == "__main__":
    # Run only non-integration tests by default
    pytest.main([__file__, "-v", "-m", "not integration"])