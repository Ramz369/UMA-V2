# Testing Status Report

**Generated**: 2025-08-07T05:31:14.003763

## Summary

- **Total Components**: 32
- **Passed**: 12 (37.5%)
- **Failed**: 16
- **Skipped**: 4

## Detailed Results

### Evolution Engine

| Component | Status | Details |
|-----------|--------|----------|
| evolution.agents.auditor_agent | SKIP | Import error: No module named 'evolution.agents.auditor_agent' |
| evolution.agents.reviewer_agent | SKIP | Import error: No module named 'evolution.agents.reviewer_agent' |
| evolution.agents.architect_agent | PASS | Module structure valid |
| evolution.agents.implementor_agent | PASS | Module structure valid |
| evolution.agents.treasurer_agent | PASS | Module structure valid |
| evolution.orchestrator | FAIL | cannot import name 'EvolutionOrchestrator' from 'evolution.orchestrator.evo_orchestrator_wired' (/home/ramz/Documents/adev/COGPLAN/evolution/orchestrator/evo_orchestrator_wired.py) |
| evolution.runtime | FAIL | AgentRuntime.__init__() got an unexpected keyword argument 'agent_name' |
| script.setup_evolution | SKIP | Script not found |
| script.start_evolution | PASS | Script exists |

### Aether Protocol

| Component | Status | Details |
|-----------|--------|----------|
| aether.intent_substrate | FAIL | No module named 'asyncpg' |
| aether.polarity_calculator | PASS | Polarity: 0.0 |
| aether.polarity_embedder | FAIL | PolarityAwareEmbedder.__init__() got an unexpected keyword argument 'threshold' |
| aether.karmic_orchestrator | PASS | Karmic system initialized |
| aether.karma_runtime | PASS | Karma tracking: 0.1 |
| aether.resonance_analyzer | PASS | Pattern detected: standing_wave |
| aether.unified_field | PASS | Consciousness: 79.8% (CONSCIOUS) |
| integration.evolution_aether | FAIL | No module named 'asyncpg' |

### Core Agents

| Component | Status | Details |
|-----------|--------|----------|
| agents.planner | FAIL | 'TaskPlan' object has no attribute 'get' |
| agents.codegen | FAIL | 'CodegenAgent' object has no attribute 'generate_api' |
| agents.tool_hunter | FAIL | ToolHunterAgent.__init__() takes 1 positional argument but 2 were given |

### Tools & Services

| Component | Status | Details |
|-----------|--------|----------|
| tools.credit_sentinel | FAIL | CreditSentinel.__init__() got an unexpected keyword argument 'checkpoint_dir' |
| tools.semantic_diff | FAIL | No module named 'sqlparse' |
| tools.har_analyzer | FAIL | HARAnalyzer.__init__() missing 1 required positional argument: 'har_path' |
| services.embedder | FAIL | cannot import name 'Embedder' from 'services.embedder' (/home/ramz/Documents/adev/COGPLAN/services/embedder.py) |
| tools.session_summarizer | FAIL | 'SessionSummarizer' object has no attribute 'summarize' |

### Infrastructure

| Component | Status | Details |
|-----------|--------|----------|
| docker.docker-compose | SKIP | File not found |
| docker.semloop-stack | PASS | Configuration exists |
| docker.docker-compose.evo | PASS | Configuration exists |

### Integration

| Component | Status | Details |
|-----------|--------|----------|
| integration.agent_karma | PASS | Karma-aware agents work |

## ⚠️ Critical Issues

- **evolution.orchestrator**: cannot import name 'EvolutionOrchestrator' from 'evolution.orchestrator.evo_orchestrator_wired' (/home/ramz/Documents/adev/COGPLAN/evolution/orchestrator/evo_orchestrator_wired.py)
- **evolution.runtime**: AgentRuntime.__init__() got an unexpected keyword argument 'agent_name'
- **aether.intent_substrate**: No module named 'asyncpg'
- **aether.polarity_embedder**: PolarityAwareEmbedder.__init__() got an unexpected keyword argument 'threshold'
- **agents.planner**: 'TaskPlan' object has no attribute 'get'
- **agents.codegen**: 'CodegenAgent' object has no attribute 'generate_api'
- **agents.tool_hunter**: ToolHunterAgent.__init__() takes 1 positional argument but 2 were given
- **tools.credit_sentinel**: CreditSentinel.__init__() got an unexpected keyword argument 'checkpoint_dir'
- **tools.semantic_diff**: No module named 'sqlparse'
- **tools.har_analyzer**: HARAnalyzer.__init__() missing 1 required positional argument: 'har_path'
- **services.embedder**: cannot import name 'Embedder' from 'services.embedder' (/home/ramz/Documents/adev/COGPLAN/services/embedder.py)
- **tools.session_summarizer**: 'SessionSummarizer' object has no attribute 'summarize'
- **schemas.events**: No module named 'schemas.events'
- **schemas.agent_events**: No module named 'schemas.agent_events'
- **schemas.credit_events**: No module named 'schemas.credit_events'
- **integration.evolution_aether**: No module named 'asyncpg'

## Recommendations

1. Fix failing components before deployment
2. Investigate skipped components for missing dependencies
3. Improve test coverage to reach 80% pass rate
