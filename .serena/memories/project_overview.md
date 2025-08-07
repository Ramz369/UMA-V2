# COGPLAN (UMA-V2) Project Overview

## Project Purpose
UMA-V2 (Unified Multi-Agent Architecture v2) is a production-grade orchestration system for autonomous AI agents with:
- Strict boundary enforcement
- Credit management and economic sustainability
- Self-evolution capabilities
- Comprehensive monitoring and testing
- Real-world deployment readiness

## Tech Stack
- **Language**: Python 3.12
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Infrastructure**: Docker Compose
- **Databases**: PostgreSQL, Redis
- **Message Queue**: Kafka/Redpanda
- **Storage**: MinIO
- **CI/CD**: GitHub Actions
- **Virtual Environment**: .venv

## Architecture Components
1. **Agent Orchestration Layer**: Orchestrator, Planner, Integration, Session Summarizer
2. **Execution Agents**: Codegen, Test, Stress Tester, SLA Verifier, Tool Builder
3. **Monitoring & Control**: Credit Sentinel v2, Meta-Analyst v2, Risk Ledger, Immune System
4. **Memory & Event System**: SemLoop Stack with PostgreSQL, Redis, Kafka, Embedder Service
5. **Evolution Engine**: (Dormant) Evo Orchestrator with various sub-agents
6. **Infrastructure**: Docker Compose, GitHub Actions, Boundary Enforcement, Sandbox

## Current Status (Phase 4.8)
- **Branch**: phase-4.8-critical-fixes
- **Test Pass Rate**: 65.7% (target: 80%)
- **Focus**: Critical system fixes, test improvements
- **Main Issues**: 12 failing tests, storage initialization problems