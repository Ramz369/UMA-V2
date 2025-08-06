# SemLoop Stack Deployment Guide

## Quick Start

```bash
# Start the entire stack
make semloop-up

# Check health status
make semloop-health

# Stop and clean up
make semloop-down
```

## Services

### MinIO (Object Storage)
- **Port**: 9000 (API), 9001 (Console)
- **Credentials**: minioadmin/minioadmin
- **Console**: http://localhost:9001
- **Health**: http://localhost:9000/minio/health/ready

### Redpanda (Event Streaming)
- **Port**: 9092 (Kafka), 8081 (Schema Registry), 8082 (Pandaproxy)
- **Admin API**: http://localhost:9644
- **Topics**: Create with `docker exec semloop-redpanda rpk topic create <name>`

### PostgreSQL with pgvector
- **Port**: 5432
- **Database**: semloop
- **Credentials**: semloop/semloop123
- **Extensions**: pgvector (pre-installed)
- **Connect**: `PGPASSWORD=semloop123 psql -h localhost -U semloop -d semloop`

### Redis (Cache)
- **Port**: 6379
- **No authentication** (local dev)
- **Max Memory**: 256MB with LRU eviction
- **Connect**: `redis-cli -h localhost`

## Environment Variables

```bash
# For agents/tools connecting to SemLoop
export MINIO_ENDPOINT=http://localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin

export REDPANDA_BROKERS=localhost:9092
export SCHEMA_REGISTRY_URL=http://localhost:8081

export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=semloop
export POSTGRES_PASSWORD=semloop123
export POSTGRES_DB=semloop

export REDIS_HOST=localhost
export REDIS_PORT=6379
```

## Data Persistence

All data is stored in `./.semloop-data/` with subdirectories:
- `minio/` - Object storage buckets
- `redpanda/` - Event stream data
- `postgres/` - Database files
- `redis/` - Cache persistence (AOF)

## Health Check

Run `python scripts/semloop_health.py` to verify all services are healthy.

Expected output:
```
✅ MinIO        : Ready on port 9000
✅ Redpanda     : Kafka on 9092, Admin on 9644
✅ PostgreSQL   : Ready with pgvector extension
✅ Redis        : Ready on port 6379
```

## Troubleshooting

### Services not starting
```bash
# Check logs
docker compose -f infra/semloop-stack.yml logs

# Restart specific service
docker compose -f infra/semloop-stack.yml restart <service>
```

### Port conflicts
```bash
# Check what's using a port
lsof -i :9092

# Use different ports in .env file
echo "REDPANDA_PORT=19092" >> .env
```

### Cleanup
```bash
# Full reset
make semloop-down
rm -rf ./.semloop-data
make semloop-up
```