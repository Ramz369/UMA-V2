# COGPLAN Testing Issues Analysis

## Current Test Status
- **Total Test Files**: 33 Python files
- **Tests Collected**: 95 tests
- **Collection Errors**: 21 files with import errors
- **Pass Rate**: 65.7% (from last session report)
- **Target**: 80% pass rate

## Root Cause of Test Failures

### 1. Import Path Issues
All test files are using incorrect import paths after directory reorganization:
- **Current (Wrong)**: `from agents.codegen_agent import ...`
- **Should Be**: `from src.agents.codegen_agent import ...`

### 2. Files with Collection Errors (21 total)
**Agent Tests**:
- tests/test_codegen_agent.py
- tests/test_planner_agent.py
- tests/test_tool_hunter_agent.py
- tests/test_credit_sentinel.py
- tests/test_meta_analyst.py
- tests/test_session_summarizer.py
- tests/test_semantic_diff.py

**Tool Tests** (in tests/tools/):
- test_agent_chat.py
- test_brave-search.py
- test_code_executor.py
- test_data_connector.py
- test_document_loader.py
- test_filesystem.py
- test_function_wrapper.py
- test_github.py
- test_rag_pipeline.py
- test_slack.py
- test_sql_query.py
- test_sqlite.py
- test_vector_search.py
- test_web_search.py

### 3. Working Test Files
These tests don't have collection errors:
- tests/test_aether_sprint_0.py
- tests/test_aether_sprint_1.py
- tests/test_aether_sprint_2.py
- tests/test_garbage_flag.py
- tests/test_semloop_bootstrap.py
- tests/test_pilot_001_e2e.py
- tests/test_real_embeddings.py
- tests/test_har_analyzer.py
- tests/test_github_client.py
- tests/integration/test_all_components.py

### 4. Import Patterns to Fix

#### For Agent Tests:
```python
# Wrong:
from agents.codegen_agent import CodegenAgent
from tools.credit_sentinel_v2 import CreditSentinel

# Correct:
from src.agents.codegen_agent import CodegenAgent
from tools.credit_sentinel_v2 import CreditSentinel  # tools path is correct
```

#### For Tool Tests:
Tool imports need to be updated based on new ecosystem structure:
```python
# Wrong:
from tools.ecosystem.library.intelligence.agent_chat import AgentChat

# May need adjustment based on actual tool location
```

### 5. Test Infrastructure Issues

#### Missing Test Dependencies:
- pytest-asyncio warnings indicate async tests not properly marked
- Integration tests marked but pytest.mark.integration not registered

#### Configuration Needed:
- pytest.ini or pyproject.toml missing
- Need to register custom markers (asyncio, integration)
- Configure test paths properly

### 6. Storage Initialization Issues
From session report, tests are failing due to:
- Storage initialization problems
- Mock configurations not working
- Optional dependencies causing import errors

## Fix Strategy

### Phase 1: Fix Import Paths (Quick Win)
1. Update all test imports to use `src.agents.*` pattern
2. Verify tool imports match new ecosystem structure
3. Add __init__.py files where missing

### Phase 2: Configure pytest
1. Create pytest.ini with proper configuration
2. Register custom markers
3. Set PYTHONPATH for test discovery

### Phase 3: Fix Storage/Mock Issues
1. Ensure storage directory exists for tests
2. Fix mock configurations
3. Handle optional dependencies gracefully

### Phase 4: Run and Fix Remaining Issues
1. Run tests individually to identify specific failures
2. Fix any remaining import or initialization issues
3. Verify 80% pass rate achieved

## Commands for Testing
```bash
# Activate environment
source .venv/bin/activate

# Run all tests
python3 -m pytest tests/ -v

# Run with specific file
python3 -m pytest tests/test_specific.py -v

# Show collection errors
python3 -m pytest tests/ --co -q

# Run only working tests
python3 -m pytest tests/test_aether_sprint_0.py tests/test_garbage_flag.py -v
```

## Priority Order
1. Fix test_codegen_agent.py imports first (core functionality)
2. Fix test_planner_agent.py imports
3. Fix remaining agent tests
4. Fix tool tests
5. Verify integration tests still pass