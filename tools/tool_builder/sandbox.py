"""Sandbox harness for testing new tools in isolated Docker containers."""
import subprocess
import json
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os


class ToolSandbox:
    """Isolated testing environment for new tools."""
    
    def __init__(self, tool_name: str, tool_path: Path, test_path: Optional[Path] = None):
        self.tool_name = tool_name
        self.tool_path = Path(tool_path)
        self.test_path = test_path
        self.temp_dir = None
        self.docker_image = "python:3.12-slim"
        
    def __enter__(self):
        """Create temporary sandbox directory."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"tool_sandbox_{self.tool_name}_"))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary directory."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def prepare_sandbox(self) -> Path:
        """Copy tool and test files to sandbox."""
        if not self.temp_dir:
            raise RuntimeError("Sandbox not initialized - use context manager")
        
        # Create directory structure
        tools_dir = self.temp_dir / "tools"
        tests_dir = self.temp_dir / "tests"
        tools_dir.mkdir(exist_ok=True)
        tests_dir.mkdir(exist_ok=True)
        
        # Copy tool file
        if self.tool_path.exists():
            shutil.copy2(self.tool_path, tools_dir / self.tool_path.name)
        else:
            raise FileNotFoundError(f"Tool not found: {self.tool_path}")
        
        # Copy test file if provided
        if self.test_path and self.test_path.exists():
            shutil.copy2(self.test_path, tests_dir / self.test_path.name)
        
        # Create requirements.txt with common dependencies
        requirements = self.temp_dir / "requirements.txt"
        requirements.write_text("""pytest>=7.0.0
pyyaml>=6.0
sqlparse>=0.4.0
""")
        
        # Create __init__.py files
        (tools_dir / "__init__.py").touch()
        (tests_dir / "__init__.py").touch()
        
        # Create pytest.ini
        pytest_ini = self.temp_dir / "pytest.ini"
        pytest_ini.write_text("""[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
""")
        
        return self.temp_dir
    
    def run_tests(self) -> Tuple[bool, str, str]:
        """Run tests in Docker container."""
        sandbox_path = self.prepare_sandbox()
        
        # Docker command to run tests
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{sandbox_path}:/app",
            "-w", "/app",
            self.docker_image,
            "bash", "-c",
            "pip install -q -r requirements.txt && python -m pytest tests/ -v --tb=short"
        ]
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Test execution timed out after 60 seconds"
        except Exception as e:
            return False, "", str(e)
    
    def validate_syntax(self) -> Tuple[bool, str]:
        """Validate Python syntax without execution."""
        try:
            with open(self.tool_path, 'r') as f:
                code = f.read()
            
            compile(code, str(self.tool_path), 'exec')
            return True, "Syntax valid"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def run_cli_test(self, args: list) -> Tuple[bool, str, str]:
        """Test tool CLI interface."""
        sandbox_path = self.prepare_sandbox()
        tool_name = self.tool_path.stem
        
        # Docker command to run the tool
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{sandbox_path}:/app",
            "-w", "/app",
            self.docker_image,
            "bash", "-c",
            f"pip install -q -r requirements.txt && python tools/{tool_name}.py {' '.join(args)}"
        ]
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "CLI test timed out after 30 seconds"
        except Exception as e:
            return False, "", str(e)


def validate_new_tool(tool_name: str, run_tests: bool = True) -> Dict[str, Any]:
    """Validate a newly created tool."""
    tool_path = Path(f"tools/{tool_name}.py")
    test_path = Path(f"tests/test_{tool_name}.py")
    
    results = {
        "tool_name": tool_name,
        "tool_exists": tool_path.exists(),
        "test_exists": test_path.exists(),
        "syntax_valid": False,
        "tests_passed": False,
        "errors": []
    }
    
    if not tool_path.exists():
        results["errors"].append(f"Tool file not found: {tool_path}")
        return results
    
    with ToolSandbox(tool_name, tool_path, test_path) as sandbox:
        # Check syntax
        syntax_ok, syntax_msg = sandbox.validate_syntax()
        results["syntax_valid"] = syntax_ok
        if not syntax_ok:
            results["errors"].append(syntax_msg)
            return results
        
        # Run tests if requested and test file exists
        if run_tests and test_path.exists():
            test_ok, stdout, stderr = sandbox.run_tests()
            results["tests_passed"] = test_ok
            results["test_output"] = stdout
            if not test_ok:
                results["errors"].append(f"Test failures:\n{stderr}")
    
    return results


if __name__ == "__main__":
    # CLI interface for sandbox testing
    if len(sys.argv) < 2:
        print("Usage: python sandbox.py <tool_name> [--skip-tests]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    skip_tests = "--skip-tests" in sys.argv
    
    results = validate_new_tool(tool_name, run_tests=not skip_tests)
    
    print(json.dumps(results, indent=2))
    
    # Exit with error if validation failed
    if not results["syntax_valid"] or (not skip_tests and not results["tests_passed"]):
        sys.exit(1)