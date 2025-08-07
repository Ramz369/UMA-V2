/**
 * CogniMap to Graphology Adapter
 * Converts CogniMap data format to Graphology graph structure
 */

import Graph from 'graphology';

export class CogniMapGraphAdapter {
  constructor() {
    this.graph = new Graph({
      multi: false,
      allowSelfLoops: false,
      type: 'directed'
    });
    this.nodeMap = new Map();
    this.edgeMap = new Map();
    this.statistics = {
      totalNodes: 0,
      totalEdges: 0,
      nodesByType: {},
      edgesByType: {}
    };
  }

  /**
   * Load graph from CogniMap JSON data
   */
  async loadFromCogniMap(data) {
    console.log('🔄 Loading CogniMap data...');
    
    // Clear existing graph
    this.graph.clear();
    this.nodeMap.clear();
    this.edgeMap.clear();
    
    // Convert nodes
    if (data.nodes && Array.isArray(data.nodes)) {
      this.convertNodes(data.nodes);
    }
    
    // Convert edges
    if (data.edges && Array.isArray(data.edges)) {
      this.convertEdges(data.edges);
    }
    
    // Calculate initial positions if not provided
    this.initializePositions();
    
    // Update statistics
    this.updateStatistics();
    
    console.log(`✅ Loaded ${this.statistics.totalNodes} nodes, ${this.statistics.totalEdges} edges`);
    return this.graph;
  }

  /**
   * Convert CogniMap nodes to Graphology nodes
   */
  convertNodes(nodes) {
    // Create a mapping from filepath to node ID for edge resolution
    this.filepathToId = new Map();
    
    nodes.forEach(node => {
      const nodeId = node.id || node.filepath;
      
      // Store filepath to ID mapping
      if (node.filepath) {
        this.filepathToId.set(node.filepath, nodeId);
      }
      
      // Prepare node attributes
      const attributes = {
        // Core attributes
        id: nodeId,
        label: node.name || node.filepath || nodeId,
        
        // CogniMap specific
        filepath: node.filepath,
        nodeType: node.type || 'unknown',  // Changed from 'type' to 'nodeType' to avoid Sigma conflict
        fingerprint: node.fingerprint || null,
        semantic_tags: node.semantic_tags || [],
        semantic_fingerprint: node.semantic_fingerprint || {},
        patterns: node.patterns || [],
        confidence: node.confidence || 0,
        
        // Visual attributes
        size: this.calculateNodeSize(node),
        color: this.getNodeColor(node),
        x: node.x || Math.random() * 1000,
        y: node.y || Math.random() * 1000,
        
        // Metrics (to be calculated)
        metrics: {
          degree: 0,
          betweenness: 0,
          closeness: 0,
          pagerank: 0,
          community: null
        },
        
        // Metadata
        loc: node.loc || 0,
        complexity: node.complexity || 0,
        language: node.language || (node.fingerprint?.language) || 'unknown'
      };
      
      // Add node to graph
      try {
        this.graph.addNode(nodeId, attributes);
        this.nodeMap.set(nodeId, attributes);
        
        // Track node types
        this.statistics.nodesByType[attributes.nodeType] = 
          (this.statistics.nodesByType[attributes.nodeType] || 0) + 1;
      } catch (error) {
        console.warn(`Failed to add node ${nodeId}:`, error.message);
      }
    });
  }

