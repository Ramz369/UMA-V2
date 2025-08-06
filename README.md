# UMA-V2

Unified Multi-Agent Architecture v2 - A production-grade orchestration system for autonomous AI agents with strict boundary enforcement and credit management.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Ramz369/UMA-V2.git
cd UMA-V2

# Run tests
python -m pytest tests/

# Generate session summary
python tools/session_summarizer.py

# Check credit usage
python tools/credit_sentinel_v2.py metrics
```

## Architecture

- [SemLoop Stack](docs/semloop-architecture.md) - Event streaming and semantic memory infrastructure
- [Session Management](agents/session-summarizer.md) - Context preservation across agent reboots
- [Credit Control](docs/credit-sentinel.md) - Real-time throttling and resource management

## Core Components

### Agents (10 deployed)
- **Orchestration**: planner, integration-agent, session-summarizer
- **Development**: tool-builder, codegen, backend-tester, frontend-tester
- **Monitoring**: credit-sentinel, meta-analyst-v2, risk-ledger-agent
- **Specialized**: semantic-diff-agent, stress-tester, ui-journey-recorder

### Tools (9 operational)
- `credit_sentinel_v2.py` - Real-time credit/token monitoring
- `session_summarizer.py` - Canonical state snapshots
- `context_validator.py` - Pre-flight validation
- `github_client.py` - PR automation
- `semantic_diff.py` - AST-aware diffing
- `har_analyzer.py` - HTTP performance analysis
- `sandbox.py` - Docker-based tool testing
- `lock_watcher.py` - Deadlock detection

### CI/CD
- Boundary enforcement (planner restrictions)
- Sandbox testing for new tools
- Credit sentinel validation
- Session summary schema checks

## Project Stats

- **Lines of Code**: ~5,500
- **Test Coverage**: ~85%
- **Test Cases**: 105
- **CI Jobs**: 5 (boundary, sandbox, sentinel, session, integration)

## Roadmap

- [x] Tool-builder agent (PR #4)
- [x] Credit Sentinel v2 (PR #5)
- [x] Integration-Agent (PR #6)
- [x] Session-Summarizer (PR #7)
- [x] SemLoop architecture docs (PR #8)
- [ ] Nightly Meta-Analyst Action
- [ ] SemLoop stack deployment
- [ ] PILOT-001 end-to-end test
- [ ] Production deployment guide

## Development

### Running Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific component
python -m pytest tests/test_credit_sentinel.py -v

# With coverage
python -m pytest --cov=tools --cov-report=term
```

### Adding New Agents
1. Create manifest in `agents/[name].md`
2. Set appropriate soft_cap in `config/sentinel.yaml`
3. Add boundary checks if needed
4. Test with sandbox: `python tools/tool_builder/sandbox.py`

### Contributing
1. Branch from `main`
2. Follow naming: `feature/`, `fix/`, `docs/`
3. Include tests for new functionality
4. Update relevant documentation
5. CI must pass before merge

## License

MIT

## Support

Open issues at: https://github.com/Ramz369/UMA-V2/issues