#!/bin/bash
# CogniMap Visualization Launcher

echo "🧠 CogniMap Visualization System"
echo "================================"
echo ""
echo "Choose an option:"
echo "1) Run Explorer (generates new graphs)"
echo "2) Open Dashboard (HTML view)"
echo "3) View Mermaid Diagram"
echo "4) Show Graph Statistics"
echo "5) Run Semantic Analysis (Enhanced)"
echo "6) Open Interactive Visualization"
echo "7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

case $choice in
    1)
        echo "Running explorer..."
        python3 "$SCRIPT_DIR/visualizer/scripts/explorer.py"
        ;;
    2)
        echo "Opening dashboard..."
        if command -v firefox &> /dev/null; then
            firefox "$SCRIPT_DIR/visualizer/frontend/dashboard.html" &
        elif command -v google-chrome &> /dev/null; then
            google-chrome "$SCRIPT_DIR/visualizer/frontend/dashboard.html" &
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$SCRIPT_DIR/visualizer/frontend/dashboard.html" &
        else
            echo "Please open: $SCRIPT_DIR/visualizer/frontend/dashboard.html"
        fi
        ;;
    3)
        echo "Mermaid Diagram:"
        echo "================"
        if [ -f "$SCRIPT_DIR/visualizer/output/architecture.mmd" ]; then
            head -50 "$SCRIPT_DIR/visualizer/output/architecture.mmd"
            echo ""
            echo "Full diagram at: $SCRIPT_DIR/visualizer/output/architecture.mmd"
            echo "Copy and paste at: https://mermaid.live/"
        else
            echo "No diagram found. Run explorer first (option 1)."
        fi
        ;;
    4)
        echo "Graph Statistics:"
        echo "================="
        if [ -f "$SCRIPT_DIR/visualizer/output/architecture_graph.json" ]; then
            echo -n "Total Nodes: "
            jq '.nodes | length' "$SCRIPT_DIR/visualizer/output/architecture_graph.json"
            echo -n "Total Edges: "
            jq '.edges | length' "$SCRIPT_DIR/visualizer/output/architecture_graph.json"
            echo ""
            echo "Component Types:"
            jq '.nodes | group_by(.type) | map({type: .[0].type, count: length})' "$SCRIPT_DIR/visualizer/output/architecture_graph.json"
        else
            echo "No graph data found. Run explorer first (option 1)."
        fi
        ;;
    5)
        echo "Running semantic analysis..."
        python3 "$SCRIPT_DIR/integrate_semantic.py"
        echo ""
        echo "✅ Semantic analysis complete!"
        echo "Use option 6 to view the enhanced visualization."
        ;;
    6)
        echo "Opening interactive visualization..."
        # Check if enhanced graph exists
        if [ -f "$SCRIPT_DIR/visualizer/output/architecture_graph_enhanced.json" ]; then
            echo "✅ Using enhanced graph with semantic data"
        else
            echo "⚠️  Enhanced graph not found. Run option 5 first for semantic features."
        fi
        
        # Start a simple HTTP server and open browser
        echo "Starting local server on port 8080..."
        cd "$SCRIPT_DIR/visualizer"
        python3 -m http.server 8080 &
        SERVER_PID=$!
        sleep 2
        
        if command -v firefox &> /dev/null; then
            firefox "http://localhost:8080/interactive.html" &
        elif command -v google-chrome &> /dev/null; then
            google-chrome "http://localhost:8080/interactive.html" &
        elif command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:8080/interactive.html" &
        else
            echo "Please open: http://localhost:8080/interactive.html"
        fi
        
        echo ""
        echo "Server running on PID: $SERVER_PID"
        echo "Press Ctrl+C to stop the server"
        wait $SERVER_PID
        ;;
    7)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again."
        ;;
esac