  /**
   * Convert CogniMap edges to Graphology edges
   */
  convertEdges(edges) {
    edges.forEach(edge => {
      // Resolve source and target - they might be filepaths or IDs
      let sourceId = edge.source;
      let targetId = edge.target;
      
      // If source/target look like filepaths, try to resolve them
      if (this.filepathToId.has(sourceId)) {
        sourceId = this.filepathToId.get(sourceId);
      }
      if (this.filepathToId.has(targetId)) {
        targetId = this.filepathToId.get(targetId);
      }
      
      const edgeId = edge.id || `${sourceId}-${targetId}`;
      
      // Prepare edge attributes
      const attributes = {
        id: edgeId,
        edgeType: edge.type || 'depends_on',  // Changed from 'type' to 'edgeType'
        weight: edge.weight || 1,
        color: this.getEdgeColor(edge),
        size: edge.size || 1,
        confidence: edge.confidence || 0,
        metadata: edge.metadata || {}
      };
      
      // Add edge to graph
      try {
        // Check if nodes exist
        if (this.graph.hasNode(sourceId) && this.graph.hasNode(targetId)) {
          this.graph.addDirectedEdge(sourceId, targetId, attributes);
          this.edgeMap.set(edgeId, attributes);
          
          // Track edge types
          this.statistics.edgesByType[attributes.edgeType] = 
            (this.statistics.edgesByType[attributes.edgeType] || 0) + 1;
        } else {
          console.warn(`Skipping edge ${edgeId}: missing nodes (${sourceId} -> ${targetId})`);
        }
      } catch (error) {
        console.warn(`Failed to add edge ${edgeId}:`, error.message);
      }
    });
  }

  /**
   * Calculate node size based on importance
   */
  calculateNodeSize(node) {
    let baseSize = 5;
    
    // Factor in lines of code
    if (node.loc) {
      baseSize += Math.log10(node.loc + 1);
    }
    
    // Factor in type importance
    const typeWeights = {
      'agent': 3,
      'tool': 2.5,
      'component': 2,
      'service': 2.5,
      'model': 2,
      'test': 1,
      'unknown': 1
    };
    
    const typeWeight = typeWeights[node.type] || 1;
    baseSize *= typeWeight;
    
    // Factor in connections (will be updated after edges are added)
    // This is a placeholder - actual degree will be calculated later
    
    return Math.min(Math.max(baseSize, 3), 30); // Clamp between 3 and 30
  }

  /**
   * Get node color based on type
   */
  getNodeColor(node) {
    const colorMap = {
      'agent': '#ff6b6b',      // Red
      'tool': '#4ecdc4',       // Teal
      'component': '#45b7d1',  // Blue
      'test': '#96ceb4',       // Green
      'service': '#f9ca24',    // Yellow
      'model': '#dda0dd',      // Plum
      'protocol': '#ff9ff3',   // Pink
      'unknown': '#95a5a6'     // Gray
    };
    
    return colorMap[node.type] || colorMap['unknown'];
  }

  /**
   * Get edge color based on type
   */
  getEdgeColor(edge) {
    const colorMap = {
      'imports': '#3498db',     // Blue
      'depends_on': '#2ecc71',  // Green
      'uses': '#9b59b6',        // Purple
      'extends': '#e74c3c',     // Red
      'implements': '#f39c12',  // Orange
      'calls': '#1abc9c',       // Turquoise
      'unknown': '#95a5a6'      // Gray
    };
    
    return colorMap[edge.type] || colorMap['unknown'];
  }

  /**
   * Initialize node positions using a simple grid layout
   */
  initializePositions() {
    const nodes = this.graph.nodes();
    const nodeCount = nodes.length;
    const gridSize = Math.ceil(Math.sqrt(nodeCount));
    
    nodes.forEach((nodeId, index) => {
      const row = Math.floor(index / gridSize);
      const col = index % gridSize;
      
      const attributes = this.graph.getNodeAttributes(nodeId);
      if (!attributes.x || !attributes.y) {
        this.graph.setNodeAttribute(nodeId, 'x', col * 100);
        this.graph.setNodeAttribute(nodeId, 'y', row * 100);
      }
    });
  }

