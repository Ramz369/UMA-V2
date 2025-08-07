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

## Installation

```bash
# Install CogniMap in your project
cd your-project
python -m pip install cognimap

# Initialize CogniMap
cognimap init

# Start the visualization server
cognimap serve
```

## Quick Start

### 1. Initialize CogniMap in Your Project

```bash
cognimap init
```

This will:
- Scan all existing files
- Inject semantic fingerprints
- Build the initial architecture graph
- Set up git hooks for continuous tracking

### 2. View Your Architecture

```bash
cognimap serve
```

Open http://localhost:8080 to see your architecture in 3D.

### 3. Query Your Architecture

```python
from cognimap import CogniMap

cm = CogniMap()

# Find all components related to authentication
auth_components = cm.query("semantic_tags CONTAINS 'authentication'")

# Find circular dependencies
circular_deps = cm.find_circular_dependencies()

# Get component relationships
relationships = cm.get_relationships("src/auth/login.py")
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
- **3D Rendering**: Three.js-based visualization
- **Real-time Updates**: WebSocket streaming
- **Interactive Controls**: Zoom, pan, filter, search
- **Time Travel**: Historical architecture replay

## Configuration

Create `.cognimap.yaml` in your project root:

```yaml
project:
  name: MyProject
  type: web-application

visualization:
  default_view: hierarchical
  theme: dark
  
analysis:
  llm_provider: openai  # or anthropic, local
  semantic_depth: deep   # or shallow, medium
  
monitoring:
  real_time: true
  event_tracking: true
  
warnings:
  circular_dependencies: error
  orphaned_code: warning
  high_complexity: info
```

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