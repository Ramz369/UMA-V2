#!/bin/bash
# Serena MCP Server Setup Script for COGPLAN

set -e

echo "==================================="
echo "Serena MCP Server Installation"
echo "==================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Create tools directory if it doesn't exist
TOOLS_DIR="/home/ramz/Documents/adev/tools"
mkdir -p "$TOOLS_DIR"

# Clone Serena if not already cloned
SERENA_DIR="$TOOLS_DIR/serena"
if [ ! -d "$SERENA_DIR" ]; then
    echo "📥 Cloning Serena repository..."
    cd "$TOOLS_DIR"
    git clone https://github.com/oraios/serena
    echo "✅ Serena cloned successfully"
else
    echo "📥 Updating Serena repository..."
    cd "$SERENA_DIR"
    git pull
    echo "✅ Serena updated"
fi

# Create Serena config directory
SERENA_CONFIG_DIR="$HOME/.serena"
mkdir -p "$SERENA_CONFIG_DIR"

# Create global Serena configuration
echo "📝 Creating Serena global configuration..."
cat > "$SERENA_CONFIG_DIR/serena_config.yml" << 'EOF'
# Serena Global Configuration for COGPLAN
default_context: ide-assistant
default_project_path: /home/ramz/Documents/adev/COGPLAN

# Tool preferences
tools:
  semantic_search: true
  code_editing: true
  symbol_analysis: true
  refactoring: true
  
# Language servers to use
language_servers:
  python:
    enabled: true
    command: pylsp
  typescript:
    enabled: true
    command: typescript-language-server
EOF
echo "✅ Global configuration created"

# Create COGPLAN project configuration
COGPLAN_DIR="/home/ramz/Documents/adev/COGPLAN"
COGPLAN_SERENA_DIR="$COGPLAN_DIR/.serena"
mkdir -p "$COGPLAN_SERENA_DIR"

echo "📝 Creating COGPLAN project configuration..."
cat > "$COGPLAN_SERENA_DIR/project.yml" << 'EOF'
# COGPLAN Project Configuration for Serena
project_name: COGPLAN
project_type: python
description: "Unified Multi-Agent System with Consciousness"

# Language servers
language_servers:
  - python
  - typescript
  - yaml
  - json

# Directories to include
include_paths:
  - src/
  - evolution/
  - tools/
  - tests/
  - services/
  - schemas/

# Directories to exclude
exclude_paths:
  - .git/
  - __pycache__/
  - node_modules/
  - .venv/
  - .pytest_cache/
  - reports/
  - storage/

# Semantic search settings
semantic_search:
  index_symbols: true
  index_references: true
  index_definitions: true
  index_imports: true
  
# Code analysis settings
analysis:
  track_todos: true
  track_fixmes: true
  analyze_complexity: true
  dead_code_detection: true
EOF
echo "✅ COGPLAN project configuration created"

# Create Claude Desktop MCP configuration
CLAUDE_CONFIG_DIR="$HOME/.config/claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

echo "📝 Creating Claude Desktop MCP configuration..."
cat > "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "serena": {
      "command": "uv",
      "args": [
        "run",
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant"
      ],
      "env": {
        "SERENA_PROJECT_PATH": "/home/ramz/Documents/adev/COGPLAN"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/home/ramz/Documents/adev/COGPLAN"
      ]
    }
  }
}
EOF
echo "✅ Claude Desktop configuration created"

# Install Python language server if needed
if ! command -v pylsp &> /dev/null; then
    echo "📦 Installing Python language server..."
    pip install --user python-lsp-server[all] || echo "⚠️ Could not install pylsp, manual installation may be needed"
fi

echo ""
echo "==================================="
echo "✅ Serena Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Start Serena MCP server:"
echo "   cd $SERENA_DIR"
echo "   uv run serena start-mcp-server"
echo ""
echo "2. Or use with Claude Desktop (config already created)"
echo ""
echo "3. In your Claude session, start with:"
echo '   "Activate the project /home/ramz/Documents/adev/COGPLAN"'
echo ""
echo "Configuration files created:"
echo "  - ~/.serena/serena_config.yml"
echo "  - /home/ramz/Documents/adev/COGPLAN/.serena/project.yml"
echo "  - ~/.config/claude/claude_desktop_config.json"
echo ""
echo "For more details, see: docs/tools/SERENA_MCP_SETUP.md"