  /**
   * Update graph statistics
   */
  updateStatistics() {
    this.statistics.totalNodes = this.graph.order;
    this.statistics.totalEdges = this.graph.size;
    
    // Calculate centrality metrics for importance-based sizing
    const degrees = new Map();
    const inDegrees = new Map();
    const outDegrees = new Map();
    let maxDegree = 0;
    let maxInDegree = 0;
    let maxOutDegree = 0;
    
    // First pass: collect degree information
    this.graph.forEachNode((node) => {
      const degree = this.graph.degree(node);
      const inDegree = this.graph.inDegree(node);
      const outDegree = this.graph.outDegree(node);
      
      degrees.set(node, degree);
      inDegrees.set(node, inDegree);
      outDegrees.set(node, outDegree);
      
      maxDegree = Math.max(maxDegree, degree);
      maxInDegree = Math.max(maxInDegree, inDegree);
      maxOutDegree = Math.max(maxOutDegree, outDegree);
    });
    
    // Second pass: update node sizes based on importance
    this.graph.forEachNode((node) => {
      const degree = degrees.get(node);
      const inDegree = inDegrees.get(node);
      const outDegree = outDegrees.get(node);
      
      // Store degree in metrics
      this.graph.setNodeAttribute(node, 'metrics.degree', degree);
      this.graph.setNodeAttribute(node, 'metrics.inDegree', inDegree);
      this.graph.setNodeAttribute(node, 'metrics.outDegree', outDegree);
      
      // Calculate importance score (weighted combination)
      const degreeScore = maxDegree > 0 ? degree / maxDegree : 0;
      const inDegreeScore = maxInDegree > 0 ? inDegree / maxInDegree : 0;
      const outDegreeScore = maxOutDegree > 0 ? outDegree / maxOutDegree : 0;
      
      // Weight: total connections matter most, but also consider direction
      const importanceScore = (degreeScore * 0.5) + (inDegreeScore * 0.3) + (outDegreeScore * 0.2);
      
      // Get base size from node type
      const baseSize = this.calculateNodeSize(this.nodeMap.get(node));
      
      // Scale size based on importance (min 5, max 30)
      const minSize = 5;
      const maxSize = 30;
      const sizeRange = maxSize - minSize;
      
      // Non-linear scaling for better visual distinction
      const scaledImportance = Math.pow(importanceScore, 0.7); // Slightly compress the range
      const finalSize = minSize + (sizeRange * scaledImportance);
      
      this.graph.setNodeAttribute(node, 'size', Math.max(minSize, Math.min(finalSize, maxSize)));
      this.graph.setNodeAttribute(node, 'importance', importanceScore);
    });
  }

  /**
   * Get the Graphology graph instance
   */
  getGraph() {
    return this.graph;
  }

  /**
   * Get graph statistics
   */
  getStatistics() {
    // Calculate density manually: edges / (nodes * (nodes - 1))
    const nodeCount = this.graph.order;
    const edgeCount = this.graph.size;
    const maxPossibleEdges = nodeCount * (nodeCount - 1);
    const density = maxPossibleEdges > 0 ? edgeCount / maxPossibleEdges : 0;
    
    return {
      ...this.statistics,
      density: density,
      order: nodeCount,
      size: edgeCount
    };
  }

  /**
   * Export graph to various formats
   */
  export(format = 'json') {
    switch(format) {
      case 'json':
        return this.exportToJSON();
      case 'gexf':
        return this.exportToGEXF();
      case 'graphml':
        return this.exportToGraphML();
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  /**
   * Export to JSON format
   */
  exportToJSON() {
    const nodes = [];
    const edges = [];
    
    this.graph.forEachNode((node, attributes) => {
      nodes.push({ id: node, ...attributes });
    });
    
    this.graph.forEachEdge((edge, attributes, source, target) => {
      edges.push({ 
        id: edge, 
        source, 
        target, 
        ...attributes 
      });
    });
    
    return {
      nodes,
      edges,
      metadata: {
        ...this.statistics,
        timestamp: new Date().toISOString()
      }
    };
  }

  /**
   * Export to GEXF format (for Gephi)
   */
  exportToGEXF() {
    // Implementation would go here
    // This is a placeholder
    return '<?xml version="1.0" encoding="UTF-8"?><gexf></gexf>';
  }

  /**
   * Export to GraphML format
   */
  exportToGraphML() {
    // Implementation would go here
    // This is a placeholder
    return '<?xml version="1.0" encoding="UTF-8"?><graphml></graphml>';
  }
}

// Export as default for easier imports
export default CogniMapGraphAdapter;