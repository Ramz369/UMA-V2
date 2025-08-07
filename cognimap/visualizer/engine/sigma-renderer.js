/**
 * Sigma.js Renderer Wrapper
 * Handles graph rendering and interaction
 */

import Sigma from 'sigma';

export class SigmaRenderer {
  constructor(container, graph) {
    this.container = container;
    this.graph = graph;
    this.sigma = null;
    this.camera = null;
    this.selectedNode = null;
    this.highlightedNodes = new Set();
    this.hoveredNode = null;
    
    // Event handlers
    this.eventHandlers = {
      nodeClick: [],
      nodeHover: [],
      stageClick: [],
      cameraUpdate: []
    };
    
    // Render settings
    this.settings = {
      // Labels
      labelRenderedSizeThreshold: 0,
      labelSize: 14,
      labelWeight: 'normal',
      labelColor: { color: '#000' },
      
      // Edges
      defaultEdgeType: 'line',  // Changed from 'arrow' to 'line'
      defaultEdgeColor: '#ccc',
      edgeReducer: this.edgeReducer.bind(this),
      
      // Nodes  
      defaultNodeColor: '#666',
      nodeReducer: this.nodeReducer.bind(this),
      
      // Interaction
      enableEdgeClickEvents: true,
      enableEdgeHoverEvents: false,
      
      // Performance
      hideEdgesOnMove: false,
      hideLabelsOnMove: false,
      renderLabels: true,
      
      // Stage
      stagePadding: 30,
      zoomToSizeRatioFunction: (ratio) => ratio
    };
  }

  /**
   * Initialize the renderer
   */
  initialize() {
    console.log('🎨 Initializing Sigma renderer...');
    
    // Create Sigma instance
    this.sigma = new Sigma(
      this.graph, 
      this.container,
      this.settings
    );
    
    // Get camera
    this.camera = this.sigma.getCamera();
    
    // Setup event handlers
    this.setupEventHandlers();
    
    // Initial render
    this.render();
    
    console.log('✅ Sigma renderer initialized');
    return this.sigma;
  }

  /**
   * Node reducer - customizes node appearance
   */
  nodeReducer(node, data) {
    const res = { ...data };
    
    // Highlight selected node
    if (this.selectedNode === node) {
      res.highlighted = true;
      res.color = '#ff0000';
      res.size = data.size * 1.5;
    }
    
    // Highlight hovered node
    if (this.hoveredNode === node) {
      res.highlighted = true;
      res.size = data.size * 1.2;
    }
    
    // Highlight nodes in selection
    if (this.highlightedNodes.has(node)) {
      res.highlighted = true;
      res.color = this.adjustColor(data.color, 1.2);
    }
    
    // Fade non-highlighted nodes when selection exists
    if (this.highlightedNodes.size > 0 && !this.highlightedNodes.has(node)) {
      res.color = this.adjustColor(data.color, 0.3);
      res.label = '';
    }
    
    return res;
  }

  /**
   * Edge reducer - customizes edge appearance
   */
  edgeReducer(edge, data) {
    const res = { ...data };
    
    // Get source and target nodes
    const source = this.graph.source(edge);
    const target = this.graph.target(edge);
    
    // Highlight edges connected to selected node
    if (this.selectedNode && (source === this.selectedNode || target === this.selectedNode)) {
      res.color = '#ff0000';
      res.size = 2;
    }
    
    // Highlight edges between highlighted nodes
    if (this.highlightedNodes.has(source) && this.highlightedNodes.has(target)) {
      res.color = this.adjustColor(data.color, 1.5);
      res.size = 2;
    }
    
    // Fade edges when nodes are highlighted
    if (this.highlightedNodes.size > 0 && 
        (!this.highlightedNodes.has(source) || !this.highlightedNodes.has(target))) {
      res.hidden = true;
    }
    
    // Color circular dependencies in red
    if (data.metadata?.circular) {
      res.color = '#ff0000';
      res.size = 3;
    }
    
    return res;
  }

  /**
   * Setup event handlers
   */
  setupEventHandlers() {
    // Node click
    this.sigma.on('clickNode', (event) => {
      const node = event.node;
      this.selectNode(node);
      this.triggerEvent('nodeClick', { node, event });
    });
    
    // Node hover
    this.sigma.on('enterNode', (event) => {
      this.hoveredNode = event.node;
      this.sigma.refresh();
      this.triggerEvent('nodeHover', { node: event.node, event });
    });
    
    this.sigma.on('leaveNode', () => {
      this.hoveredNode = null;
      this.sigma.refresh();
    });
    
    // Stage click (deselect)
    this.sigma.on('clickStage', (event) => {
      this.clearSelection();
      this.triggerEvent('stageClick', { event });
    });
    
    // Camera updates
    this.sigma.on('cameraUpdated', (state) => {
      this.triggerEvent('cameraUpdate', { state });
    });
    
    // Edge click
    this.sigma.on('clickEdge', (event) => {
      console.log('Edge clicked:', event);
    });
  }

