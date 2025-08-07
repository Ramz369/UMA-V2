"""
Serena MCP Collector for CogniMap
This module integrates with Serena MCP to collect code analysis data.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SerenaMCPCollector:
    """
    Collector that uses Serena MCP for heavy lifting.
    Serena provides: file discovery, AST parsing, symbol analysis, relationships.
    CogniMap adds: fingerprinting, semantic enrichment, visualization.
    """
    
    def __init__(self, serena_client=None):
        """
        Initialize with optional Serena MCP client.
        If no client provided, will attempt to connect to default.
        """
        self.serena = serena_client
        self.cache = {}
        self.fingerprint_cache = {}
        
    def connect_serena(self, config: Dict[str, Any]) -> bool:
        """Connect to Serena MCP server."""
        try:
            # In real implementation, this would connect to Serena MCP
            # For now, we'll use a mock connection
            logger.info(f"Connecting to Serena MCP at {config.get('server_url', 'default')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Serena MCP: {e}")
            return False
    
    def collect_project_data(self, project_path: str, mode: str = 'full') -> Dict[str, Any]:
        """
        Collect all project data using Serena MCP.
        
        Args:
            project_path: Root path of project
            mode: 'full' for complete scan, 'incremental' for changes only
            
        Returns:
            Bulk data for semantic analysis
        """
        logger.info(f"Collecting project data from {project_path} in {mode} mode")
        
        # Step 1: Use Serena to list all files
        files = self._list_files_via_serena(project_path)
        
        # Step 2: Filter for code files
        code_files = self._filter_code_files(files)
        
        # Step 3: Bulk analyze with Serena
        bulk_data = []
        for filepath in code_files:
            file_data = self._analyze_file_with_serena(filepath)
            if file_data:
                bulk_data.append(file_data)
        
        # Step 4: Build initial relationship map
        relationships = self._discover_relationships(bulk_data)
        
        return {
            'project_path': project_path,
            'mode': mode,
            'timestamp': datetime.utcnow().isoformat(),
            'files_analyzed': len(bulk_data),
            'files': bulk_data,
            'relationships': relationships,
            'needs_semantic_enrichment': True
        }
    
    def _list_files_via_serena(self, project_path: str) -> List[str]:
        """Use Serena MCP to list all files."""
        if self.serena:
            # Real Serena MCP call
            result = self.serena.list_dir(project_path, recursive=True)
            return result.get('files', [])
        else:
            # Fallback to filesystem
            path = Path(project_path)
            return [str(f) for f in path.rglob('*') if f.is_file()]
    
    def _filter_code_files(self, files: List[str]) -> List[str]:
        """Filter for supported code files."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.go', '.rs', '.cpp', '.c',
            '.cs', '.rb', '.php', '.swift', '.kt'
        }
        
        code_files = []
        for filepath in files:
            path = Path(filepath)
            # Skip common non-code directories
            if any(part in str(path) for part in [
                '__pycache__', 'node_modules', '.git',
                'venv', '.venv', 'dist', 'build'
            ]):
                continue
            
            if path.suffix.lower() in code_extensions:
                code_files.append(filepath)
        
        return code_files
    
    def _analyze_file_with_serena(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Analyze a single file using Serena MCP."""
        try:
            # Get or create fingerprint
            fingerprint = self._get_or_create_fingerprint(filepath)
            
            # Use Serena for symbol analysis
            symbols = self._get_symbols_via_serena(filepath)
            
            # Use Serena for relationship discovery
            references = self._get_references_via_serena(filepath)
            
            # Get file content snippet for semantic analysis
            snippet = self._get_content_snippet(filepath, 500)
            
            return {
                'path': filepath,
                'fingerprint': fingerprint,
                'symbols': symbols,
                'references': references,
                'snippet': snippet,
                'metadata': {
                    'size': Path(filepath).stat().st_size if Path(filepath).exists() else 0,
                    'modified': datetime.fromtimestamp(
                        Path(filepath).stat().st_mtime
                    ).isoformat() if Path(filepath).exists() else None
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing {filepath}: {e}")
            return None
    
    def _get_or_create_fingerprint(self, filepath: str) -> Dict[str, Any]:
        """Get existing fingerprint or create new one."""
        # Check cache first
        if filepath in self.fingerprint_cache:
            return self.fingerprint_cache[filepath]
        
        # Try to extract from file
        existing = self._extract_fingerprint_from_file(filepath)
        if existing:
            self.fingerprint_cache[filepath] = existing
            return existing
        
        # Create new fingerprint
        new_fingerprint = {
            'id': str(uuid.uuid4()),
            'birth': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'path': filepath,
            'language': self._detect_language(filepath),
            'intent': 'To be determined',
            'semantic_tags': [],
            'last_sync': datetime.utcnow().isoformat() + 'Z'
        }
        
        self.fingerprint_cache[filepath] = new_fingerprint
        return new_fingerprint
    
    def _extract_fingerprint_from_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract existing fingerprint from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # Read first 2000 chars
                
            # Look for fingerprint marker
            if '@cognimap:fingerprint' in content:
                import re
                pattern = r'@cognimap:fingerprint\n(.*?)@end:cognimap'
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    # Parse fingerprint data
                    fingerprint_text = match.group(1)
                    return self._parse_fingerprint_text(fingerprint_text)
        except:
            pass
        return None
    
    def _parse_fingerprint_text(self, text: str) -> Dict[str, Any]:
        """Parse fingerprint text into dictionary."""
        fingerprint = {}
        for line in text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Parse lists
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                
                fingerprint[key] = value
        return fingerprint
    
    def _get_symbols_via_serena(self, filepath: str) -> List[Dict[str, Any]]:
        """Get symbols using Serena MCP."""
        if self.serena:
            # Real Serena call
            return self.serena.get_symbols_overview(filepath)
        else:
            # Fallback - return empty for now
            return []
    
    def _get_references_via_serena(self, filepath: str) -> List[Dict[str, Any]]:
        """Get references using Serena MCP."""
        if self.serena:
            # Real Serena call
            return self.serena.find_referencing_symbols(filepath)
        else:
            # Fallback
            return []
    
    def _get_content_snippet(self, filepath: str, max_chars: int = 500) -> str:
        """Get content snippet for semantic analysis."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read(max_chars)
        except:
            return ""
    
    def _detect_language(self, filepath: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        suffix = Path(filepath).suffix.lower()
        return ext_map.get(suffix, 'unknown')
    
    def _discover_relationships(self, bulk_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover relationships between files."""
        relationships = []
        
        # Build a map of files for quick lookup
        file_map = {data['path']: data for data in bulk_data}
        
        for file_data in bulk_data:
            source = file_data['path']
            
            # Check references
            for ref in file_data.get('references', []):
                target = ref.get('file_path')
                if target and target in file_map:
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': 'references',
                        'symbol': ref.get('symbol_name')
                    })
            
            # Check imports (from symbols)
            for symbol in file_data.get('symbols', []):
                # This would need more sophisticated import detection
                pass
        
        return relationships
    
    def update_fingerprints(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update fingerprints for changed files."""
        updated = []
        
        for file_data in files:
            filepath = file_data['path']
            old_fingerprint = self._extract_fingerprint_from_file(filepath)
            new_fingerprint = file_data.get('fingerprint', {})
            
            # Merge old and new
            if old_fingerprint:
                new_fingerprint['id'] = old_fingerprint['id']  # Keep same ID
                new_fingerprint['birth'] = old_fingerprint['birth']  # Keep birth time
            
            new_fingerprint['last_sync'] = datetime.utcnow().isoformat() + 'Z'
            
            # Update cache
            self.fingerprint_cache[filepath] = new_fingerprint
            
            updated.append({
                'path': filepath,
                'fingerprint': new_fingerprint,
                'updated': True
            })
        
        return {
            'updated_count': len(updated),
            'files': updated
        }
    
    def get_changed_files(self, since: str = 'last_commit') -> List[str]:
        """Get list of changed files since a point in time."""
        # This would use git or filesystem timestamps
        # For now, return empty list
        return []
    
    def inject_fingerprints(self, files: List[Dict[str, Any]], force: bool = False) -> Dict[str, Any]:
        """
        Inject fingerprints into files.
        This is delegated to the fingerprint module to keep separation.
        """
        from ..core.fingerprint import FingerprintInjector, Fingerprint
        
        results = []
        for file_data in files:
            filepath = file_data['path']
            fingerprint_data = file_data['fingerprint']
            
            # Create fingerprint object
            fp = Fingerprint(filepath)
            fp.data = fingerprint_data
            
            # Inject
            success = FingerprintInjector.inject(filepath, fp, force=force)
            
            results.append({
                'path': filepath,
                'injected': success
            })
        
        return {
            'total': len(files),
            'succeeded': sum(1 for r in results if r['injected']),
            'results': results
        }


class SerenaMCPTool:
    """
    MCP Tool definitions for CogniMap when running in Serena MCP.
    These would be registered with the MCP server.
    """
    
    def __init__(self):
        self.collector = SerenaMCPCollector()
        
    def cognimap_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool: Analyze entire project.
        
        Parameters:
            path: Project root path
            mode: Analysis mode (full, incremental)
            include_tests: Include test files
            
        Returns:
            Bulk analysis data for semantic enrichment
        """
        project_path = params.get('path', '.')
        mode = params.get('mode', 'full')
        
        # Collect all data
        data = self.collector.collect_project_data(project_path, mode)
        
        # Return for semantic analysis by Claude
        return {
            'tool': 'cognimap_analyze',
            'status': 'success',
            'data': data
        }
    
    def cognimap_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool: Update changed files only.
        
        Parameters:
            since: Update files changed since (commit/timestamp)
            force: Force update even if unchanged
            
        Returns:
            Update results
        """
        since = params.get('since', 'last_commit')
        force = params.get('force', False)
        
        # Get changed files
        changed = self.collector.get_changed_files(since)
        
        # Analyze changed files
        bulk_data = []
        for filepath in changed:
            file_data = self.collector._analyze_file_with_serena(filepath)
            if file_data:
                bulk_data.append(file_data)
        
        # Update fingerprints
        result = self.collector.update_fingerprints(bulk_data)
        
        return {
            'tool': 'cognimap_update',
            'status': 'success',
            'data': result
        }
    
    def cognimap_inject(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool: Inject fingerprints into files.
        
        Parameters:
            files: List of files with fingerprint data
            force: Overwrite existing fingerprints
            
        Returns:
            Injection results
        """
        files = params.get('files', [])
        force = params.get('force', False)
        
        result = self.collector.inject_fingerprints(files, force)
        
        return {
            'tool': 'cognimap_inject',
            'status': 'success',
            'data': result
        }
    
    def cognimap_graph(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool: Build architecture graph.
        
        Parameters:
            format: Output format (json, graphml, dot)
            include_relationships: Relationship types to include
            
        Returns:
            Architecture graph
        """
        # This would build the complete graph
        # For now, return a placeholder
        return {
            'tool': 'cognimap_graph',
            'status': 'success',
            'data': {
                'nodes': [],
                'edges': [],
                'format': params.get('format', 'json')
            }
        }