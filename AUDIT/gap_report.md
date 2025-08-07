# Gap Report

- Missing `jsonschema` dependency causes schema tests to fail.
- Async tests lack `pytest-asyncio`; many tests skipped or error.
- Numerous ruff style violations and type annotation gaps.
- Security warnings from bandit (subprocess usage, asserts).
- CI lacks unified workflow for lint, type check, security, tests.
