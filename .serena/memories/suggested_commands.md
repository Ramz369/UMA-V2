# COGPLAN Development Commands

## Essential Commands

### Environment Setup
```bash
# Navigate to project
cd /home/ramz/Documents/adev/COGPLAN

# Activate virtual environment (CRITICAL - always do this first)
source .venv/bin/activate

# Verify Python version (must be 3.12)
python3 --version
```

### Testing Commands
```bash
# Run all tests with verbose output
python3 -m pytest tests/ -v

# Run tests with short traceback (easier to read)
python3 -m pytest tests/ -v --tb=short

# Run tests with coverage
python3 -m pytest tests/ --cov --cov-report=term

# Run unit tests only
python3 -m pytest tests/ -v -m "not integration"

# Run integration tests
python3 -m pytest tests/ -v -m "integration"

# Stop at first failure
python3 -m pytest tests/ -x

# Run specific test file
python3 -m pytest tests/test_specific.py -v
```

### SemLoop Stack Management
```bash
# Start SemLoop services (MinIO, Redpanda, PostgreSQL, Redis)
make semloop-up

# Stop SemLoop services
make semloop-down

# Check health of services
make semloop-health
# or
python3 scripts/semloop_health.py
```

### Git Commands
```bash
# Check status
git status
git branch

# View recent commits
git log --oneline -10

# View diff with main branch
git diff main..phase-4.8-critical-fixes

# Create PR using GitHub CLI
gh pr list
gh pr create
```

### Utility Commands
```bash
# Clean generated files and caches
make clean

# Find Python files
find . -name "*.py" -type f

# Count test files
find tests/ -name "*.py" -type f | wc -l

# Check for running processes on a port
lsof -i :PORT
```

## CRITICAL NOTES
1. **ALWAYS use python3**, never just "python" (system has no python alias)
2. **ALWAYS activate .venv** before running Python commands
3. **Test commands** must be run from project root with .venv activated
4. **SemLoop stack** requires Docker to be running