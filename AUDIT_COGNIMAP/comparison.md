# Comparison with Existing Graph Tools

- Existing GraphBuilder detected 97 nodes and 388 edges (`AUDIT_COGNIMAP/existing_graph.json`).
- Custom networkx scan found 67 nodes and 117 import edges (`AUDIT_COGNIMAP/semantic_map.json`).
- Discrepancies stem from:
  - GraphBuilder uses fingerprints for components; our scan only counts files.
  - GraphBuilder tracks calls and data-flow; our scan only inspects imports.
  - GraphAnalyzer reports 388 relationships; our graph missed call/data edges.
