#!/usr/bin/env python3
"""
CogniMap Explorer - Visual Architecture Analysis Tool
"""

import sys
from pathlib import Path
# Add parent directories to path to import cognimap modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from cognimap.graph.graph_builder import GraphBuilder
from cognimap.graph.graph_visualizer import GraphVisualizer
from cognimap.graph.graph_analyzer import GraphAnalyzer
import json

def explore_architecture():
    """Main exploration function"""
    print("🧠 COGNIMAP ARCHITECTURE EXPLORER")
    print("=" * 80)
    
    # Build full graph
    print("\n1️⃣ FULL PROJECT ANALYSIS")
    print("-" * 40)
    full_builder = GraphBuilder(scope='full')
    full_graph = full_builder.build()
    print(f"✅ Full project: {len(full_graph['nodes'])} components, {len(full_graph['edges'])} relationships")
    
    # Build cognimap subsystem only
    print("\n2️⃣ COGNIMAP SUBSYSTEM ANALYSIS")
    print("-" * 40)
    cogni_builder = GraphBuilder(scope='cognimap')
    cogni_graph = cogni_builder.build()
    print(f"✅ CogniMap only: {len(cogni_graph['nodes'])} components, {len(cogni_graph['edges'])} relationships")
    
    # Create visualizations
    visualizer = GraphVisualizer(full_graph)
    
    # Generate text view
    print("\n3️⃣ TOP CONNECTED COMPONENTS")
    print("-" * 40)
    text_viz = visualizer.create_text_visualization()
    for line in text_viz.split('\n')[:20]:
        if line.strip():
            print(line)
    
    # Generate and save Mermaid diagram
    print("\n4️⃣ GENERATING VISUAL DIAGRAMS")
    print("-" * 40)
    
    # Output directory
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    mermaid = visualizer.create_mermaid_diagram()
    mermaid_path = output_dir / 'architecture.mmd'
    with open(mermaid_path, 'w') as f:
        f.write(mermaid)
    print(f"✅ Mermaid diagram saved to: {mermaid_path}")
    
    # Save full graph as JSON for external tools
    json_path = output_dir / 'architecture_graph.json'
    with open(json_path, 'w') as f:
        json.dump(full_graph, f, indent=2, default=str)
    print(f"✅ Full graph saved to: {json_path}")
    
    # Run semantic enhancement
    print("\n🔬 RUNNING SEMANTIC ENHANCEMENT")
    print("-" * 40)
    try:
        # Import and run the semantic integration
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from integrate_semantic import enhance_graph_with_semantics
        enhance_graph_with_semantics()
        print("✅ Semantic enhancement complete!")
    except Exception as e:
        print(f"⚠️ Semantic enhancement failed: {e}")
        print("  Continuing with basic graph...")
    
    # Component type analysis
    print("\n5️⃣ COMPONENT TYPES")
    print("-" * 40)
    types = {}
    for node in full_graph['nodes']:
        t = node.get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
    
    for comp_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {comp_type}: {count}")
    
    # Semantic tag analysis
    print("\n6️⃣ SEMANTIC TAGS (Top 10)")
    print("-" * 40)
    tags = {}
    for node in full_graph['nodes']:
        for tag in node.get('semantic_tags', []):
            tags[tag] = tags.get(tag, 0) + 1
    
    for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {tag}: {count} components")
    
    print("\n" + "=" * 80)
    print("✨ VISUALIZATION FILES CREATED:")
    print(f"  1. {mermaid_path.relative_to(Path.cwd())}")
    print(f"  2. {json_path.relative_to(Path.cwd())}")
    print(f"  3. Dashboard: cognimap/visualizer/frontend/dashboard.html")
    print("\n📊 TO VIEW INTERACTIVELY:")
    print("  1. Copy mermaid diagram contents")
    print("  2. Visit: https://mermaid.live/")
    print("  3. Paste and explore!")
    print("\n🌐 OR OPEN DASHBOARD:")
    print("  firefox cognimap/visualizer/frontend/dashboard.html")
    print("=" * 80)

if __name__ == "__main__":
    explore_architecture()