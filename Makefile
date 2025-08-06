# UMA-V2 Makefile

.PHONY: help semloop-up semloop-down semloop-health test test-unit test-integration clean

help:
	@echo "UMA-V2 Development Commands"
	@echo ""
	@echo "SemLoop Stack:"
	@echo "  make semloop-up      - Start SemLoop stack (MinIO, Redpanda, PostgreSQL, Redis)"
	@echo "  make semloop-down    - Stop and clean SemLoop stack"
	@echo "  make semloop-health  - Check health of SemLoop services"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests (requires Docker)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Remove generated files and caches"

# SemLoop Stack Management
semloop-up:
	@echo "🚀 Starting SemLoop stack..."
	docker compose -f infra/semloop-stack.yml up -d
	@echo "⏳ Waiting for services to initialize (30s)..."
	@sleep 30
	@echo "🔍 Running health check..."
	@python scripts/semloop_health.py || echo "⚠️  Some services may still be initializing"

semloop-down:
	@echo "🛑 Stopping SemLoop stack..."
	docker compose -f infra/semloop-stack.yml down -v
	@echo "🧹 Cleaning up data directories..."
	rm -rf ./.semloop-data
	@echo "✅ SemLoop stack stopped and cleaned"

semloop-health:
	@python scripts/semloop_health.py

# Testing
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/ -v -m "not integration"

test-integration:
	python -m pytest tests/ -v -m "integration"

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf ./.semloop-data
	@echo "✅ Cleanup complete"