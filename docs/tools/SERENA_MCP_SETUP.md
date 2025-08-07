# Serena MCP Server Setup Guide for COGPLAN

## What is Serena?

Serena is a powerful coding agent toolkit that provides **semantic** code retrieval and editing capabilities through MCP (Model Context Protocol). Unlike other MCP servers that rely on text-based analysis, Serena uses Language Server Protocol (LSP) for true semantic understanding of code.

## Why Serena for COGPLAN?

1. **Semantic Code Understanding**: Analyzes code structure, not just text
2. **Large Codebase Navigation**: Perfect for COGPLAN's growing complexity
3. **MCP Integration**: Works seamlessly with Claude and other AI assistants
4. **Language Server Protocol**: Professional-grade code analysis

## Installation

### Prerequisites
```bash
# Install uv package manager if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Method 1: Local Installation (Recommended)
```bash
# Clone Serena repository
cd /home/ramz/Documents/adev/
git clone https://github.com/oraios/serena
cd serena

# Optional: Configure Serena
uv run serena config edit

# Start MCP server
uv run serena start-mcp-server
```

### Method 2: Direct Execution with uvx
```bash
# Run directly from GitHub
uvx --from git+https://github.com/oraios/serena serena start-mcp-server
```

### Method 3: Docker (Experimental)
```bash
docker run --rm -i --network host \
  -v /home/ramz/Documents/adev/COGPLAN:/workspaces/cogplan \
  ghcr.io/oraios/serena:latest \
  serena start-mcp-server --transport stdio
```

## Configuration

### 1. Global Configuration
Create/edit `~/.serena/serena_config.yml`:
```yaml
# Serena Global Configuration
default_context: ide-assistant
default_project_path: /home/ramz/Documents/adev/COGPLAN

# Tool preferences
tools:
  semantic_search: true
  code_editing: true
  symbol_analysis: true
  refactoring: true
```

### 2. COGPLAN Project Configuration
Create `/home/ramz/Documents/adev/COGPLAN/.serena/project.yml`:
```yaml
# COGPLAN Project Configuration for Serena
project_name: COGPLAN
project_type: python
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

# Directories to exclude
exclude_paths:
  - .git/
  - __pycache__/
  - node_modules/
  - .venv/

# Semantic search settings
semantic_search:
  index_symbols: true
  index_references: true
  index_definitions: true
```

## Using Serena with Claude

### Step 1: Configure Claude Desktop
Edit your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
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
    }
  }
}
```

### Step 2: Start Using Serena in Claude
Once configured, you can use Serena's semantic tools in Claude:

```
# First, activate the COGPLAN project
"Activate the project /home/ramz/Documents/adev/COGPLAN"

# Then use semantic tools
"Find all classes that inherit from BaseAgent"
"Show me the implementation of the Aether Protocol"
"Find all references to consciousness_level"
"Refactor the PlannerAgent to use async/await"
```

## Available Tools

### Semantic Search Tools
- `semantic_find_symbols` - Find classes, functions, variables by name
- `semantic_find_references` - Find all references to a symbol
- `semantic_find_implementations` - Find implementations of interfaces/base classes
- `semantic_find_definitions` - Find where symbols are defined

### Code Analysis Tools
- `analyze_dependencies` - Analyze import dependencies
- `find_unused_code` - Identify dead code
- `complexity_analysis` - Measure code complexity
- `type_analysis` - Analyze type usage and violations

### Code Editing Tools
- `semantic_edit` - Edit code with semantic understanding
- `refactor_rename` - Rename symbols across codebase
- `extract_method` - Extract code into methods
- `inline_variable` - Inline variable definitions

## Use Cases for COGPLAN

### 1. Understanding the Aether Protocol
```
"Use semantic search to find all components of the Aether Protocol and show their relationships"
```

### 2. Refactoring Agents
```
"Find all agent classes and analyze their common patterns for potential base class extraction"
```

### 3. Test Coverage Analysis
```
"Find all test files and identify which components lack tests"
```

### 4. Evolution Engine Analysis
```
"Trace the execution flow of an Evolution cycle from start to finish"
```

### 5. Consciousness Tracking
```
"Find all code paths that update consciousness_level and analyze the calculation logic"
```

## Troubleshooting

### Issue: Server not starting
```bash
# Check if uv is installed
which uv

# Update Serena
cd /home/ramz/Documents/adev/serena
git pull
uv sync
```

### Issue: Language server not working
```bash
# Install Python language server
pip install python-lsp-server[all]

# For TypeScript
npm install -g typescript-language-server
```

### Issue: Project not activated
Always start your session with:
```
"Activate the project /home/ramz/Documents/adev/COGPLAN"
```

## Advanced Features

### Custom Contexts
Create custom contexts for specific workflows:

```yaml
# .serena/contexts/testing.yml
context_name: testing
system_prompt: "Focus on test creation and coverage analysis"
tools:
  - test_generator
  - coverage_analyzer
  - test_runner
```

### Integration with Tool Hunter
Serena can be discovered and integrated by COGPLAN's Tool Hunter Agent:

```python
# The Tool Hunter can discover Serena as an MCP tool
"Run Tool Hunter to discover and integrate Serena's capabilities"
```

## Best Practices

1. **Always activate project first** - This loads the project context
2. **Use semantic search** - More powerful than text search
3. **Leverage LSP features** - Go to definition, find references, etc.
4. **Configure exclude paths** - Avoid indexing unnecessary files
5. **Update regularly** - Serena is actively developed

## Next Steps

1. Install Serena using Method 1 above
2. Configure for COGPLAN project
3. Test basic semantic search
4. Integrate with Claude Desktop
5. Use for Phase 4.8 Critical System Fixes

## Resources

- [Serena GitHub](https://github.com/oraios/serena)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Servers Collection](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

---
Generated: 2025-08-07
For: COGPLAN Phase 4.8 - Critical System Fixes