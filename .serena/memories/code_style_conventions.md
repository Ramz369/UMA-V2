# COGPLAN Code Style and Conventions

## Python Code Style
- **Python Version**: 3.12
- **Import Style**: Absolute imports from src/
- **Type Hints**: Used in agent classes and core modules
- **Docstrings**: Present in main classes and methods
- **Class Names**: PascalCase (e.g., CodegenAgent, PlannerAgent)
- **Function Names**: snake_case
- **Constants**: UPPER_SNAKE_CASE

## Project Structure
```
COGPLAN/
├── src/agents/          # Core agent implementations
├── tests/              # Test files (test_*.py pattern)
├── tools/              # Tool implementations
├── services/           # Service layer
├── infra/              # Infrastructure configs (Docker)
├── scripts/            # Utility scripts
├── docs/               # Documentation
├── config/             # Configuration files
├── storage/            # Storage layer
├── schemas/            # Data schemas
└── requirements/       # Dependency files
```

## Testing Conventions
- Test files: `test_*.py` pattern
- Test classes: `TestClassName`
- Test methods: `test_method_name`
- Fixtures in conftest.py files
- Use pytest markers: @pytest.mark.integration, @pytest.mark.asyncio

## Agent Development Patterns
- Agents inherit from base classes
- Use dependency injection for services
- Implement standard interfaces (execute, validate, etc.)
- Credit management built into agent operations
- Boundary enforcement at agent level

## Error Handling
- Comprehensive try-except blocks in agents
- Structured error logging
- Graceful degradation for missing dependencies
- Return meaningful error messages

## Documentation
- README.md files in major directories
- Architectural decisions in docs/
- Session handover documents in docs/progress/
- Roadmap tracking in ROADMAP.md