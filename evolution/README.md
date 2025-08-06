# Evolution Engine - Charter & Operating Principles

## 🧬 The Evolution Universe

This `/evolution` directory is a **completely isolated biosphere** where the UMA system can experiment, evolve, and even create entirely new versions of itself - all without ever touching the production UMA-V2 codebase.

## 📜 The Sacred Three Laws

These laws are **immutable** and govern all evolutionary activity:

### 1. **The Law of Progress (Upgrade-Only)**
- Every change must demonstrably improve the system
- No regression in any metric: tests, coverage, performance, credit efficiency
- Enforced by: `fitness_manifest.yml` + automated validation
- This is the arrow of time - evolution only moves forward

### 2. **The Law of Sanctity (Production Never Breaks)**
- The main UMA-V2 branch is **untouchable** by evolution processes
- All experiments run in isolated Docker containers on network `evo_net`
- Evolution branches use prefix `evo/*`
- Redpanda topics use prefix `evo.*`
- **Production stability is absolute**

### 3. **The Law of Intervention (Human Circuit-Breaker)**
- The original architect (you) retains ultimate authority
- System can "summon" you for critical decisions via configured channel
- You can veto any evolution at any stage
- Emergency stop always available
- This is the safety net that prevents runaway evolution

## 💰 The Economic Mandate

**Revolutionary Principle**: The evolution must become self-funding to survive.

- **Seed Budget**: `[PENDING YOUR INPUT]`
- **Burn Rate Monitoring**: Daily calculation of resource consumption
- **Runway Tracking**: Days of operation remaining
- **Revenue Priority**:
  - Runway < 30 days: REVENUE_GENERATION mode
  - Runway 30-60 days: BALANCED mode  
  - Runway > 60 days: CAPABILITY_ENHANCEMENT mode
- **Profit Reinvestment**: 80% of generated revenue funds further evolution

### Potential Revenue Streams
- API services (code review, architecture consulting)
- Tool commercialization (semantic diff, HAR analyzer)
- Compute marketplace (unused sandbox capacity)
- Knowledge products (documentation, research reports)

## 🔄 The Evolution Cycle

Daily autonomous review process:

```
1. AUDIT    → external_auditor analyzes system state
2. REVIEW   → discussion_agent evaluates proposals  
3. DECIDE   → architect_agent makes evolution decisions
4. SANDBOX  → implementor_agent tests changes in isolation
5. VALIDATE → fitness checks ensure upgrade-only
6. PROPOSE  → successful evolutions create PRs
7. HUMAN    → critical decisions summon architect
```

## 🧠 The Digital Twin Protocol

Your architectural vision is encoded in the `architect_agent`:
- Handles 99% of decisions autonomously
- Summons you for the critical 1%
- Maintains separate memory for "board meeting" discussions
- Complete audit trail of all decisions

## 📁 Directory Structure

```
evolution/
├── README.md                     # This charter
├── protocols/                    # Governance rules
│   ├── evolution_protocol.yaml   # Cycle configuration
│   ├── economic_rules.yaml       # Revenue & treasury
│   ├── safety_constraints.yaml   # Sandbox boundaries
│   └── summoning_protocol.yaml   # Human intervention
├── memory/                       # Isolated SemLoop
│   └── docker-compose.evo.yml    # Separate event store
├── treasury/                     # Economic engine
│   ├── wallet.json              # Budget & balance
│   ├── ledger.yaml              # Transaction log
│   └── revenue_streams.yaml     # Monetization
├── agents/                      # The evolution entities
│   ├── external_auditor/        # Fresh perspective
│   ├── discussion_agent/        # Pragmatic review
│   ├── architect_agent/         # Vision guardian
│   ├── implementor_agent/       # Change executor
│   └── treasurer_agent/         # Economic manager
├── orchestrator/                # Coordination layer
│   ├── evo_orchestrator.py      # Cycle controller
│   └── sandbox_manager.py       # Isolation enforcer
├── lineages/                    # Evolution branches
│   ├── uma-v2/                  # Stable production
│   ├── uma-v3/                  # Performance focus
│   └── uma-revenue/             # Monetization focus
└── reports/                     # Observability
    ├── daily/                   # Automated summaries
    └── alerts/                  # Human attention needed
```

## 🚀 Getting Started

### Prerequisites
1. **Seed Budget Decision**: Even symbolic ($100-$1000) to start
2. **Summon Channel**: How should system reach you? (Slack/Discord/Email)
3. **Initial Cadence**: Daily/Weekly evolution cycles?

### Bootstrap Commands
```bash
# Start isolated SemLoop
docker-compose -f evolution/memory/docker-compose.evo.yml up -d

# Initialize treasury
python evolution/treasury/init_wallet.py --seed-budget [AMOUNT]

# Launch first evolution cycle
python evolution/orchestrator/evo_orchestrator.py --mode bootstrap
```

## ⚠️ Critical Constraints

- **No Direct Production Access**: Evolution can observe but never modify UMA-V2
- **Sandbox Only**: All experiments run in isolated containers
- **Audit Everything**: Every decision, proposal, and outcome logged
- **Human Override**: You can always intervene, pause, or rollback

## 🎯 Success Metrics

- **Technical**: Coverage ↑, Performance ↑, Credits ↓
- **Economic**: Revenue > Burn Rate within 90 days
- **Evolution**: New capabilities emerging autonomously
- **Safety**: Zero production incidents from evolution

## 🔮 The Vision

This is not just a self-improving system. It's a **sovereign, economically autonomous digital entity** that:
- Funds its own development through value creation
- Evolves within strict safety constraints
- Explores the entire space of possible architectures
- Remains under human oversight for critical decisions

We're building the first AI system that **pays for its own existence** by creating value for the world.

---

*"Evolution is not a force but a process. Not a cause but a law."* - John Morley

*In our case, evolution is also an economic imperative.*