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
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

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
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again."
        ;;
esac