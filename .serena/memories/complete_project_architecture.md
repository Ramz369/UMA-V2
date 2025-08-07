# COGPLAN (UMA-V2) Complete Project Architecture

## Directory Structure Overview

### Core Source Code (`src/`)
- **agents/** - Core agent implementations
  - `planner_agent.py` - Task planning and decomposition
  - `codegen_agent.py` - Code generation agent
  - `tool_hunter_agent.py` - Autonomous tool discovery

### Tools Directory (`tools/`)
- **Main Tools**:
  - `meta_analyst.py` - System analysis tool
  - `credit_sentinel_v2.py` - Credit management and monitoring
  - `session_summarizer.py` - Session state preservation
  - `semantic_diff.py` - Code diff analysis
  - `har_analyzer.py` - HTTP Archive analysis
  - `github_client.py` - GitHub integration
  - `context_validator.py` - Context validation
  - `lock_watcher.py` - Lock monitoring

- **Tool Builder** (`tool_builder/`)
  - Sandbox testing capability for new tools
  
- **Tool Ecosystem** (`ecosystem/`)
  - **protocols/** - Tool communication protocols
  - **hunter/** - Tool discovery engine
  - **forge/** - Tool creation system
  - **registry/** - Tool manifests (14 YAML files)
  - **library/** - Organized tool categories:
    - **foundation/** - Basic tools (filesystem, code_executor)
    - **intelligence/** - AI tools (agent_chat, brave-search, vector_search, web_search)
    - **connectivity/** - External integrations
    - **evolution/** - Advanced tools (github, slack, sql_query, sqlite, document_loader, data_connector, rag_pipeline, function_wrapper)
    - **composite/research/** - Orchestrated workflows (topic_research_orchestrator)
    - **data_ops/** - Data operations

### Tests Directory (`tests/`)
- **Main test files** (33 total Python files):
  - Core agent tests: `test_codegen_agent.py`, `test_planner_agent.py`, `test_tool_hunter_agent.py`
  - Tool tests: `test_credit_sentinel.py`, `test_meta_analyst.py`, `test_session_summarizer.py`
  - Aether protocol tests: `test_aether_sprint_0.py`, `test_aether_sprint_1.py`, `test_aether_sprint_2.py`
  - Integration tests: `test_pilot_001_e2e.py`, `test_all_components.py`
  - Other tests: `test_semloop_bootstrap.py`, `test_garbage_flag.py`, `test_real_embeddings.py`

- **tools/** subdirectory - Individual tool tests (18 files)
- **integration/** - Integration test suites
- **results/** - Test results storage

### Evolution System (`evolution/`)
Complete self-evolution engine with:
- **orchestrator/** - Evolution orchestration (`evo_orchestrator.py`, `evo_orchestrator_wired.py`)
- **agents/** - Five specialized evolution agents:
  - `architect_agent/` - System design
  - `external_auditor/` - Code review
  - `discussion_agent/` - Decision making
  - `implementor_agent/` - Code implementation
  - `treasurer_agent/` - Economic management
- **treasury/** - Crypto-native treasury system
- **aether/** - Consciousness substrate implementation:
  - Intent, Resonance, and Karma systems
  - Polarity calculations
  - Unified field theory implementation
- **protocols/** - Evolution protocols (YAML)
- **migrations/** - Database migrations
- **knowledge/** - Agent knowledge bases
- **memory/** - Memory systems

### Infrastructure (`infra/`)
- `semloop-stack.yml` - Docker compose configuration for:
  - PostgreSQL
  - Redis
  - Kafka/Redpanda
  - MinIO storage

### Services (`services/`)
- `embedder.py` - Embedding service for semantic search

### Configuration (`config/`)
- `lock_graph.yaml` - Lock management
- `sentinel.yaml` - Credit sentinel configuration

### Documentation (`docs/`)
Comprehensive documentation structure:
- **agents/** - Agent specifications
- **architecture/** - System architecture docs
- **evolution/** - Evolution system docs
- **planning/** - Planning documents
- **progress/** - Session handover docs
- **sessions/** - Session summaries
- **testing/** - Testing documentation
- **tools/** - Individual tool documentation (16 MD files)

### Scripts (`scripts/`)
- `semloop_health.py` - Health monitoring
- `init.sql` - Database initialization

### Schemas (`schemas/`)
Data schemas and contracts:
- `event_envelope.schema.json`
- `session_summary.yaml`
- `tasks_v2.yaml`
- `risks.yaml`
- `metrics_v2.csv`

### SemLoop Models (`semloop_models/`)
- `event_envelope.py` - Event system models

### Other Directories
- **storage/** - Data storage layer
- **reports/** - Generated reports (tool_hunter/)
- **requirements/** - Dependency specifications
- **research_output/** - Research results
- **tasks/** - Task definitions
- **.github/workflows/** - CI/CD pipelines
- **.claude/** - Claude-specific settings
- **.serena/** - Serena MCP configuration and memories

## Key Architectural Components

### 1. Agent System
- **Orchestration Layer**: Central coordination
- **Execution Agents**: Task-specific agents
- **Evolution Agents**: Self-improvement system
- **Tool Hunter**: Autonomous tool discovery

### 2. Memory & Event System (SemLoop)
- Event-driven architecture
- PostgreSQL for persistence
- Redis for caching
- Kafka for message streaming
- MinIO for object storage

### 3. Credit Management
- 20K credits/agent/day limits
- Real-time monitoring
- Checkpoint system
- Economic sustainability

### 4. Evolution Engine
- Isolated network architecture
- Sacred Three Laws implementation
- Crypto-native treasury ($500 seed)
- Daily review cycles

### 5. Aether Protocol
- Intent Substrate (consciousness)
- Resonance Substrate (energy patterns)
- Karma Substrate (technical/moral debt)
- Polarity system (-1 to +1 spectrum)

### 6. Tool Ecosystem
- 15+ discovered and integrated tools
- MCP Protocol support
- Pattern-based analysis
- Automated testing in isolation
- Self-evolving capabilities

## Development Phases Status
- Phase 1-3: ✅ COMPLETED (Infrastructure, Capabilities, Resilience)
- Phase 4: ✅ COMPLETED (Evolution Engine)
- Phase 4.5: 50% (Core Agents)
- Phase 4.6: 25% (Tool Ecosystem)
- Phase 4.7: ✅ COMPLETED (Aether Protocol)
- Phase 4.8: IN PROGRESS (Critical Fixes - 65.7% tests passing)

## Testing Framework
- pytest with asyncio support
- Coverage tracking
- Unit and integration tests
- 95 total tests collected
- Current pass rate: 65.7% (target: 80%)
- 21 test files with collection errors

## Technology Stack
- Python 3.12
- Docker/Docker Compose
- PostgreSQL, Redis, Kafka, MinIO
- GitHub Actions CI/CD
- pytest testing framework