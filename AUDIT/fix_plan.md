# Fix Plan

1. tools/ecosystem/library/foundation/code_executor.py ➜ replace JSON literals with Python `True`/`None` ➜ fix ruff F821 and enable imports ➜ 10m
2. requirements-dev.txt ➜ add `jsonschema`, `pytest-asyncio` ➜ satisfy tests needing schema & async support ➜ 5m
3. .github/workflows/ci.yml ➜ run ruff, mypy, bandit, pytest-cov ➜ ensure unified CI pipeline ➜ 15m
