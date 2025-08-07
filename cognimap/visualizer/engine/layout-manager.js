/**
 * Layout Manager
 * Handles different graph layout algorithms
 */

import forceAtlas2 from 'graphology-layout-forceatlas2';

export class LayoutManager {
  constructor(graph) {
    this.graph = graph;
    this.currentLayout = null;
    this.isRunning = false;
    this.worker = null;
    
    // Layout configurations
    this.layouts = {
      forceAtlas2: {
        name: 'Force Atlas 2',
        description: 'Force-directed layout for natural clustering',
        settings: {
          iterations: 1000,
          settings: {
            gravity: 1,
            scalingRatio: 10,
            strongGravityMode: false,
            barnesHutOptimize: true,
            barnesHutTheta: 0.5,
            edgeWeightInfluence: 1,
            slowDown: 1
          }
        }
      },
      circular: {
        name: 'Circular',
        description: 'Nodes arranged in a circle',
        settings: {
          scale: 500
        }
      },
      random: {
        name: 'Random',
        description: 'Random node placement',
        settings: {
          scale: 500,
          center: 0.5
        }
      },
      grid: {
        name: 'Grid',
        description: 'Nodes arranged in a grid',
        settings: {
          spacing: 100
        }
      },
      hierarchical: {
        name: 'Hierarchical',
        description: 'Tree-like hierarchical layout',
        settings: {
          direction: 'TB',
          levelSpacing: 100,
          nodeSpacing: 50
        }
      }
    };
  }

  /**
   * Apply a layout algorithm
   */
  async applyLayout(layoutName = 'forceAtlas2', options = {}) {
    if (this.isRunning) {
      console.warn('Layout already running');
      return;
    }
    
    console.log(`📐 Applying ${layoutName} layout...`);
    this.isRunning = true;
    this.currentLayout = layoutName;
    
    try {
      switch(layoutName) {
        case 'forceAtlas2':
          await this.applyForceAtlas2(options);
          break;
        case 'circular':
          this.applyCircular(options);
          break;
        case 'random':
          this.applyRandom(options);
          break;
        case 'grid':
          this.applyGrid(options);
          break;
        case 'hierarchical':
          await this.applyHierarchical(options);
          break;
        default:
          throw new Error(`Unknown layout: ${layoutName}`);
      }
      
      console.log(`✅ ${layoutName} layout applied`);
    } catch (error) {
      console.error(`Failed to apply ${layoutName} layout:`, error);
    } finally {
      this.isRunning = false;
    }
  }

  /**
   * Apply ForceAtlas2 layout
   */
  async applyForceAtlas2(options = {}) {
    const settings = {
      ...this.layouts.forceAtlas2.settings.settings,
      ...options
    };
    
    const iterations = options.iterations || this.layouts.forceAtlas2.settings.iterations;
    
    // Apply layout
    forceAtlas2.assign(this.graph, {
      iterations,
      settings
    });
    
    // Alternative: Use web worker for large graphs
    if (this.graph.order > 1000) {
      console.log('Using web worker for large graph...');
      // This would require setting up a web worker
      // For now, we'll use the synchronous version
    }
  }

  /**
   * Apply circular layout
   */
  applyCircular(options = {}) {
    const scale = options.scale || this.layouts.circular.settings.scale;
    const nodes = this.graph.nodes();
    const nodeCount = nodes.length;
    const angleStep = (2 * Math.PI) / nodeCount;
    
    nodes.forEach((node, index) => {
      const angle = index * angleStep;
      const x = scale * Math.cos(angle);
      const y = scale * Math.sin(angle);
      
      this.graph.setNodeAttribute(node, 'x', x);
      this.graph.setNodeAttribute(node, 'y', y);
    });
  }

  /**
   * Apply random layout
   */
  applyRandom(options = {}) {
    const scale = options.scale || this.layouts.random.settings.scale;
    const center = options.center || this.layouts.random.settings.center;
    
    this.graph.forEachNode((node) => {
      const x = (Math.random() - center) * scale;
      const y = (Math.random() - center) * scale;
      
      this.graph.setNodeAttribute(node, 'x', x);
      this.graph.setNodeAttribute(node, 'y', y);
    });
  }

  /**
   * Apply grid layout
   */
  applyGrid(options = {}) {
    const spacing = options.spacing || this.layouts.grid.settings.spacing;
    const nodes = this.graph.nodes();
    const nodeCount = nodes.length;
    const gridSize = Math.ceil(Math.sqrt(nodeCount));
    
    nodes.forEach((node, index) => {
      const row = Math.floor(index / gridSize);
      const col = index % gridSize;
      
      this.graph.setNodeAttribute(node, 'x', col * spacing);
      this.graph.setNodeAttribute(node, 'y', row * spacing);
    });
  }

