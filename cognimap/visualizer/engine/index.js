/**
 * CogniMap Visualization Engine
 * Main entry point for the visualization system
 */

import { CogniMapGraphAdapter } from './graph-adapter.js';
import { SigmaRenderer } from './sigma-renderer.js';
import { LayoutManager } from './layout-manager.js';

export class CogniMapVisualizer {
  constructor(container, options = {}) {
    // Container element
    if (typeof container === 'string') {
      this.container = document.getElementById(container);
    } else {
      this.container = container;
    }
    
    if (!this.container) {
      throw new Error('Container element not found');
    }
    
    // Options
    this.options = {
      defaultLayout: 'forceAtlas2',
      autoLayout: true,
      renderLabels: true,
      ...options
    };
    
    // Core components
    this.adapter = new CogniMapGraphAdapter();
    this.graph = null;
    this.renderer = null;
    this.layoutManager = null;
    
    // State
    this.isInitialized = false;
    this.data = null;
  }

  /**
   * Initialize the visualizer with data
   */
  async initialize(data) {
    console.log('🚀 Initializing CogniMap Visualizer...');
    
    try {
      // Load data into graph
      if (data) {
        await this.loadData(data);
      }
      
      // Initialize renderer
      if (this.graph) {
        this.renderer = new SigmaRenderer(this.container, this.graph);
        this.renderer.initialize();
        
        // Initialize layout manager
        this.layoutManager = new LayoutManager(this.graph);
        
        // Apply default layout if auto-layout is enabled
        if (this.options.autoLayout) {
          await this.applyLayout(this.options.defaultLayout);
        }
        
        // Setup event handlers
        this.setupEventHandlers();
        
        this.isInitialized = true;
        console.log('✅ CogniMap Visualizer initialized');
      }
    } catch (error) {
      console.error('Failed to initialize visualizer:', error);
      throw error;
    }
    
    return this;
  }

  /**
   * Load data into the graph
   */
  async loadData(data) {
    console.log('📊 Loading data...');
    
    // Handle different data sources
    if (typeof data === 'string') {
      // URL or file path
      data = await this.fetchData(data);
    }
    
    // Load into adapter
    this.graph = await this.adapter.loadFromCogniMap(data);
    this.data = data;
    
    // If already initialized, update renderer
    if (this.renderer) {
      this.renderer.destroy();
      this.renderer = new SigmaRenderer(this.container, this.graph);
      this.renderer.initialize();
      
      if (this.options.autoLayout) {
        await this.applyLayout(this.options.defaultLayout);
      }
    }
    
    return this.graph;
  }

  /**
   * Fetch data from URL
   */
  async fetchData(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
  }

  /**
   * Apply a layout algorithm
   */
  async applyLayout(layoutName, options = {}) {
    if (!this.layoutManager) {
      console.warn('Layout manager not initialized');
      return;
    }
    
    await this.layoutManager.applyLayout(layoutName, options);
    
    // Optimize for viewing
    this.layoutManager.optimizeForViewing();
    
    // Refresh renderer
    if (this.renderer) {
      this.renderer.render();
      this.renderer.zoomToFit();
    }
  }

  /**
   * Setup event handlers
   */
  setupEventHandlers() {
    // Node click handler
    this.renderer.on('nodeClick', ({ node }) => {
      console.log('Node clicked:', node);
      const nodeData = this.graph.getNodeAttributes(node);
      this.onNodeClick(node, nodeData);
    });
    
    // Node hover handler
    this.renderer.on('nodeHover', ({ node }) => {
      const nodeData = this.graph.getNodeAttributes(node);
      this.onNodeHover(node, nodeData);
    });
    
    // Stage click handler
    this.renderer.on('stageClick', () => {
      this.onStageClick();
    });
  }

  /**
   * Node click handler
   */
  onNodeClick(nodeId, nodeData) {
    // Override this method for custom behavior
    console.log('Node details:', {
      id: nodeId,
      type: nodeData.nodeType,
      filepath: nodeData.filepath,
      metrics: nodeData.metrics,
      fingerprint: nodeData.fingerprint
    });
  }

  /**
   * Node hover handler
   */
  onNodeHover(nodeId, nodeData) {
    // Override this method for custom behavior
  }

  /**
   * Stage click handler
   */
  onStageClick() {
    // Override this method for custom behavior
  }

  /**
   * Search nodes
   */
  searchNodes(query) {
    const results = [];
    const lowerQuery = query.toLowerCase();
    
    this.graph.forEachNode((node, attributes) => {
      if (attributes.label.toLowerCase().includes(lowerQuery) ||
          attributes.filepath?.toLowerCase().includes(lowerQuery) ||
          attributes.nodeType?.toLowerCase().includes(lowerQuery) ||
          attributes.semantic_tags?.some(tag => tag.toLowerCase().includes(lowerQuery))) {
        results.push({ id: node, ...attributes });
      }
    });
    
    return results;
  }

  /**
   * Filter nodes
   */
  filterNodes(filterFn) {
    const nodesToShow = new Set();
    
    this.graph.forEachNode((node, attributes) => {
      if (filterFn(node, attributes)) {
        nodesToShow.add(node);
      }
    });
    
    // Hide non-matching nodes
    this.graph.forEachNode((node) => {
      this.graph.setNodeAttribute(node, 'hidden', !nodesToShow.has(node));
    });
    
    // Hide edges where either endpoint is hidden
    this.graph.forEachEdge((edge, attributes, source, target) => {
      const hidden = !nodesToShow.has(source) || !nodesToShow.has(target);
      this.graph.setEdgeAttribute(edge, 'hidden', hidden);
    });
    
    this.renderer.render();
  }

  /**
   * Reset filters
   */
  resetFilters() {
    this.graph.forEachNode((node) => {
      this.graph.setNodeAttribute(node, 'hidden', false);
    });
    
    this.graph.forEachEdge((edge) => {
      this.graph.setEdgeAttribute(edge, 'hidden', false);
    });
    
    this.renderer.render();
  }

  /**
   * Get graph statistics
   */
  getStatistics() {
    return {
      ...this.adapter.getStatistics(),
      currentLayout: this.layoutManager?.getCurrentLayout(),
      zoom: this.renderer?.getCamera()?.getState().ratio
    };
  }

  /**
   * Export visualization
   */
  export(format = 'json') {
    switch(format) {
      case 'json':
        return this.adapter.export('json');
      case 'png':
        return this.renderer.screenshot('png');
      case 'svg':
        // Would need SVG renderer
        console.warn('SVG export not yet implemented');
        return null;
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  /**
   * Destroy the visualizer
   */
  destroy() {
    if (this.renderer) {
      this.renderer.destroy();
    }
    this.graph = null;
    this.adapter = null;
    this.layoutManager = null;
    this.isInitialized = false;
  }

  /**
   * Get the graph instance
   */
  getGraph() {
    return this.graph;
  }

  /**
   * Get the renderer instance
   */
  getRenderer() {
    return this.renderer;
  }

  /**
   * Get the layout manager instance
   */
  getLayoutManager() {
    return this.layoutManager;
  }
}

// Export components for individual use
export { CogniMapGraphAdapter } from './graph-adapter.js';
export { SigmaRenderer } from './sigma-renderer.js';
export { LayoutManager } from './layout-manager.js';

// Export as default
export default CogniMapVisualizer;