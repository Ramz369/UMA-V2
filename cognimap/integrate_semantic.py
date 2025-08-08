#!/usr/bin/env python3
"""
Integration script to connect the semantic analysis engine with the visualization.
This runs the semantic analyzer and enhances the graph data with AI insights.
"""

import json
import sys
from pathlib import Path

# Add cognimap to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cognimap.semantic_engine.semantic_analyzer import SemanticAnalyzer


def enhance_graph_with_semantics():
    """Run semantic analysis and enhance the visualization data."""
    
    print("🔍 Starting semantic analysis...")
    
    # Initialize analyzer
    analyzer = SemanticAnalyzer(
        root_path=Path(__file__).parent.parent,
        memory_path="reports/cognimap/semantic"
    )
    
    # Run analysis steps
    print("  1. Scanning symbols...")
    analyzer.scan_symbols()
    print(f"     Found {len(analyzer.symbols)} symbols")
    
    print("  2. Mapping references...")
    analyzer.map_references()
    print(f"     Mapped {len(analyzer.connections)} connections")
    
    print("  3. Building semantic fingerprints...")
    analyzer.build_fingerprints()
    
    print("  4. Analyzing gaps...")
    gaps = analyzer.analyze_gaps()
    print(f"     Found {len(gaps)} potential gaps")
    
    print("  5. Saving reports...")
    analyzer.save_reports(gaps)
    
    # Load existing graph data
    graph_file = Path(__file__).parent / "visualizer/output/architecture_graph.json"
    if not graph_file.exists():
        print(f"❌ Graph file not found: {graph_file}")
        return
    
    with open(graph_file, "r") as f:
        graph_data = json.load(f)
    
    print("\n📊 Enhancing graph with semantic data...")
    
    # Create a mapping of file paths to semantic data
    file_to_semantics = {}
    for symbol_id, symbol_data in analyzer.symbols.items():
        file_path = symbol_data["file"]
        if file_path not in file_to_semantics:
            file_to_semantics[file_path] = {
                "symbols": [],
                "patterns": [],
                "semantic_tags": [],
                "connections": analyzer.connections.get(file_path, {})
            }
        file_to_semantics[file_path]["symbols"].append(symbol_data["name"])
        
        # Add fingerprint data
        if symbol_id in analyzer.fingerprints:
            fp = analyzer.fingerprints[symbol_id]
            file_to_semantics[file_path]["semantic_tags"].extend(fp.get("tags", []))
            if fp.get("pattern"):
                file_to_semantics[file_path]["patterns"].append(fp["pattern"])
    
    # Enhance nodes with semantic data
    enhanced_nodes = 0
    for node in graph_data["nodes"]:
        filepath = node.get("filepath", "")
        
        # Try to match with semantic data
        for sem_path in file_to_semantics:
            if filepath.endswith(sem_path) or sem_path.endswith(filepath):
                # Add semantic enhancements
                node["semantic_fingerprint"] = {
                    "symbols": file_to_semantics[sem_path]["symbols"][:5],  # Top 5 symbols
                    "tags": list(set(file_to_semantics[sem_path]["semantic_tags"]))[:10],
                    "patterns": list(set(file_to_semantics[sem_path]["patterns"]))[:3]
                }
                node["semantic_tags"] = list(set(file_to_semantics[sem_path]["semantic_tags"]))[:10]
                node["patterns"] = list(set(file_to_semantics[sem_path]["patterns"]))[:3]
                enhanced_nodes += 1
                break
    
    print(f"  Enhanced {enhanced_nodes}/{len(graph_data['nodes'])} nodes with semantic data")
    
    # Add suggested connections (gaps) as special edges
    suggested_edges = []
    for gap in gaps[:20]:  # Limit to top 20 suggestions
        # Find nodes matching the gap files
        source_node = None
        target_node = None
        
        for node in graph_data["nodes"]:
            filepath = node.get("filepath", "")
            if filepath.endswith(gap["from"]) or gap["from"].endswith(filepath):
                source_node = node["id"]
            if filepath.endswith(gap["to"]) or gap["to"].endswith(filepath):
                target_node = node["id"]
        
        if source_node and target_node and source_node != target_node:
            suggested_edges.append({
                "source": source_node,
                "target": target_node,
                "type": "suggested",
                "confidence": 0.7,
                "metadata": {
                    "reason": f"Semantic similarity: {gap['tag']}",
                    "is_suggestion": True
                }
            })
    
    print(f"  Added {len(suggested_edges)} suggested connections")
    
    # Add suggested edges to the graph
    graph_data["edges"].extend(suggested_edges)
    
    # Save enhanced graph
    enhanced_file = Path(__file__).parent / "visualizer/output/architecture_graph_enhanced.json"
    with open(enhanced_file, "w") as f:
        json.dump(graph_data, f, indent=2)
    
    print(f"\n✅ Enhanced graph saved to: {enhanced_file}")
    print("\n📈 Summary:")
    print(f"  - Total nodes: {len(graph_data['nodes'])}")
    print(f"  - Total edges: {len(graph_data['edges'])}")
    print(f"  - Semantic enhancements: {enhanced_nodes}")
    print(f"  - Suggested connections: {len(suggested_edges)}")
    
    # Generate improvement roadmap
    print("\n📝 Generating improvement roadmap...")
    roadmap = []
    roadmap.append("# CogniMap Improvement Roadmap\n")
    roadmap.append(f"## Analysis Date: {Path('reports/cognimap/semantic/symbol_graph.json').stat().st_mtime if Path('reports/cognimap/semantic/symbol_graph.json').exists() else 'Now'}\n\n")
    roadmap.append("## Semantic Analysis Results\n\n")
    roadmap.append(f"- **Symbols discovered**: {len(analyzer.symbols)}\n")
    roadmap.append(f"- **Connections mapped**: {len(analyzer.connections)}\n")
    roadmap.append(f"- **Gaps identified**: {len(gaps)}\n\n")
    
    roadmap.append("## Top Architectural Gaps\n\n")
    for i, gap in enumerate(gaps[:10], 1):
        roadmap.append(f"{i}. **{gap['tag']}** connection missing between:\n")
        roadmap.append(f"   - {gap['from']}\n")
        roadmap.append(f"   - {gap['to']}\n\n")
    
    roadmap.append("## Recommendations\n\n")
    roadmap.append("1. Review suggested connections in the enhanced visualization\n")
    roadmap.append("2. Consider creating interfaces for semantically similar components\n")
    roadmap.append("3. Implement missing connections identified by gap analysis\n")
    roadmap.append("4. Run DeepSeek analysis for detailed architectural recommendations\n")
    
    roadmap_file = Path("reports/cognimap/semantic/improvement_roadmap.md")
    roadmap_file.parent.mkdir(parents=True, exist_ok=True)
    with open(roadmap_file, "w") as f:
        f.writelines(roadmap)
    
    print(f"  Roadmap saved to: {roadmap_file}")
    print("\n🎉 Integration complete! You can now:")
    print("  1. Open visualizer with enhanced data")
    print("  2. View suggested connections (dotted lines)")
    print("  3. Check semantic tags in node details")
    print("  4. Review improvement roadmap")


if __name__ == "__main__":
    enhance_graph_with_semantics()