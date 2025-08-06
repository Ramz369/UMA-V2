#!/bin/bash
# Evolution Engine Startup Script

set -e

echo "=================================================="
echo "     EVOLUTION ENGINE STARTUP"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "evolution/.env.evolution" ]; then
    echo -e "${RED}Error: Must run from UMA-V2 root directory${NC}"
    exit 1
fi

# Parse arguments
MODE=${1:-mock}
CYCLE=${2:-test}

echo -e "${GREEN}Mode: $MODE${NC}"
echo -e "${GREEN}Cycle: $CYCLE${NC}"
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Function to start infrastructure
start_infrastructure() {
    echo -e "${YELLOW}Starting infrastructure...${NC}"
    
    # Check if containers are already running
    if [ "$MODE" == "live" ]; then
        check_docker
        
        # Start main SemLoop stack
        if docker-compose -f infra/semloop-stack.yml ps | grep -q "Up"; then
            echo "Main SemLoop stack already running"
        else
            echo "Starting main SemLoop stack..."
            docker-compose -f infra/semloop-stack.yml up -d
            sleep 10  # Wait for services to start
        fi
        
        # Start evolution-specific stack
        if docker-compose -f evolution/memory/docker-compose.evo.yml ps | grep -q "Up"; then
            echo "Evolution stack already running"
        else
            echo "Starting evolution stack..."
            docker-compose -f evolution/memory/docker-compose.evo.yml up -d
            sleep 10  # Wait for services to start
        fi
        
        echo -e "${GREEN}Infrastructure started${NC}"
    else
        echo -e "${YELLOW}Running in mock mode - no infrastructure needed${NC}"
    fi
}

# Function to check health
check_health() {
    echo -e "${YELLOW}Checking system health...${NC}"
    
    if [ "$MODE" == "live" ]; then
        # Check Kafka
        nc -zv localhost 9092 2>/dev/null && echo "✅ Kafka: OK" || echo "❌ Kafka: Not responding"
        
        # Check PostgreSQL
        nc -zv localhost 5433 2>/dev/null && echo "✅ PostgreSQL: OK" || echo "❌ PostgreSQL: Not responding"
        
        # Check Redis
        nc -zv localhost 6380 2>/dev/null && echo "✅ Redis: OK" || echo "❌ Redis: Not responding"
        
        # Check MinIO
        nc -zv localhost 9001 2>/dev/null && echo "✅ MinIO: OK" || echo "❌ MinIO: Not responding"
    else
        echo "✅ Mock mode: All services simulated"
    fi
    
    # Check wallet
    if [ -f "evolution/treasury/wallet.json" ]; then
        BALANCE=$(python3 -c "import json; print(json.load(open('evolution/treasury/wallet.json'))['balances']['USD'])")
        RUNWAY=$(python3 -c "import json; w=json.load(open('evolution/treasury/wallet.json')); print(int(w['balances']['USD']/w['burn_rate_daily']))")
        echo "✅ Wallet: \$${BALANCE} (${RUNWAY} days runway)"
        
        if [ $RUNWAY -lt 30 ]; then
            echo -e "${RED}⚠️  WARNING: Low runway!${NC}"
        fi
    else
        echo "❌ Wallet not found"
    fi
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running integration tests...${NC}"
    python3 evolution/test_integration.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Tests passed${NC}"
    else
        echo -e "${RED}Tests failed${NC}"
        exit 1
    fi
}

# Function to start orchestrator
start_orchestrator() {
    echo -e "${YELLOW}Starting Evolution Orchestrator...${NC}"
    
    if [ "$CYCLE" == "continuous" ]; then
        echo "Starting in continuous mode..."
        python3 evolution/orchestrator/evo_orchestrator_wired.py &
        ORCH_PID=$!
        echo "Orchestrator PID: $ORCH_PID"
        echo $ORCH_PID > evolution/.orchestrator.pid
        echo -e "${GREEN}Orchestrator running in background (PID: $ORCH_PID)${NC}"
    else
        echo "Running single test cycle..."
        python3 evolution/orchestrator/evo_orchestrator_wired.py
    fi
}

# Function to stop everything
stop_all() {
    echo -e "${YELLOW}Stopping Evolution Engine...${NC}"
    
    # Stop orchestrator if running
    if [ -f "evolution/.orchestrator.pid" ]; then
        PID=$(cat evolution/.orchestrator.pid)
        if ps -p $PID > /dev/null; then
            kill $PID
            echo "Stopped orchestrator (PID: $PID)"
        fi
        rm evolution/.orchestrator.pid
    fi
    
    # Stop Docker containers if requested
    if [ "$MODE" == "live" ]; then
        read -p "Stop Docker containers? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f evolution/memory/docker-compose.evo.yml down
            docker-compose -f infra/semloop-stack.yml down
            echo -e "${GREEN}Infrastructure stopped${NC}"
        fi
    fi
}

# Trap Ctrl+C
trap stop_all INT

# Main execution
case "$1" in
    start)
        start_infrastructure
        check_health
        run_tests
        start_orchestrator
        ;;
    test)
        MODE="mock"
        check_health
        run_tests
        ;;
    stop)
        stop_all
        ;;
    health)
        check_health
        ;;
    *)
        echo "Usage: $0 {start|test|stop|health} [live|mock] [test|continuous]"
        echo ""
        echo "Examples:"
        echo "  $0 test                # Run tests in mock mode"
        echo "  $0 start mock test     # Start in mock mode, single cycle"
        echo "  $0 start live test      # Start with Docker, single cycle"
        echo "  $0 start live continuous # Start with Docker, continuous operation"
        echo "  $0 stop                 # Stop everything"
        echo "  $0 health               # Check system health"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "     EVOLUTION ENGINE READY"
echo "=================================================="