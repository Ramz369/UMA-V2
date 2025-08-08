#!/usr/bin/env python3
"""
CogniMap AI Server - Live Analysis Engine
Connects all the disconnected parts and provides real-time AI analysis
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Web server imports
from aiohttp import web
from aiohttp import ClientSession
import aiohttp_cors
from dotenv import load_dotenv

# CogniMap imports
from graph.graph_analyzer import GraphAnalyzer
from semantic_engine.semantic_analyzer import SemanticAnalyzer
from semantic_engine.deepseek_integration import request_improvements
from core.fingerprint import Fingerprint
from scripts.deepseek_scenario_report import generate_report as deepseek_generate

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CogniMapAIServer:
    """Main AI server that connects all CogniMap components"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        self.websocket_connections = set()
        
        # Configuration
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.port = int(os.getenv('COGNIMAP_PORT', 8090))
        self.ws_port = int(os.getenv('WEBSOCKET_PORT', 8091))
        self.enable_live = os.getenv('ENABLE_LIVE_ANALYSIS', 'true').lower() == 'true'
        
        # Load graph data
        self.graph_path = Path(__file__).parent / 'visualizer/output/architecture_graph_enhanced.json'
        self.graph_data = self.load_graph()
        
        # Initialize analyzers
        self.graph_analyzer = GraphAnalyzer(self.graph_data) if self.graph_data else None
        self.semantic_analyzer = SemanticAnalyzer(
            root_path=Path(__file__).parent.parent,
            memory_path="reports/cognimap/semantic"
        )
        
        logger.info(f"CogniMap AI Server initialized. DeepSeek API: {'✓' if self.api_key else '✗'}")
    
    def load_graph(self) -> Optional[Dict]:
        """Load the architecture graph"""
        if self.graph_path.exists():
            with open(self.graph_path, 'r') as f:
                return json.load(f)
        logger.warning(f"Graph file not found: {self.graph_path}")
        return None
    
    def setup_routes(self):
        """Setup HTTP routes"""
        # Analysis endpoints
        self.app.router.add_get('/api/status', self.handle_status)
        self.app.router.add_post('/api/analyze/node', self.handle_analyze_node)
        self.app.router.add_post('/api/analyze/graph', self.handle_analyze_graph)
        self.app.router.add_post('/api/analyze/gaps', self.handle_analyze_gaps)
        self.app.router.add_post('/api/analyze/patterns', self.handle_analyze_patterns)
        
        # DeepSeek endpoints
        self.app.router.add_post('/api/deepseek/analyze', self.handle_deepseek_analyze)
        self.app.router.add_post('/api/deepseek/scenario', self.handle_deepseek_scenario)
        
        # WebSocket for live updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Static files (if needed)
        self.app.router.add_static('/', path=Path(__file__).parent / 'visualizer', name='static')
    
    def setup_cors(self):
        """Setup CORS for browser access"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def handle_status(self, request):
        """API status endpoint"""
        return web.json_response({
            'status': 'online',
            'deepseek_enabled': bool(self.api_key),
            'live_analysis': self.enable_live,
            'graph_loaded': bool(self.graph_data),
            'nodes': len(self.graph_data['nodes']) if self.graph_data else 0,
            'edges': len(self.graph_data['edges']) if self.graph_data else 0,
            'timestamp': datetime.now().isoformat()
        })
    
    async def handle_analyze_node(self, request):
        """Analyze a specific node with AI"""
        data = await request.json()
        node_id = data.get('node_id')
        
        if not node_id:
            return web.json_response({'error': 'node_id required'}, status=400)
        
        # Find node in graph
        node = None
        for n in self.graph_data['nodes']:
            if n['id'] == node_id:
                node = n
                break
        
        if not node:
            return web.json_response({'error': 'Node not found'}, status=404)
        
        analysis = {
            'node': node,
            'metrics': {},
            'patterns': [],
            'recommendations': [],
            'ai_insights': {}
        }
        
        # Run graph analysis
        if self.graph_analyzer:
            graph_analysis = self.graph_analyzer.analyze()
            # Extract relevant parts for this node
            analysis['metrics'] = {
                'complexity': graph_analysis.get('complexity', {}).get('nodes', {}).get(node_id, 0),
                'coupling': self._calculate_node_coupling(node_id),
                'cohesion': self._calculate_node_cohesion(node_id)
            }
            analysis['recommendations'] = graph_analysis.get('recommendations', [])
        
        # Run semantic analysis
        if node.get('filepath'):
            from semantic_engine.pattern_detector import detect_patterns
            patterns = detect_patterns(node.get('name', ''))
            analysis['patterns'] = patterns
        
        # Run DeepSeek analysis if API key available
        if self.api_key and self.enable_live:
            try:
                ai_result = await self._deepseek_analyze_node(node)
                analysis['ai_insights'] = ai_result
            except Exception as e:
                logger.error(f"DeepSeek analysis failed: {e}")
                analysis['ai_insights'] = {'error': str(e)}
        
        # Send to WebSocket clients
        await self.broadcast_update({
            'type': 'node_analysis',
            'data': analysis
        })
        
        return web.json_response(analysis)
    
    async def handle_analyze_graph(self, request):
        """Analyze entire graph architecture"""
        if not self.graph_analyzer:
            return web.json_response({'error': 'Graph not loaded'}, status=500)
        
        analysis = self.graph_analyzer.analyze()
        
        # Add semantic analysis
        self.semantic_analyzer.run()
        
        # Send to WebSocket clients
        await self.broadcast_update({
            'type': 'graph_analysis',
            'data': analysis
        })
        
        return web.json_response(analysis)
    
    async def handle_analyze_gaps(self, request):
        """Find and analyze architectural gaps"""
        # Run semantic analyzer to find gaps
        self.semantic_analyzer.scan_symbols()
        self.semantic_analyzer.map_references()
        self.semantic_analyzer.build_fingerprints()
        gaps = self.semantic_analyzer.analyze_gaps()
        
        # Enhance with AI if available
        if self.api_key and gaps:
            try:
                enhanced_gaps = await self._deepseek_enhance_gaps(gaps)
                gaps = enhanced_gaps
            except Exception as e:
                logger.error(f"Gap enhancement failed: {e}")
        
        result = {
            'gaps': gaps,
            'total': len(gaps),
            'categories': self._categorize_gaps(gaps)
        }
        
        # Send to WebSocket clients
        await self.broadcast_update({
            'type': 'gap_analysis',
            'data': result
        })
        
        return web.json_response(result)
    
    async def handle_analyze_patterns(self, request):
        """Detect architectural patterns"""
        patterns = {}
        
        # Analyze each node for patterns
        from semantic_engine.pattern_detector import detect_patterns
        for node in self.graph_data['nodes']:
            node_patterns = detect_patterns(node.get('name', ''))
            if node_patterns:
                patterns[node['id']] = node_patterns
        
        result = {
            'patterns': patterns,
            'summary': self._summarize_patterns(patterns)
        }
        
        return web.json_response(result)
    
    async def handle_deepseek_analyze(self, request):
        """Direct DeepSeek analysis endpoint"""
        if not self.api_key:
            return web.json_response({'error': 'DeepSeek API key not configured'}, status=503)
        
        data = await request.json()
        context = data.get('context', '')
        
        try:
            # Use the existing deepseek_scenario_report function
            from scripts.deepseek_scenario_report import collect_repo_context
            if not context:
                context = collect_repo_context(Path(__file__).parent.parent)
            
            report = deepseek_generate(context, self.api_key)
            
            # Save report
            report_path = Path("reports/cognimap/deepseek_scenario_report.md")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report)
            
            return web.json_response({
                'success': True,
                'report': report,
                'saved_to': str(report_path)
            })
        except Exception as e:
            logger.error(f"DeepSeek analysis error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_deepseek_scenario(self, request):
        """Generate scenario report with DeepSeek"""
        if not self.api_key:
            return web.json_response({'error': 'DeepSeek API key not configured'}, status=503)
        
        # Run full scenario analysis
        try:
            # Collect context
            from scripts.deepseek_scenario_report import collect_repo_context
            context = collect_repo_context(Path(__file__).parent.parent)
            
            # Generate report
            report = deepseek_generate(context, self.api_key)
            
            # Parse and structure report
            structured = self._parse_scenario_report(report)
            
            # Send to WebSocket clients
            await self.broadcast_update({
                'type': 'scenario_report',
                'data': structured
            })
            
            return web.json_response(structured)
        except Exception as e:
            logger.error(f"Scenario generation error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for live updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websocket_connections.add(ws)
        
        try:
            await ws.send_json({
                'type': 'connected',
                'message': 'Connected to CogniMap AI Server'
            })
            
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_websocket_message(ws, data)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        finally:
            self.websocket_connections.discard(ws)
        
        return ws
    
    async def handle_websocket_message(self, ws, data):
        """Handle incoming WebSocket messages"""
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await ws.send_json({'type': 'pong'})
        elif msg_type == 'analyze_node':
            # Trigger node analysis
            node_id = data.get('node_id')
            # ... implement analysis
        # Add more message handlers as needed
    
    async def broadcast_update(self, data):
        """Broadcast update to all WebSocket clients"""
        if self.websocket_connections:
            await asyncio.gather(
                *[ws.send_json(data) for ws in self.websocket_connections],
                return_exceptions=True
            )
    
    def _calculate_node_coupling(self, node_id):
        """Calculate coupling metric for a node"""
        incoming = 0
        outgoing = 0
        for edge in self.graph_data['edges']:
            if edge['source'] == node_id:
                outgoing += 1
            elif edge['target'] == node_id:
                incoming += 1
        return {'incoming': incoming, 'outgoing': outgoing, 'total': incoming + outgoing}
    
    def _calculate_node_cohesion(self, node_id):
        """Calculate cohesion metric for a node"""
        # Simplified cohesion calculation
        node = next((n for n in self.graph_data['nodes'] if n['id'] == node_id), None)
        if node:
            tags = node.get('semantic_tags', [])
            return len(tags) / 10.0  # Normalized score
        return 0
    
    def _categorize_gaps(self, gaps):
        """Categorize gaps by type"""
        categories = {}
        for gap in gaps:
            tag = gap.get('tag', 'unknown')
            if tag not in categories:
                categories[tag] = []
            categories[tag].append(gap)
        return categories
    
    def _summarize_patterns(self, patterns):
        """Summarize detected patterns"""
        summary = {}
        for node_id, node_patterns in patterns.items():
            for pattern in node_patterns:
                if pattern not in summary:
                    summary[pattern] = 0
                summary[pattern] += 1
        return summary
    
    def _parse_scenario_report(self, report):
        """Parse markdown scenario report into structured data"""
        # Simple parsing - can be enhanced
        lines = report.split('\n')
        structured = {
            'raw': report,
            'sections': {},
            'recommendations': [],
            'gaps': []
        }
        
        current_section = None
        for line in lines:
            if line.startswith('##'):
                current_section = line.strip('# ').lower().replace(' ', '_')
                structured['sections'][current_section] = []
            elif current_section and line.strip():
                structured['sections'][current_section].append(line.strip())
        
        return structured
    
    async def _deepseek_analyze_node(self, node):
        """Analyze a node with DeepSeek"""
        prompt = f"""
        Analyze this software component:
        Name: {node.get('name')}
        Type: {node.get('type')}
        Language: {node.get('language')}
        Semantic Tags: {node.get('semantic_tags', [])}
        Filepath: {node.get('filepath')}
        
        Provide:
        1. Purpose and responsibility
        2. Potential improvements
        3. Missing connections
        4. Architectural concerns
        """
        
        # Call DeepSeek API
        async with ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a software architecture expert."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()
                return data['choices'][0]['message']['content']
    
    async def _deepseek_enhance_gaps(self, gaps):
        """Enhance gap analysis with DeepSeek insights"""
        # Implementation for gap enhancement
        return gaps
    
    def run(self):
        """Start the AI server"""
        logger.info(f"Starting CogniMap AI Server on port {self.port}")
        web.run_app(self.app, host='0.0.0.0', port=self.port)


if __name__ == '__main__':
    server = CogniMapAIServer()
    server.run()