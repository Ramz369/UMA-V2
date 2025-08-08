#!/usr/bin/env node

/**
 * Update visualization graph with semantic enhancements
 * This adds AI-suggested connections and semantic tags to nodes
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load the current graph
const graphPath = path.join(__dirname, 'output', 'architecture_graph.json');
const graphData = JSON.parse(fs.readFileSync(graphPath, 'utf8'));

console.log('📊 Enhancing graph with semantic features...');
console.log(`  Nodes: ${graphData.nodes.length}`);
console.log(`  Edges: ${graphData.edges.length}`);

// Add semantic enhancements to nodes
let enhanced = 0;
graphData.nodes.forEach(node => {
  // Add semantic fingerprint based on node type and name
  const semanticTags = [];
  const patterns = [];
  
  // Extract semantic tags from node name and type
  if (node.name) {
    if (node.name.includes('Agent')) {
      semanticTags.push('agent', 'core');
      patterns.push('Agent Pattern');
    }
    if (node.name.includes('Tool')) {
      semanticTags.push('tool', 'utility');
      patterns.push('Tool Pattern');
    }
    if (node.name.includes('Test')) {
      semanticTags.push('test', 'quality');
      patterns.push('Test Suite');
    }
    if (node.name.includes('Config')) {
      semanticTags.push('configuration');
      patterns.push('Configuration');
    }
    if (node.name.includes('Engine')) {
      semanticTags.push('engine', 'core');
      patterns.push('Engine Pattern');
    }
  }
  
  // Add based on file type
  if (node.filepath) {
    if (node.filepath.includes('test')) {
      semanticTags.push('test');
    }
    if (node.filepath.includes('config')) {
      semanticTags.push('configuration');
    }
    if (node.filepath.includes('agent')) {
      semanticTags.push('agent');
    }
    if (node.filepath.includes('tool')) {
      semanticTags.push('tool');
    }
  }
  
  // Add semantic fingerprint
  if (semanticTags.length > 0) {
    node.semantic_fingerprint = {
      tags: [...new Set(semanticTags)],
      patterns: [...new Set(patterns)],
      confidence: 0.8
    };
    node.semantic_tags = [...new Set(semanticTags)];
    enhanced++;
  }
});

console.log(`  Enhanced ${enhanced} nodes with semantic data`);

// Add AI-suggested connections based on semantic similarity
const suggestedEdges = [];

// Find nodes that should be connected based on patterns
const agentNodes = graphData.nodes.filter(n => 
  n.semantic_tags && n.semantic_tags.includes('agent')
);
const toolNodes = graphData.nodes.filter(n => 
  n.semantic_tags && n.semantic_tags.includes('tool')
);

// Suggest connections between agents and tools that aren't connected
agentNodes.forEach(agent => {
  toolNodes.forEach(tool => {
    // Check if connection already exists
    const exists = graphData.edges.some(e => 
      (e.source === agent.id && e.target === tool.id) ||
      (e.target === agent.id && e.source === tool.id)
    );
    
    if (!exists && suggestedEdges.length < 10) {
      // Only suggest if names seem related
      const agentName = agent.name?.toLowerCase() || '';
      const toolName = tool.name?.toLowerCase() || '';
      
      // Simple heuristic: suggest if they share common words
      const agentWords = agentName.split(/[_\-\s]/);
      const toolWords = toolName.split(/[_\-\s]/);
      const commonWords = agentWords.filter(w => toolWords.includes(w));
      
      if (commonWords.length > 0) {
        suggestedEdges.push({
          source: agent.id,
          target: tool.id,
          edgeType: 'suggested',
          confidence: 0.6,
          metadata: {
            reason: `Semantic similarity: ${commonWords.join(', ')}`,
            is_suggestion: true,
            style: 'dashed'
          }
        });
      }
    }
  });
});

// Add gap analysis suggestions
const orphanedNodes = graphData.nodes.filter(node => {
  const hasIncoming = graphData.edges.some(e => e.target === node.id);
  const hasOutgoing = graphData.edges.some(e => e.source === node.id);
  return !hasIncoming && !hasOutgoing;
});

console.log(`  Found ${orphanedNodes.length} orphaned nodes`);
console.log(`  Generated ${suggestedEdges.length} suggested connections`);

// Add suggested edges to graph
graphData.edges.push(...suggestedEdges);

// Add metadata
graphData.metadata = {
  ...graphData.metadata,
  semantic_analysis: {
    timestamp: new Date().toISOString(),
    enhanced_nodes: enhanced,
    suggested_connections: suggestedEdges.length,
    orphaned_nodes: orphanedNodes.length,
    patterns_detected: ['Agent Pattern', 'Tool Pattern', 'Test Suite', 'Configuration']
  }
};

// Save enhanced graph
const enhancedPath = path.join(__dirname, 'output', 'architecture_graph_enhanced.json');
fs.writeFileSync(enhancedPath, JSON.stringify(graphData, null, 2));

console.log(`✅ Enhanced graph saved to: ${enhancedPath}`);
console.log('\n📈 Summary:');
console.log(`  - Total nodes: ${graphData.nodes.length}`);
console.log(`  - Total edges: ${graphData.edges.length}`);
console.log(`  - Semantic enhancements: ${enhanced}`);
console.log(`  - Suggested connections: ${suggestedEdges.length}`);
console.log(`  - Orphaned components: ${orphanedNodes.length}`);

// Generate simple improvement roadmap
const roadmapPath = path.join(__dirname, 'output', 'improvement_roadmap.md');
const roadmap = `# CogniMap Improvement Roadmap

## Analysis Date: ${new Date().toISOString()}

## Semantic Analysis Results
- **Nodes analyzed**: ${graphData.nodes.length}
- **Semantic tags added**: ${enhanced}
- **Suggested connections**: ${suggestedEdges.length}
- **Orphaned components**: ${orphanedNodes.length}

## Detected Patterns
${[...new Set(graphData.nodes.flatMap(n => n.semantic_fingerprint?.patterns || []))].map(p => `- ${p}`).join('\n')}

## Orphaned Components
${orphanedNodes.slice(0, 10).map(n => `- ${n.name || n.id} (${n.filepath || 'unknown'})`).join('\n')}

## Suggested Connections
${suggestedEdges.slice(0, 10).map(e => {
  const source = graphData.nodes.find(n => n.id === e.source);
  const target = graphData.nodes.find(n => n.id === e.target);
  return `- ${source?.name || e.source} → ${target?.name || e.target}: ${e.metadata.reason}`;
}).join('\n')}

## Recommendations
1. **Immediate**: Connect orphaned components to main architecture
2. **Short-term**: Review suggested connections for implementation
3. **Long-term**: Refactor to reduce coupling between layers
`;

fs.writeFileSync(roadmapPath, roadmap);
console.log(`\n📝 Roadmap saved to: ${roadmapPath}`);