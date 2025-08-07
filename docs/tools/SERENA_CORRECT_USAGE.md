# Serena MCP Server - Setup for Claude Desktop

## Installation Status ✅

Serena is correctly configured as an MCP server for Claude Desktop.

## Configuration Files

### 1. Claude Desktop Configuration
**File**: `~/.config/claude/claude_desktop_config.json`
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
      ]
    }
  }
}
```

### 2. Serena Global Configuration
**File**: `~/.serena/serena_config.yml`
- Contains project list: `/home/ramz/Documents/adev/COGPLAN`
- Tool usage stats enabled
- Web dashboard enabled (when Serena runs)

### 3. COGPLAN Project Configuration
**File**: `/home/ramz/Documents/adev/COGPLAN/.serena/project.yml`
- Language: Python
- Project name: COGPLAN

## How to Use

### In Claude Desktop:
1. **Restart Claude Desktop** to load the MCP configuration
2. **Start a new conversation**
3. Claude automatically has access to Serena's tools (prefixed with `mcp__serena__`)
4. **Activate the project**: 
   - Say: "Activate the COGPLAN project"
   - Or: "Use the activate_project tool for /home/ramz/Documents/adev/COGPLAN"
5. **Use semantic tools**:
   - "Find all classes that inherit from BaseAgent"
   - "Show me the structure of the PlannerAgent class"
   - "Find all references to the Aether Protocol"
   - "Search for TODO comments in the codebase"

### Available Serena Tools in Claude Desktop:
- `mcp__serena__find_symbol`
- `mcp__serena__get_symbols_overview`
- `mcp__serena__find_referencing_symbols`
- `mcp__serena__search_for_pattern`
- `mcp__serena__replace_symbol_body`
- `mcp__serena__insert_after_symbol`
- `mcp__serena__insert_before_symbol`
- `mcp__serena__replace_regex`
- `mcp__serena__list_dir`
- `mcp__serena__find_file`
- `mcp__serena__write_memory`
- `mcp__serena__read_memory`
- And more...

## Important Notes

- **Serena runs AUTOMATICALLY inside Claude Desktop** via MCP protocol
- **No manual startup required** - Claude Desktop handles it
- **No separate web server needed** - MCP handles communication
- **Tools are namespaced** as `mcp__serena__<tool_name>`

## Verification

To verify Serena is working in Claude Desktop:
1. Open Claude Desktop
2. Ask: "What MCP tools do you have available?"
3. You should see Serena tools listed

## Troubleshooting

If Serena doesn't work:
1. Ensure `uv` is installed and in PATH
2. Restart Claude Desktop
3. Check the config file is valid JSON
4. Test Serena installation: `uv run --from git+https://github.com/oraios/serena serena --help`

## Source Documentation

Based on official Serena documentation from: https://github.com/oraios/serena