  /**
   * Select a node
   */
  selectNode(nodeId) {
    this.selectedNode = nodeId;
    
    // Highlight node and its neighbors
    this.highlightedNodes.clear();
    this.highlightedNodes.add(nodeId);
    
    // Add neighbors
    this.graph.forEachNeighbor(nodeId, (neighbor) => {
      this.highlightedNodes.add(neighbor);
    });
    
    this.sigma.refresh();
  }

  /**
   * Clear selection
   */
  clearSelection() {
    this.selectedNode = null;
    this.highlightedNodes.clear();
    this.sigma.refresh();
  }

  /**
   * Highlight specific nodes
   */
  highlightNodes(nodeIds) {
    this.highlightedNodes.clear();
    nodeIds.forEach(id => this.highlightedNodes.add(id));
    this.sigma.refresh();
  }

  /**
   * Focus on a specific node
   */
  focusNode(nodeId, animate = true) {
    const nodePosition = this.sigma.getNodeDisplayData(nodeId);
    
    if (nodePosition) {
      if (animate) {
        this.camera.animatedGoTo({
          x: nodePosition.x,
          y: nodePosition.y,
          ratio: 0.5,
          duration: 500
        });
      } else {
        this.camera.setState({
          x: nodePosition.x,
          y: nodePosition.y,
          ratio: 0.5
        });
      }
    }
  }

  /**
   * Zoom to fit all nodes
   */
  zoomToFit(animate = true) {
    if (animate) {
      this.camera.animatedReset({ duration: 500 });
    } else {
      this.camera.reset();
    }
  }

  /**
   * Set zoom level
   */
  setZoom(ratio, animate = true) {
    if (animate) {
      this.camera.animatedGoTo({ ratio, duration: 300 });
    } else {
      this.camera.setState({ ratio });
    }
  }

  /**
   * Pan camera
   */
  pan(x, y, animate = true) {
    const currentState = this.camera.getState();
    
    if (animate) {
      this.camera.animatedGoTo({
        x: currentState.x + x,
        y: currentState.y + y,
        duration: 300
      });
    } else {
      this.camera.setState({
        x: currentState.x + x,
        y: currentState.y + y
      });
    }
  }

  /**
   * Update settings
   */
  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings };
    this.sigma.setSetting(Object.keys(newSettings)[0], Object.values(newSettings)[0]);
    this.sigma.refresh();
  }

  /**
   * Toggle labels
   */
  toggleLabels(show) {
    this.updateSettings({ renderLabels: show });
  }

  /**
   * Toggle edges
   */
  toggleEdges(show) {
    this.updateSettings({ renderEdges: show });
  }

  /**
   * Render the graph
   */
  render() {
    this.sigma.refresh();
  }

  /**
   * Take a screenshot
   */
  screenshot(format = 'png') {
    const canvas = this.container.querySelector('canvas');
    if (canvas) {
      return canvas.toDataURL(`image/${format}`);
    }
    return null;
  }

  /**
   * Register event handler
   */
  on(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].push(handler);
    }
  }

  /**
   * Trigger event
   */
  triggerEvent(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => handler(data));
    }
  }

  /**
   * Adjust color brightness
   */
  adjustColor(color, factor) {
    // Simple color adjustment
    const hex = color.replace('#', '');
    const rgb = parseInt(hex, 16);
    const r = Math.min(255, Math.floor(((rgb >> 16) & 0xff) * factor));
    const g = Math.min(255, Math.floor(((rgb >> 8) & 0xff) * factor));
    const b = Math.min(255, Math.floor((rgb & 0xff) * factor));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
  }

  /**
   * Get node at position
   */
  getNodeAtPosition(x, y) {
    // This would need implementation based on Sigma's internal methods
    return null;
  }

  /**
   * Destroy the renderer
   */
  destroy() {
    if (this.sigma) {
      this.sigma.kill();
      this.sigma = null;
    }
  }

  /**
   * Get Sigma instance
   */
  getSigma() {
    return this.sigma;
  }

  /**
   * Get camera instance
   */
  getCamera() {
    return this.camera;
  }
}

// Export as default
export default SigmaRenderer;