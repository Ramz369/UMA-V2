# 🧠 CogniMap - Living Architecture Visualization System

## Overview

CogniMap is a revolutionary architecture visualization and understanding system that makes codebases self-aware. It automatically discovers, tracks, and visualizes the relationships between all components in your project, creating a living, breathing map of your software architecture.

## Key Features

### 🔍 Automatic Discovery
- **Zero-configuration setup** - Works with any codebase
- **Multi-language support** - Python, JavaScript, TypeScript, Go, Rust, Java
- **Intelligent relationship detection** - Understands imports, calls, data flows
- **Semantic understanding** - Uses AI to comprehend component purposes

### 📍 Fingerprint System
- Every file gets a unique semantic fingerprint
- Tracks intent, purpose, and relationships
- Version history and evolution tracking
- Automatic metadata injection

### 🎨 3D Interactive Visualization
- Real-time architecture rendering
- Multiple visualization layers (structure, data flow, dependencies)
- Time-travel through git history
- Interactive debugging and exploration

### ⚠️ Intelligent Warnings
- Architectural violations
- Circular dependencies
- Orphaned code
- Performance bottlenecks
- Security vulnerabilities

## Installation & Setup

```bash
# Clone or navigate to your project with CogniMap
cd your-project/cognimap

# Install JavaScript dependencies for visualization
npm install

# Build the visualization bundle
npm run build

# Generate the architecture graph
python3 cli.py visualize
```

## Quick Start

### 1. Generate Architecture Graph

```bash
# Use the interactive launcher
./visualize.sh

# Or run directly
python3 cli.py visualize
```

This will:
- Scan all project files
- Extract semantic fingerprints
- Build the architecture graph
- Generate visualization data

### 2. View Your Architecture

```bash
# Option 1: Open the InfraNodus-style interactive visualization
open visualizer/interactive.html

# Option 2: Use the launcher menu
./visualize.sh
# Then select option 2 (Open Dashboard)

# Option 3: Serve via HTTP
python3 -m http.server 8080
# Then navigate to http://localhost:8080/visualizer/interactive.html
```

### 3. Explore Your Architecture

**Interactive Visualization Features:**
- **ForceAtlas2 Layout**: InfraNodus-style network visualization
- **Real-time Search**: Filter nodes by name or type
- **Component Details**: Click nodes to see relationships
- **Multiple Layouts**: Switch between ForceAtlas2, hierarchical, circular
- **Statistics**: View node/edge counts and component types

**Command Line Analysis:**
```bash
# Analyze architecture for issues
python3 cli.py analyze

# Export to different formats
python3 cli.py export --format mermaid
python3 cli.py export --format json
```

## Architecture

CogniMap consists of several key components:

### Core Engine (`core/`)
- **Fingerprint System**: Unique identification for every file
- **Scanner**: Multi-language code analysis
- **Analyzer**: Semantic understanding using AI
- **Protocol**: CogniMap communication standards

### Data Collection (`collectors/`)
- **Static Analysis**: AST-based code understanding
- **Runtime Monitoring**: Live event tracking
- **Git Tracking**: Historical evolution
- **Semantic Indexing**: Meaning-based relationships

### Graph Database (`graph/`)
- **Storage**: High-performance graph persistence
- **Queries**: Complex relationship queries
- **Models**: Architecture data models
- **Relationships**: Connection discovery

### Analysis Engine (`analysis/`)
- **LLM Integration**: AI-powered understanding
- **Pattern Detection**: Design pattern recognition
- **Flow Tracing**: Data and control flow analysis
- **Health Checking**: Architecture quality metrics

### Visualization (`visualizer/`)
- **Interactive Network Graph**: Sigma.js-based visualization
- **InfraNodus-style Layout**: ForceAtlas2 algorithm for natural clustering
- **Multiple Views**: 
  - `interactive.html` - Main network visualization
  - `dashboard.html` - Simple metrics view
  - `visualizer.html` - Alternative visualization
- **Interactive Controls**: Zoom, pan, filter, search, layout switching

## Current Capabilities

### ✅ Working Features
- **Fingerprint System**: Automatic semantic tagging of all files
- **Graph Generation**: Extracts and maps 388+ component relationships
- **Interactive Visualization**: InfraNodus-style network graph
- **Multiple Formats**: Export to JSON, Mermaid, tree view
- **Architecture Analysis**: Detect circular dependencies, orphaned code
- **CLI Interface**: Command-line tools for analysis and export

### 🚧 In Development
- Package distribution (pip install)
- Real-time monitoring
- IDE integrations
- WebSocket updates

## Use Cases

### For Developers
- Understand complex codebases quickly
- Find dependencies and impacts
- Debug architectural issues
- Track technical debt

### For Architects
- Verify intended vs actual architecture
- Identify architectural violations
- Plan refactoring strategies
- Document system design

### For Teams
- Onboard new developers
- Code review with context
- Collaborative architecture discussions
- Track architecture evolution

### For Management
- Visualize technical debt
- Understand system complexity
- Track development progress
- Make informed decisions

## Integration

CogniMap integrates with:
- **Git**: Automatic tracking on commits
- **CI/CD**: Architecture validation in pipelines
- **IDEs**: VS Code, IntelliJ extensions
- **Documentation**: Auto-generated architecture docs

## Advanced Features

### Semantic Layers
Switch between different views of your architecture:
- **Code Structure**: Files and functions
- **Data Flow**: How data moves through the system
- **Control Flow**: Execution paths
- **Intent Layer**: What each component is trying to achieve
- **Dependency Layer**: What depends on what

### Time Travel
Slide through your project's history and watch the architecture evolve:
- See when components were added
- Track relationship changes
- Identify breaking points
- Understand evolution patterns

### AI-Powered Insights
CogniMap uses LLMs to provide intelligent insights:
- Component purpose explanation
- Improvement suggestions
- Anti-pattern detection
- Refactoring recommendations

## DeepSeek Scenario Reports

CogniMap can leverage the [DeepSeek](https://deepseek.com) API to identify core
architectural elements and highlight gaps in the current implementation. Run:

```bash
export DEEPSEEK_API_KEY=your_key
python scripts/deepseek_scenario_report.py
```

The generated proposal will be written to
`reports/cognimap/deepseek_scenario_report.md` so downstream agents can reason
over the architecture and fill in missing links.

## Semantic Analysis Engine

To build a symbol-based understanding of the codebase and surface potential
architecture gaps run the semantic analyzer:

```bash
python -m cognimap.semantic_engine.semantic_analyzer
```

This produces machine-readable reports under `reports/cognimap/semantic/`
including:

- `symbol_graph.json` – all discovered symbols and references
- `semantic_gaps.json` – components that share semantics but are not
  connected
- `pattern_analysis.json` – detected design pattern markers
- `improvement_roadmap.md` – placeholder for AI generated suggestions

These outputs also seed persistent memory files used by future agents to
incrementally grow CogniMap's semantic understanding.

## Contributing

CogniMap is open source and welcomes contributions!

```bash
# Clone the repository
git clone https://github.com/cognimap/cognimap

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

MIT License - See LICENSE file for details.

## Support

- Documentation: https://cognimap.dev/docs
- Issues: https://github.com/cognimap/cognimap/issues
- Discord: https://discord.gg/cognimap

---

**CogniMap** - Making Software Architecture Visible, Understandable, and Alive.