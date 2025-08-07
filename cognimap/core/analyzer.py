"""
CogniMap Semantic Analyzer - AI-powered code understanding.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import json
from datetime import datetime
import hashlib


class SemanticAnalyzer:
    """Analyzes code semantically to understand purpose and relationships."""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm_provider = llm_provider  # For future LLM integration
        self.semantic_cache = {}
        
    def analyze_file(self, filepath: str, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic analysis on a file."""
        filepath = Path(filepath)
        
        analysis = {
            'purpose': self.extract_purpose(filepath, scan_result),
            'domain': self.identify_domain(scan_result),
            'patterns': self.detect_patterns(scan_result),
            'complexity': self.calculate_complexity(scan_result),
            'inputs': self.identify_inputs(scan_result),
            'outputs': self.identify_outputs(scan_result),
            'side_effects': self.detect_side_effects(scan_result),
            'semantic_tags': self.generate_semantic_tags(scan_result),
            'architectural_layer': self.identify_layer(filepath, scan_result),
            'quality_metrics': self.calculate_quality_metrics(scan_result),
        }
        
        return analysis
    
    def extract_purpose(self, filepath: Path, scan_result: Dict[str, Any]) -> str:
        """Extract the purpose of the file from various sources."""
        # Try to get from docstring/comments first
        content = filepath.read_text(encoding='utf-8') if filepath.exists() else ""
        
        # Python docstring
        docstring = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring:
            purpose = docstring.group(1).strip().split('\n')[0]
            if purpose:
                return purpose
        
        # JavaScript/TypeScript comment
        comment = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
        if comment:
            purpose = comment.group(1).strip().split('\n')[0]
            if purpose:
                return purpose.strip('* ')
        
        # Infer from class/function names
        if scan_result.get('classes'):
            main_class = scan_result['classes'][0]
            return f"Implements {main_class['name']} functionality"
        
        if scan_result.get('functions'):
            if len(scan_result['functions']) == 1:
                return f"Provides {scan_result['functions'][0]['name']} functionality"
            else:
                return f"Provides {len(scan_result['functions'])} functions for various operations"
        
        # Infer from filename
        filename = filepath.stem
        if 'test' in filename.lower():
            return f"Tests for {filename.replace('test_', '').replace('_test', '')}"
        elif 'config' in filename.lower():
            return "Configuration settings"
        elif 'model' in filename.lower():
            return "Data model definitions"
        elif 'service' in filename.lower():
            return "Service layer implementation"
        elif 'controller' in filename.lower():
            return "Controller for handling requests"
        elif 'util' in filename.lower() or 'helper' in filename.lower():
            return "Utility functions and helpers"
        
        return "Purpose to be determined through analysis"
    
    def identify_domain(self, scan_result: Dict[str, Any]) -> str:
        """Identify the domain/area of the code."""
        domains = {
            'authentication': ['auth', 'login', 'password', 'token', 'session', 'credential'],
            'database': ['database', 'db', 'sql', 'query', 'orm', 'model', 'schema'],
            'api': ['api', 'endpoint', 'route', 'rest', 'graphql', 'http'],
            'frontend': ['render', 'component', 'view', 'ui', 'dom', 'react', 'vue'],
            'backend': ['server', 'service', 'handler', 'controller', 'middleware'],
            'testing': ['test', 'spec', 'mock', 'fixture', 'assert', 'expect'],
            'infrastructure': ['docker', 'kubernetes', 'deploy', 'ci', 'cd', 'pipeline'],
            'data_processing': ['transform', 'process', 'pipeline', 'etl', 'stream'],
            'machine_learning': ['model', 'train', 'predict', 'neural', 'ml', 'ai'],
            'security': ['encrypt', 'decrypt', 'hash', 'secure', 'vulnerability'],
        }
        
        # Check all text in the scan result
        all_text = json.dumps(scan_result).lower()
        
        scores = {}
        for domain, keywords in domains.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                scores[domain] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'general'
    
    def detect_patterns(self, scan_result: Dict[str, Any]) -> List[str]:
        """Detect design patterns and architectural patterns."""
        patterns = []
        
        # Check for common patterns
        class_names = [c['name'].lower() for c in scan_result.get('classes', [])]
        function_names = [f['name'].lower() for f in scan_result.get('functions', [])]
        
        # Singleton pattern
        if any('singleton' in name or 'instance' in name for name in class_names + function_names):
            patterns.append('singleton')
        
        # Factory pattern
        if any('factory' in name or 'create' in name for name in class_names + function_names):
            patterns.append('factory')
        
        # Observer pattern
        if any('observer' in name or 'listener' in name or 'subscribe' in name for name in class_names + function_names):
            patterns.append('observer')
        
        # MVC pattern
        if any('controller' in name for name in class_names):
            patterns.append('mvc-controller')
        elif any('model' in name for name in class_names):
            patterns.append('mvc-model')
        elif any('view' in name for name in class_names):
            patterns.append('mvc-view')
        
        # Repository pattern
        if any('repository' in name for name in class_names):
            patterns.append('repository')
        
        # Service pattern
        if any('service' in name for name in class_names):
            patterns.append('service')
        
        # Middleware pattern
        if any('middleware' in name for name in class_names + function_names):
            patterns.append('middleware')
        
        return patterns
    
    def calculate_complexity(self, scan_result: Dict[str, Any]) -> Dict[str, int]:
        """Calculate various complexity metrics."""
        return {
            'classes': len(scan_result.get('classes', [])),
            'functions': len(scan_result.get('functions', [])),
            'imports': len(scan_result.get('imports', [])),
            'cyclomatic': self._estimate_cyclomatic_complexity(scan_result),
            'dependencies': len(scan_result.get('imports', [])) + 
                          len(scan_result.get('api_calls', [])) + 
                          len(scan_result.get('db_operations', [])),
            'depth': self._calculate_nesting_depth(scan_result),
        }
    
    def _estimate_cyclomatic_complexity(self, scan_result: Dict[str, Any]) -> int:
        """Estimate cyclomatic complexity based on structure."""
        # Simple estimation based on number of functions and their characteristics
        complexity = 1  # Base complexity
        
        for func in scan_result.get('functions', []):
            complexity += 1  # Each function adds complexity
            # Add complexity for parameters (decision points)
            complexity += len(func.get('args', [])) // 3
        
        for cls in scan_result.get('classes', []):
            complexity += len(cls.get('methods', []))
        
        return complexity
    
    def _calculate_nesting_depth(self, scan_result: Dict[str, Any]) -> int:
        """Calculate maximum nesting depth."""
        # Estimate based on class hierarchy
        max_depth = 0
        
        for cls in scan_result.get('classes', []):
            depth = 1
            if cls.get('extends') or cls.get('bases'):
                depth += 1  # Inheritance adds depth
            if cls.get('methods'):
                depth += 1  # Methods add depth
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def identify_inputs(self, scan_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify what inputs the code accepts."""
        inputs = []
        
        # Function parameters
        for func in scan_result.get('functions', []):
            for arg in func.get('args', []):
                inputs.append({
                    'type': 'parameter',
                    'name': arg,
                    'source': func['name']
                })
        
        # API endpoints (they receive requests)
        if 'api' in json.dumps(scan_result).lower():
            inputs.append({
                'type': 'http_request',
                'name': 'HTTP Request',
                'source': 'network'
            })
        
        # File operations (reading)
        for file_op in scan_result.get('file_operations', []):
            if 'read' in str(file_op).lower():
                inputs.append({
                    'type': 'file',
                    'name': file_op.get('path', 'file'),
                    'source': 'filesystem'
                })
        
        # Database queries (reading)
        for db_op in scan_result.get('db_operations', []):
            if 'select' in str(db_op).lower():
                inputs.append({
                    'type': 'database',
                    'name': db_op.get('table', 'table'),
                    'source': 'database'
                })
        
        return inputs
    
    def identify_outputs(self, scan_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify what outputs the code produces."""
        outputs = []
        
        # Return values (generic)
        for func in scan_result.get('functions', []):
            outputs.append({
                'type': 'return_value',
                'name': f"{func['name']} result",
                'destination': 'caller'
            })
        
        # API calls (they send data)
        for api_call in scan_result.get('api_calls', []):
            outputs.append({
                'type': 'http_request',
                'name': api_call.get('url', 'API'),
                'destination': 'external_api'
            })
        
        # File operations (writing)
        for file_op in scan_result.get('file_operations', []):
            if 'write' in str(file_op).lower():
                outputs.append({
                    'type': 'file',
                    'name': file_op.get('path', 'file'),
                    'destination': 'filesystem'
                })
        
        # Database operations (writing)
        for db_op in scan_result.get('db_operations', []):
            if any(op in str(db_op).lower() for op in ['insert', 'update', 'delete']):
                outputs.append({
                    'type': 'database',
                    'name': db_op.get('table', 'table'),
                    'destination': 'database'
                })
        
        return outputs
    
    def detect_side_effects(self, scan_result: Dict[str, Any]) -> List[str]:
        """Detect potential side effects."""
        side_effects = []
        
        # File operations
        if scan_result.get('file_operations'):
            side_effects.append('file_system_modification')
        
        # Database operations
        db_ops = scan_result.get('db_operations', [])
        if any('insert' in str(op).lower() or 'update' in str(op).lower() or 'delete' in str(op).lower() for op in db_ops):
            side_effects.append('database_modification')
        
        # API calls
        if scan_result.get('api_calls'):
            side_effects.append('network_calls')
        
        # Global state (heuristic)
        if 'global' in json.dumps(scan_result).lower() or 'state' in json.dumps(scan_result).lower():
            side_effects.append('global_state_modification')
        
        return side_effects
    
    def generate_semantic_tags(self, scan_result: Dict[str, Any]) -> List[str]:
        """Generate semantic tags for categorization."""
        tags = []
        
        # Add domain as tag
        domain = self.identify_domain(scan_result)
        if domain != 'general':
            tags.append(domain)
        
        # Add patterns as tags
        tags.extend(self.detect_patterns(scan_result))
        
        # Add based on file operations
        if scan_result.get('api_calls'):
            tags.append('network')
        if scan_result.get('db_operations'):
            tags.append('database')
        if scan_result.get('file_operations'):
            tags.append('filesystem')
        
        # Add based on structure
        if scan_result.get('classes'):
            tags.append('object-oriented')
        if any(f.get('async') for f in scan_result.get('functions', [])):
            tags.append('asynchronous')
        
        # Add based on testing
        if 'test' in str(scan_result.get('filepath', '')).lower():
            tags.append('testing')
        
        return list(set(tags))  # Remove duplicates
    
    def identify_layer(self, filepath: Path, scan_result: Dict[str, Any]) -> str:
        """Identify architectural layer."""
        path_str = str(filepath).lower()
        
        # Check path patterns
        if 'controller' in path_str or 'handler' in path_str or 'route' in path_str:
            return 'presentation'
        elif 'service' in path_str or 'business' in path_str or 'logic' in path_str:
            return 'business'
        elif 'model' in path_str or 'entity' in path_str or 'schema' in path_str:
            return 'data'
        elif 'repository' in path_str or 'dao' in path_str or 'database' in path_str:
            return 'persistence'
        elif 'util' in path_str or 'helper' in path_str or 'common' in path_str:
            return 'utility'
        elif 'test' in path_str:
            return 'testing'
        elif 'config' in path_str:
            return 'configuration'
        
        # Check class/function names
        domain = self.identify_domain(scan_result)
        if domain == 'api':
            return 'presentation'
        elif domain == 'database':
            return 'persistence'
        elif domain == 'frontend':
            return 'presentation'
        elif domain == 'backend':
            return 'business'
        
        return 'unknown'
    
    def calculate_quality_metrics(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate code quality metrics."""
        complexity = self.calculate_complexity(scan_result)
        
        # Calculate scores (0-100)
        maintainability = max(0, 100 - complexity['cyclomatic'] * 5 - complexity['dependencies'] * 2)
        modularity = min(100, 100 - complexity['classes'] * 10 if complexity['classes'] > 0 else 50)
        testability = 100 if 'test' in str(scan_result.get('filepath', '')).lower() else max(0, 100 - complexity['cyclomatic'] * 3)
        
        return {
            'maintainability': maintainability,
            'modularity': modularity,
            'testability': testability,
            'overall': (maintainability + modularity + testability) // 3
        }


class IntentExtractor:
    """Extracts and analyzes intent from code and context."""
    
    def __init__(self):
        self.intent_patterns = {
            'create': ['create', 'new', 'init', 'setup', 'build', 'generate'],
            'read': ['get', 'fetch', 'read', 'load', 'retrieve', 'find', 'search'],
            'update': ['update', 'modify', 'change', 'edit', 'patch', 'alter'],
            'delete': ['delete', 'remove', 'destroy', 'clean', 'purge', 'clear'],
            'process': ['process', 'handle', 'execute', 'run', 'perform', 'compute'],
            'validate': ['validate', 'check', 'verify', 'ensure', 'assert', 'test'],
            'transform': ['transform', 'convert', 'map', 'translate', 'parse', 'format'],
            'communicate': ['send', 'receive', 'publish', 'subscribe', 'emit', 'broadcast'],
        }
    
    def extract_intent(self, scan_result: Dict[str, Any], semantic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract intent from code structure and semantics."""
        # Get all text to analyze
        all_names = []
        all_names.extend([c['name'] for c in scan_result.get('classes', [])])
        all_names.extend([f['name'] for f in scan_result.get('functions', [])])
        all_names.extend([m['name'] for c in scan_result.get('classes', []) for m in c.get('methods', [])])
        
        # Analyze intent patterns
        detected_intents = []
        for intent, keywords in self.intent_patterns.items():
            for name in all_names:
                name_lower = name.lower()
                if any(keyword in name_lower for keyword in keywords):
                    detected_intents.append({
                        'type': intent,
                        'source': name,
                        'confidence': 0.8
                    })
        
        # Primary intent (most common)
        if detected_intents:
            intent_types = [i['type'] for i in detected_intents]
            primary_intent = max(set(intent_types), key=intent_types.count)
        else:
            primary_intent = 'process'  # Default
        
        return {
            'primary': primary_intent,
            'secondary': list(set(i['type'] for i in detected_intents if i['type'] != primary_intent)),
            'detected_patterns': detected_intents,
            'purpose': semantic_analysis.get('purpose', 'Unknown'),
            'confidence': len(detected_intents) / max(len(all_names), 1) if all_names else 0
        }
    
    def analyze_intent_fulfillment(self, intent: Dict[str, Any], scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well the code fulfills its intent."""
        issues = []
        suggestions = []
        score = 100
        
        primary_intent = intent.get('primary', 'unknown')
        
        # Check if structure matches intent
        if primary_intent == 'create' and not any('create' in f['name'].lower() or 'new' in f['name'].lower() or 'init' in f['name'].lower() for f in scan_result.get('functions', [])):
            issues.append("Intent is 'create' but no creation functions found")
            suggestions.append("Add explicit creation methods")
            score -= 20
        
        if primary_intent == 'validate' and not any('validate' in f['name'].lower() or 'check' in f['name'].lower() or 'verify' in f['name'].lower() for f in scan_result.get('functions', [])):
            issues.append("Intent is 'validate' but no validation functions found")
            suggestions.append("Add validation methods")
            score -= 20
        
        # Check complexity vs intent
        complexity = len(scan_result.get('functions', [])) + len(scan_result.get('classes', []))
        if primary_intent in ['read', 'get'] and complexity > 10:
            issues.append("Simple read intent but complex implementation")
            suggestions.append("Consider simplifying the code")
            score -= 15
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'alignment': 'good' if score >= 80 else 'moderate' if score >= 60 else 'poor'
        }