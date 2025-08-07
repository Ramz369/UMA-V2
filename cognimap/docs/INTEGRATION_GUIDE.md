# CogniMap Integration Guide

## Prerequisites

1. **Serena MCP** must be installed and configured
2. **Claude CLI** or compatible LLM interface
3. **Python 3.8+** with required dependencies

## Installation

### Step 1: Install CogniMap

```bash
cd cognimap
pip install -e .
```

### Step 2: Configure Serena MCP Integration

Create `cognimap/config/serena.yaml`:

```yaml
serena:
  enabled: true
  server_url: "http://localhost:3000"
  project_path: "."
  
collectors:
  use_serena: true
  use_git: true
  use_runtime: false
  
analysis:
  use_language_server: true
  cache_symbols: true
  
bulk_processing:
  batch_size: 100
  include_snippets: true
  snippet_size: 500
```

### Step 3: Register with MCP

The CogniMap tools are automatically registered when Serena MCP starts with CogniMap support.

## Usage

### Initial Analysis

```bash
# In Claude CLI or terminal
cognimap init

# Or through MCP tool
mcp_tool cognimap_analyze --path . --mode full
```

### Update Analysis

```bash
# Update changed files only
cognimap update

# Or through MCP
mcp_tool cognimap_update --since last_commit
```

### Query Architecture

```python
from cognimap import CogniMap

cm = CogniMap()

# Find all authentication components
auth_components = cm.query("semantic_tags CONTAINS 'authentication'")

# Find circular dependencies
circular = cm.find_circular_dependencies()

# Get component relationships
rels = cm.get_relationships("src/auth/login.py")
```

## Serena MCP Tools

When integrated with Serena MCP, these tools become available:

### cognimap_analyze
Performs bulk analysis of entire project.

**Parameters:**
- `path`: Project root path
- `mode`: Analysis mode (full, incremental, update)
- `include_tests`: Include test files (default: false)

**Returns:**
- Bulk analysis data for semantic enrichment

### cognimap_update
Updates fingerprints for changed files.

**Parameters:**
- `since`: Update files changed since (commit hash or timestamp)
- `force`: Force update even if unchanged

**Returns:**
- List of updated files with changes

### cognimap_inject
Injects fingerprints into files.

**Parameters:**
- `files`: List of files with fingerprint data
- `force`: Overwrite existing fingerprints

**Returns:**
- Injection results

### cognimap_graph
Builds and returns architecture graph.

**Parameters:**
- `format`: Output format (json, graphml, dot)
- `include_relationships`: Types of relationships to include

**Returns:**
- Complete architecture graph

## Workflow Examples

### 1. New Project Setup

```python
# 1. Initialize CogniMap
cognimap init

# 2. Perform full analysis
result = mcp_tool("cognimap_analyze", {
    "path": ".",
    "mode": "full"
})

# 3. Claude enriches semantically
enriched = claude_analyze(result.data)

# 4. Inject fingerprints
mcp_tool("cognimap_inject", {
    "files": enriched
})

# 5. Build graph
graph = mcp_tool("cognimap_graph", {
    "format": "json"
})
```

### 2. Continuous Updates

```python
# Set up file watcher
cognimap watch

# On file change:
# 1. Detect change
# 2. Update fingerprint
# 3. Rebuild affected relationships
# 4. Update visualization
```

### 3. Architecture Analysis

```python
# Get architecture health
health = cognimap.analyze_health()

# Find issues
issues = cognimap.find_issues()
print(f"Circular dependencies: {issues['circular']}")
print(f"Orphaned files: {issues['orphaned']}")
print(f"High complexity: {issues['complex']}")

# Get recommendations
recommendations = cognimap.get_recommendations()
```

## Configuration Options

### Project Configuration

Create `.cognimap.yaml` in project root:

```yaml
project:
  name: "My Project"
  type: "web-application"
  
exclude:
  - "node_modules"
  - ".venv"
  - "build"
  - "dist"
  
fingerprint:
  auto_inject: true
  update_on_save: true
  
visualization:
  default_view: "hierarchical"
  theme: "dark"
  
analysis:
  depth: "deep"
  include_tests: false
  semantic_provider: "claude"
```

### Global Configuration

Edit `cognimap/config/default.yaml`:

```yaml
defaults:
  language_support:
    - python
    - javascript
    - typescript
    - java
    - go
    
  fingerprint:
    version: "1.0.0"
    hash_algorithm: "sha256"
    
  graph:
    storage_backend: "sqlite"
    cache_enabled: true
    
  visualization:
    port: 8080
    auto_open: true
```

## Troubleshooting

### Issue: Fingerprints not injecting
- Check file permissions
- Verify language is supported
- Check `.cognimap.yaml` exclude patterns

### Issue: Serena MCP connection failed
- Verify Serena is running
- Check `serena.yaml` configuration
- Ensure project is activated in Serena

### Issue: Graph not building
- Check for syntax errors in code
- Verify all dependencies installed
- Clear cache with `cognimap cache --clear`

### Issue: Semantic analysis not working
- Ensure Claude CLI is configured
- Check batch size in configuration
- Verify LLM context limits

## Best Practices

1. **Run full analysis initially**, then use incremental updates
2. **Configure excludes properly** to avoid analyzing vendor code
3. **Use semantic tags** for better categorization
4. **Regular updates** to keep fingerprints current
5. **Monitor graph size** - large projects may need pagination

## API Reference

See [API Documentation](./API.md) for detailed API reference.