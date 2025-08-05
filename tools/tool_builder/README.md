# Tool Builder System

The tool-builder agent enables autonomous creation and testing of new micro-tools for the UMA-V2 system.

## Features

- **Autonomous Tool Generation**: Agent creates production-ready Python tools
- **Sandboxed Testing**: All new tools are tested in Docker containers
- **Unit Test Generation**: Comprehensive test suites created automatically
- **CI Integration**: GitHub Actions validates new tools on PRs

## Usage

### Via Agent (Recommended)

```
/use tool-builder:
  create a new tool called "json_validator" that validates JSON schemas
  include comprehensive unit tests
```

### Manual Testing

Test a tool in the sandbox:

```bash
python tools/tool_builder/sandbox.py semantic_diff
```

Skip tests (syntax check only):

```bash
python tools/tool_builder/sandbox.py semantic_diff --skip-tests
```

## Workflow

1. **Request**: User requests new tool via `/use tool-builder:`
2. **Generation**: Agent creates tool in `tools/` and tests in `tests/`
3. **Validation**: Sandbox runs tests in Docker container
4. **CI Check**: GitHub Actions validates on PR
5. **Merge**: Tool becomes available to all agents

## Sandbox Environment

The sandbox provides:
- Isolated Docker container (Python 3.12)
- Common dependencies pre-installed
- pytest test runner
- 60-second timeout protection
- Syntax validation

## CI Integration

PRs with new tools trigger sandbox testing:
- Detects new/modified Python files in `tools/`
- Runs each tool's tests in Docker
- Blocks merge if tests fail
- Add `new-tool` label to force testing

## Directory Structure

```
tools/
├── tool_builder/
│   ├── __init__.py
│   ├── sandbox.py      # Sandbox harness
│   └── README.md       # This file
├── semantic_diff.py    # Example tool
└── har_analyzer.py     # Example tool

tests/
├── test_semantic_diff.py  # Example tests
└── test_har_analyzer.py   # Example tests
```

## Quality Standards

All generated tools must have:
- Type hints on all functions
- Comprehensive error handling
- 80%+ test coverage
- Docstrings and examples
- CLI interface when appropriate
- JSON I/O for agent compatibility

## Credit Management

The tool-builder agent has a 180 credit soft cap:
- Checkpoints at 80 and 160 credits
- Aborts if approaching limit
- Summarizes progress at each checkpoint

## Security

- Tools run in isolated containers
- No network access during tests
- 60-second execution timeout
- Read-only access to system files
- Validated syntax before execution