  /**
   * Apply hierarchical layout
   */
  async applyHierarchical(options = {}) {
    const settings = {
      ...this.layouts.hierarchical.settings,
      ...options
    };
    
    // Detect layers using BFS
    const layers = this.detectLayers();
    
    // Position nodes by layer
    const { direction, levelSpacing, nodeSpacing } = settings;
    
    layers.forEach((layer, depth) => {
      const layerSize = layer.length;
      const startOffset = -(layerSize - 1) * nodeSpacing / 2;
      
      layer.forEach((node, index) => {
        if (direction === 'TB' || direction === 'BT') {
          // Top-Bottom or Bottom-Top
          const y = direction === 'TB' ? depth * levelSpacing : -depth * levelSpacing;
          const x = startOffset + index * nodeSpacing;
          this.graph.setNodeAttribute(node, 'x', x);
          this.graph.setNodeAttribute(node, 'y', y);
        } else {
          // Left-Right or Right-Left
          const x = direction === 'LR' ? depth * levelSpacing : -depth * levelSpacing;
          const y = startOffset + index * nodeSpacing;
          this.graph.setNodeAttribute(node, 'x', x);
          this.graph.setNodeAttribute(node, 'y', y);
        }
      });
    });
  }

  /**
   * Detect layers for hierarchical layout
   */
  detectLayers() {
    const layers = [];
    const visited = new Set();
    const nodeLayer = new Map();
    
    // Find root nodes (nodes with no incoming edges)
    const roots = this.graph.nodes().filter(node => {
      return this.graph.inDegree(node) === 0;
    });
    
    if (roots.length === 0) {
      // If no roots, start with nodes that have the most outgoing edges
      roots.push(...this.graph.nodes().sort((a, b) => {
        return this.graph.outDegree(b) - this.graph.outDegree(a);
      }).slice(0, 1));
    }
    
    // BFS from roots
    let currentLayer = roots;
    let depth = 0;
    
    while (currentLayer.length > 0) {
      layers[depth] = currentLayer;
      currentLayer.forEach(node => {
        visited.add(node);
        nodeLayer.set(node, depth);
      });
      
      // Find next layer
      const nextLayer = [];
      currentLayer.forEach(node => {
        this.graph.forEachOutNeighbor(node, neighbor => {
          if (!visited.has(neighbor)) {
            nextLayer.push(neighbor);
            visited.add(neighbor);
          }
        });
      });
      
      currentLayer = [...new Set(nextLayer)];
      depth++;
    }
    
    // Add any unvisited nodes to the last layer
    this.graph.nodes().forEach(node => {
      if (!visited.has(node)) {
        if (!layers[depth]) layers[depth] = [];
        layers[depth].push(node);
      }
    });
    
    return layers;
  }

  /**
   * Stop running layout
   */
  stop() {
    this.isRunning = false;
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
  }

  /**
   * Get available layouts
   */
  getAvailableLayouts() {
    return Object.keys(this.layouts).map(key => ({
      id: key,
      ...this.layouts[key]
    }));
  }

  /**
   * Get current layout
   */
  getCurrentLayout() {
    return this.currentLayout;
  }

  /**
   * Save layout positions
   */
  savePositions() {
    const positions = {};
    this.graph.forEachNode((node, attributes) => {
      positions[node] = {
        x: attributes.x,
        y: attributes.y
      };
    });
    return positions;
  }

  /**
   * Restore layout positions
   */
  restorePositions(positions) {
    Object.entries(positions).forEach(([node, pos]) => {
      if (this.graph.hasNode(node)) {
        this.graph.setNodeAttribute(node, 'x', pos.x);
        this.graph.setNodeAttribute(node, 'y', pos.y);
      }
    });
  }

  /**
   * Optimize layout for viewing
   */
  optimizeForViewing() {
    // Center the graph
    this.centerGraph();
    
    // Scale to fit viewport
    this.scaleToFit();
  }

  /**
   * Center the graph at origin
   */
  centerGraph() {
    let sumX = 0, sumY = 0;
    let count = 0;
    
    this.graph.forEachNode((node, attributes) => {
      sumX += attributes.x;
      sumY += attributes.y;
      count++;
    });
    
    if (count > 0) {
      const centerX = sumX / count;
      const centerY = sumY / count;
      
      this.graph.forEachNode((node) => {
        const x = this.graph.getNodeAttribute(node, 'x');
        const y = this.graph.getNodeAttribute(node, 'y');
        this.graph.setNodeAttribute(node, 'x', x - centerX);
        this.graph.setNodeAttribute(node, 'y', y - centerY);
      });
    }
  }

  /**
   * Scale graph to fit in standard viewport
   */
  scaleToFit(targetSize = 1000) {
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    this.graph.forEachNode((node, attributes) => {
      minX = Math.min(minX, attributes.x);
      maxX = Math.max(maxX, attributes.x);
      minY = Math.min(minY, attributes.y);
      maxY = Math.max(maxY, attributes.y);
    });
    
    const width = maxX - minX;
    const height = maxY - minY;
    const maxDimension = Math.max(width, height);
    
    if (maxDimension > 0) {
      const scale = targetSize / maxDimension;
      
      this.graph.forEachNode((node) => {
        const x = this.graph.getNodeAttribute(node, 'x');
        const y = this.graph.getNodeAttribute(node, 'y');
        this.graph.setNodeAttribute(node, 'x', x * scale);
        this.graph.setNodeAttribute(node, 'y', y * scale);
      });
    }
  }
}

// Export as default
export default LayoutManager;