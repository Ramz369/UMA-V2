# CogniMap Architecture Documentation

## Overview

CogniMap is a self-contained architecture visualization and understanding system that creates a living map of any codebase. It works by injecting semantic fingerprints into files and building a comprehensive graph of relationships.

## System Architecture

```
cognimap/
├── core/               # Core engine (fingerprints, scanning, analysis)
├── collectors/         # Data collection modules
│   └── serena_collector.py  # Integration with Serena MCP
├── graph/             # Graph database and operations
├── analysis/          # Analysis engines
├── visualizer/        # Visualization system
├── protocols/         # Protocol definitions
├── hooks/            # Git and IDE hooks
├── docs/             # CogniMap documentation (NOT mixed with project docs)
├── config/           # CogniMap configuration files
└── setup.py          # Installation and setup

```

## Integration Points

### 1. Serena MCP Integration
- CogniMap uses Serena MCP as its primary data collection engine
- Serena handles: file discovery, AST parsing, symbol analysis
- CogniMap adds: fingerprinting, semantic analysis, visualization

### 2. Claude CLI Integration
- CogniMap registers as an MCP tool
- Bulk processing through single tool calls
- Semantic enrichment through Claude's understanding

## Data Flow

1. **Discovery Phase**
   - Serena MCP discovers all files
   - Filters for code files
   - Extracts symbols and relationships

2. **Analysis Phase**
   - CogniMap generates fingerprints
   - Performs programmatic analysis
   - Queues for semantic enrichment

3. **Enrichment Phase**
   - Claude receives bulk data
   - Adds semantic understanding
   - Returns enriched analysis

4. **Storage Phase**
   - Fingerprints injected into files
   - Graph stored in database
   - Relationships cached

5. **Visualization Phase**
   - Graph data served via API
   - Real-time updates via WebSocket
   - 3D rendering in browser

## Key Components

### Core Engine (`core/`)
- **Fingerprint System**: Unique identification for every file
- **Scanner**: Multi-language code analysis
- **Analyzer**: Semantic understanding
- **Protocol**: Communication standards

### Collectors (`collectors/`)
- **Serena Collector**: Primary data collection via Serena MCP
- **Git Collector**: Version history tracking
- **Runtime Collector**: Live event monitoring

### Graph System (`graph/`)
- **Storage**: Persistent graph database
- **Queries**: Complex relationship queries
- **Cache**: Performance optimization

### Analysis (`analysis/`)
- **Pattern Detector**: Design pattern recognition
- **Flow Tracer**: Data and control flow analysis
- **Health Checker**: Architecture quality metrics

## Configuration

CogniMap configuration is stored in `cognimap/config/` and includes:
- `default.yaml`: Default settings
- `project.yaml`: Project-specific overrides
- `serena.yaml`: Serena MCP integration settings

## Separation of Concerns

### What CogniMap Owns:
- Fingerprint generation and injection
- Semantic analysis and enrichment
- Graph building and visualization
- Architecture health metrics

### What Serena MCP Provides:
- File discovery and caching
- AST parsing and symbol extraction
- Language server capabilities
- File modification operations

### What Claude Provides:
- Semantic understanding
- Pattern recognition
- Quality assessment
- Improvement suggestions

## Update Mechanism

CogniMap supports three update modes:

1. **Full Scan**: Complete analysis of entire codebase
2. **Incremental Update**: Only changed files since last scan
3. **Real-time Monitoring**: Continuous updates as files change

## Security & Privacy

- Fingerprints contain no sensitive data
- All analysis is local (no external API calls when in Claude)
- Graph data is stored locally
- No code is transmitted externally

## Performance Considerations

- Serena's caching minimizes file I/O
- Bulk processing reduces Claude API calls
- Incremental updates for efficiency
- Graph queries optimized with indexes