# Storage Migration Guide

## Overview

This guide outlines the migration path from current file-based storage to the full SemLoop stack.

## Current State (Phase 1)

We're currently using simple file-based storage:

- **Session Summaries**: `schemas/session_summary.yaml`
- **Metrics**: `schemas/metrics_v2.csv`
- **Agent Manifests**: `agents/*.md`
- **Tool Definitions**: `tools/*.py`
- **Test Results**: Local pytest output

This approach is perfect for getting started but lacks:
- Historical querying
- Semantic search
- Real-time streaming
- Distributed access

## Hybrid Mode (Phase 2)

Transition period where we write to both systems:

1. **Keep existing file writes** (for backward compatibility)
2. **Add SemLoop event emission** in parallel
3. **Gradually migrate readers** to use SemLoop

### Setup
```bash
# Start local SemLoop stack
docker-compose -f infra/semloop-stack.yml up -d

# Verify services are running
docker-compose -f infra/semloop-stack.yml ps
```

### Code Changes
```python
# In session_summarizer.py
def save_summary(summary):
    # Existing: Save to YAML
    save_to_yaml(summary)
    
    # New: Also emit to SemLoop
    if SEMLOOP_ENABLED:
        emit_event(EventEnvelope(
            type="session_summary",
            agent="session-summarizer",
            payload=summary
        ))
```

## Full SemLoop (Phase 3)

Complete migration to event-driven architecture:

### Components
- **Event Bus**: Redpanda at `localhost:9092`
- **Object Store**: MinIO at `localhost:9000`
- **Vector DB**: PostgreSQL + pgvector at `localhost:5432`
- **Cache**: Redis at `localhost:6379`

### File System Role
- **Backup only**: Keep YAML/CSV as disaster recovery
- **Local cache**: Speed up agent startup
- **Config files**: Still read from disk

### Migration Checklist

- [ ] Deploy `infra/semloop-stack.yml`
- [ ] Update agents to use `EventEnvelope` schema
- [ ] Migrate historical data (optional)
- [ ] Switch readers to LlamaIndex queries
- [ ] Set up retention policies
- [ ] Configure backups to S3/GCS

## Quick Start

```bash
# 1. Start the stack (requires Docker)
cd infra
docker-compose -f semloop-stack.yml up -d

# 2. Run health checks
./scripts/health_check.sh

# 3. Test event emission
python tools/test_semloop_connection.py

# 4. View events in MinIO console
open http://localhost:9001  # admin:minioadmin
```

## Storage Paths

### Current (File-based)
```
COGPLAN/
├── schemas/
│   ├── session_summary.yaml      # Latest session
│   └── metrics_v2.csv           # Credit/token metrics
├── reports/
│   └── meta/                    # Meta-analyst reports
└── checkpoints/                 # Agent state snapshots
```

### Future (SemLoop)
```
MinIO Buckets:
├── agent-events/                # Raw events
│   └── 2024/01/01/             # Date partitioned
├── session-summaries/           # Session snapshots
├── artifacts/                   # Large files
└── checkpoints/                # State backups

PostgreSQL Tables:
├── events                      # Structured event data
├── event_embeddings           # Vector embeddings
└── agent_metrics              # Aggregated metrics

Redis Keys:
├── session:{id}               # Active session state
├── metrics:{agent}            # Real-time metrics
└── locks:{file}               # Distributed locks
```

## Benefits of Migration

### Phase 1 → Phase 2
- Start collecting historical data
- Enable real-time monitoring
- Test SemLoop without breaking changes

### Phase 2 → Phase 3
- Full semantic search over all events
- Distributed agent coordination
- Sub-second query performance
- Automatic data lifecycle management

## Rollback Plan

If issues arise during migration:

1. **Phase 2 → Phase 1**: Disable `SEMLOOP_ENABLED` flag
2. **Phase 3 → Phase 2**: Switch readers back to file-based
3. **Emergency**: All data is backed up to files regardless

## Support

- **SemLoop Issues**: Check `infra/semloop-stack.yml` logs
- **Migration Help**: See `docs/semloop-architecture.md`
- **Performance Tuning**: Adjust `config/semloop.yaml`

## Next Steps

1. Review the [SemLoop Architecture](../docs/semloop-architecture.md)
2. Start Phase 2 by running `docker-compose -f infra/semloop-stack.yml up`
3. Monitor metrics in `reports/meta/` for migration progress