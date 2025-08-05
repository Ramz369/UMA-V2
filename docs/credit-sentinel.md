# Credit Sentinel v2 Documentation

The Credit Sentinel provides real-time monitoring and throttling of agent credit/token usage with wall-time limits and deadlock detection.

## Features

- **Real-time Monitoring**: Track credits, tokens, and wall-time per agent
- **Multi-level Throttling**: ALLOW → WARN → THROTTLE → ABORT progression
- **Automatic Checkpointing**: Save state every 50 credits
- **Wall-time Protection**: Prevent runaway agents (45s-120s limits)
- **Deadlock Detection**: Identify and resolve file lock cycles
- **Metrics Export**: JSON endpoint for meta-analyst consumption
- **CSV Logging**: Detailed audit trail in `schemas/metrics_v2.csv`

## Architecture

```
┌─────────────────────────────────────┐
│         Credit Sentinel v2          │
├─────────────────────────────────────┤
│  • Global Hard Cap: 1000 credits    │
│  • Checkpoint Interval: 50 credits  │
│  • Wall-time Monitor Thread         │
│  • Lock Graph Manager               │
└─────────────────────────────────────┘
          │                │
    ┌─────▼──────┐   ┌─────▼──────┐
    │   Agents   │   │   Metrics   │
    ├────────────┤   ├─────────────┤
    │ • planner  │   │ • CSV log   │
    │ • codegen  │   │ • JSON API  │
    │ • tester   │   │ • Real-time │
    └────────────┘   └─────────────┘
```

## Usage

### Python API

```python
from tools.credit_sentinel_v2 import get_sentinel, track_tool_call

# Track a tool call
action = track_tool_call("my-agent", "my-tool", credits=5, tokens=500)
print(f"Sentinel action: {action}")  # "allow", "warn", "checkpoint", etc.

# Get metrics
sentinel = get_sentinel()
metrics = sentinel.get_metrics()
print(f"Total credits used: {metrics['global']['total_credits']}")
```

### CLI Interface

```bash
# Start tracking an agent
python tools/credit_sentinel_v2.py start my-agent

# Track a tool call
python tools/credit_sentinel_v2.py track my-agent my-tool 10 1000

# Get current metrics
python tools/credit_sentinel_v2.py metrics
```

## Configuration

Edit `config/sentinel.yaml` to adjust:

```yaml
global_hard_cap: 1000        # Total system credits
checkpoint_interval: 50       # Credits between saves

agent_caps:
  planner: 50                # Per-agent limits
  codegen: 150
  tool-builder: 180

wall_time_limits:
  default: 45000             # 45 seconds
  container_runner: 60000    # 60 seconds
```

## Throttle Actions

| Action | Trigger | Effect |
|--------|---------|--------|
| **ALLOW** | < 80% of cap | Normal operation |
| **WARN** | 80-90% of cap | Log warning, continue |
| **THROTTLE** | 90-95% of cap | Slow operations |
| **CHECKPOINT** | Every 50 credits | Save agent state |
| **ABORT** | > 100% cap or timeout | Terminate agent |

## Lock Management

The sentinel prevents deadlocks through:

1. **Lock Graph Tracking**: Monitor which agent holds which file
2. **Cycle Detection**: Identify A→B→A lock cycles
3. **Resolution Strategy**: Abort youngest lock holder

## Metrics Endpoint

Access real-time metrics at `/metrics` or via:

```python
from tools.credit_sentinel_v2 import get_metrics_json

metrics_json = get_metrics_json()
# Returns JSON with global stats, per-agent breakdown, locks, etc.
```

## CSV Audit Log

All tool calls are logged to `schemas/metrics_v2.csv`:

```csv
team_id,timestamp,agent,tokens,credits,wall_time_ms,model,tool_call,exit_status
default,2024-01-01T10:00:00,planner,100,1,1234,claude-3,Think,allow
default,2024-01-01T10:00:01,codegen,500,5,2345,claude-3,Writer,checkpoint
```

## Integration with Agents

Agents should check sentinel response:

```python
action = track_tool_call(agent_name, tool_name, credits, tokens)

if action == "abort":
    # Clean up and exit
    return
elif action == "throttle":
    # Add delay before next operation
    time.sleep(1)
elif action == "checkpoint":
    # Save current state
    save_checkpoint()
```

## Monitoring Best Practices

1. **Set Realistic Caps**: Base on historical usage + 20% buffer
2. **Monitor Wall-time**: Especially for I/O operations
3. **Review Metrics Daily**: Use meta-analyst for trends
4. **Tune Checkpoints**: Balance between safety and overhead
5. **Test Deadlock Scenarios**: Ensure resolution works

## Troubleshooting

### Agent Aborted Unexpectedly
- Check `schemas/metrics_v2.csv` for exit_status
- Review wall-time limits in config
- Verify credit cap is appropriate

### Deadlock Detected
- Check lock graph in metrics JSON
- Review abort strategy in `config/lock_graph.yaml`
- Consider refactoring to reduce lock contention

### High Credit Usage
- Enable more frequent checkpoints
- Reduce per-agent caps
- Review tool call patterns in CSV log

## Future Enhancements

- [ ] Predictive throttling based on usage patterns
- [ ] Dynamic cap adjustment via meta-analyst
- [ ] Distributed sentinel for multi-node systems
- [ ] GraphQL API for metrics queries
- [ ] Real-time dashboard UI