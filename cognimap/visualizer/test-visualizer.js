#!/usr/bin/env node

/**
 * Test script for CogniMap Visualizer
 * Verifies that all components work correctly
 */

const fs = require('fs');
const path = require('path');

// Load the graph data
const dataPath = path.join(__dirname, 'output', 'architecture_graph.json');
const graphData = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));

console.log('🧪 Testing CogniMap Visualizer Components');
console.log('=========================================\n');

// Test 1: Data structure validation
console.log('✅ Test 1: Data Structure');
console.log(`  - Nodes: ${graphData.nodes.length}`);
console.log(`  - Edges: ${graphData.edges.length}`);

// Validate node structure
const sampleNode = graphData.nodes[0];
console.log('\n📊 Sample Node Structure:');
console.log(`  - ID: ${sampleNode.id}`);
console.log(`  - Type: ${sampleNode.type}`);
console.log(`  - Filepath: ${sampleNode.filepath}`);
console.log(`  - Fingerprint: ${sampleNode.fingerprint ? 'Present' : 'Missing'}`);

// Validate edge structure  
const sampleEdge = graphData.edges[0];
console.log('\n🔗 Sample Edge Structure:');
console.log(`  - Source: ${sampleEdge.source}`);
console.log(`  - Target: ${sampleEdge.target}`);
console.log(`  - Type: ${sampleEdge.type || 'default'}`);

// Test 2: Node type distribution
console.log('\n✅ Test 2: Node Type Distribution');
const typeCount = {};
graphData.nodes.forEach(node => {
  const type = node.type || 'unknown';
  typeCount[type] = (typeCount[type] || 0) + 1;
});

Object.entries(typeCount).forEach(([type, count]) => {
  console.log(`  - ${type}: ${count} nodes`);
});

// Test 3: Edge connectivity
console.log('\n✅ Test 3: Edge Connectivity');
const nodeIds = new Set(graphData.nodes.map(n => n.id));
let validEdges = 0;
let invalidEdges = 0;

graphData.edges.forEach(edge => {
  if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
    validEdges++;
  } else {
    invalidEdges++;
  }
});

console.log(`  - Valid edges: ${validEdges}`);
console.log(`  - Invalid edges: ${invalidEdges}`);

// Test 4: Check if webpack bundle exists
console.log('\n✅ Test 4: Bundle Status');
const bundlePath = path.join(__dirname, 'dist', 'bundle.js');
if (fs.existsSync(bundlePath)) {
  const stats = fs.statSync(bundlePath);
  console.log(`  - Bundle exists: ${bundlePath}`);
  console.log(`  - Bundle size: ${(stats.size / 1024).toFixed(2)} KB`);
} else {
  console.log('  ❌ Bundle not found! Run "npm run build" first.');
}

// Test 5: HTML files
console.log('\n✅ Test 5: HTML Files');
const htmlFiles = ['index.html', 'test.html'];
htmlFiles.forEach(file => {
  const htmlPath = path.join(__dirname, file);
  if (fs.existsSync(htmlPath)) {
    console.log(`  - ${file}: ✓ exists`);
  } else {
    console.log(`  - ${file}: ✗ missing`);
  }
});

// Summary
console.log('\n=========================================');
console.log('📈 Summary:');
console.log(`  - Graph has ${graphData.nodes.length} nodes and ${graphData.edges.length} edges`);
console.log(`  - All edges are valid: ${invalidEdges === 0 ? '✅' : '❌'}`);
console.log(`  - Bundle is built: ${fs.existsSync(bundlePath) ? '✅' : '❌'}`);
console.log('\n🚀 Ready to visualize! Open test.html in a browser.');
console.log('   Run: python3 -m http.server 8080');
console.log('   Then visit: http://localhost:8080/test.html');