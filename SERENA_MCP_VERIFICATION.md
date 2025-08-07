# Serena MCP Server - Verification Guide for New Terminal Session

## 🔍 Quick Verification Steps

### 1. Check Serena Installation
```bash
# Verify Serena is installed
ls -la ~/tools/serena/ | head -5

# Expected: Should show Serena repository files
# If missing: Clone from https://github.com/oraios/serena
```

### 2. Check UV Package Manager
```bash
# Verify uv is installed
which uv

# Expected: /home/ramz/.cargo/bin/uv or similar
# If missing: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Test Serena Command
```bash
# Test if Serena runs
uv run --from git+https://github.com/oraios/serena serena --help

# Expected: Shows Serena help text
# If fails: Check uv installation and internet connection
```

## 📋 Configuration Files to Verify

### 1. Claude Desktop Configuration
**File**: `~/.config/claude/claude_desktop_config.json`

```bash
# Check if config exists and is correct
cat ~/.config/claude/claude_desktop_config.json
```

**Should contain**:
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

```bash
# Check Serena config
cat ~/.serena/serena_config.yml
```

**Should contain** (at minimum):
```yaml
gui_log_window: false
web_dashboard: true
web_dashboard_open_on_launch: false
log_level: 20
trace_lsp_communication: false
tool_timeout: 240
excluded_tools: []
included_optional_tools: []
jetbrains: false
record_tool_usage_stats: true
token_count_estimator: TIKTOKEN_GPT4O

projects:
  - /home/ramz/Documents/adev/COGPLAN
```

### 3. COGPLAN Project Configuration
**File**: `/home/ramz/Documents/adev/COGPLAN/.serena/project.yml`

```bash
# From COGPLAN directory
cat .serena/project.yml
```

**Should contain**:
```yaml
project_name: COGPLAN
project_type: python
language: python
language_servers:
  - python
  - yaml
  - json
  - toml
```

## 🚀 How to Use Serena with Claude Desktop

### Step 1: Restart Claude Desktop
```bash
# Close Claude Desktop completely
# Reopen Claude Desktop
# The MCP server configuration will load automatically
```

### Step 2: In Claude Desktop Conversation
Start a new conversation and say:
```
"What MCP tools do you have available?"
```

**Expected Response**: Claude should list tools prefixed with `mcp__serena__` such as:
- mcp__serena__find_symbol
- mcp__serena__get_symbols_overview
- mcp__serena__search_for_pattern
- etc.

### Step 3: Activate COGPLAN Project
In Claude Desktop, say:
```
"Activate the COGPLAN project at /home/ramz/Documents/adev/COGPLAN"
```

Or:
```
"Use the mcp__serena__activate_project tool to load /home/ramz/Documents/adev/COGPLAN"
```

### Step 4: Use Semantic Tools
Once activated, you can use semantic queries:
- "Find all classes that inherit from BaseAgent"
- "Show me the structure of the PlannerAgent class"
- "Search for TODO comments in the codebase"
- "Find all references to the Aether Protocol"

## ❌ What NOT to Do

1. **DON'T** try to start Serena manually in terminal
2. **DON'T** run Serena as a background service
3. **DON'T** use nohup, screen, or tmux with Serena
4. **DON'T** access Serena via web browser

## ✅ What TO Do

1. **DO** use Serena through Claude Desktop only
2. **DO** let Claude Desktop manage the MCP server
3. **DO** use the mcp__serena__ prefixed tools
4. **DO** restart Claude Desktop if tools aren't showing

## 🔧 Troubleshooting

### If Serena tools don't appear in Claude Desktop:

1. **Check JSON syntax**:
```bash
python3 -m json.tool ~/.config/claude/claude_desktop_config.json
```

2. **Verify uv works**:
```bash
uv --version
```

3. **Test Serena directly**:
```bash
cd ~/tools/serena
uv run serena --help
```

4. **Check PATH**:
```bash
echo $PATH | grep -o ".cargo/bin"
# Should show: .cargo/bin
```

5. **Reinstall if needed**:
```bash
# Only if Serena is missing
cd ~/tools
git clone https://github.com/oraios/serena
```

## 📝 Important Notes

- **Serena is NOT part of COGPLAN** - it's a system-wide tool
- **Serena runs INSIDE Claude Desktop** - not as a separate service
- **MCP protocol** handles all communication automatically
- **No manual startup required** - Claude Desktop manages everything

## 🎯 Success Indicators

✅ Claude Desktop shows mcp__serena__ tools
✅ Project activation works
✅ Semantic searches return results
✅ No manual Serena processes running in terminal

## 📚 Documentation

- **COGPLAN Serena Guide**: `docs/tools/SERENA_CORRECT_USAGE.md`
- **Official Serena Docs**: https://github.com/oraios/serena
- **MCP Protocol**: Model Context Protocol for AI tools

---

**Remember**: Serena enhances Claude Desktop's capabilities. It's not a standalone service you run in terminal!