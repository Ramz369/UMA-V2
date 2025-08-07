
"""
@cognimap:fingerprint
id: 8b309d52-c224-4b8f-a4a6-4a88aa934dba
birth: 2025-08-07T07:23:38.099218Z
parent: None
intent: CogniMap Code Scanner - Multi-language code analysis engine.
semantic_tags: [database, api, testing, utility, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.099909Z
hash: a2b64240
language: python
type: component
@end:cognimap
"""

"""
CogniMap Code Scanner - Multi-language code analysis engine.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import json


class MultiLanguageParser:
    """Universal parser for multiple programming languages."""
    
    def __init__(self):
        self.parsers = {
            'python': PythonParser(),
            'javascript': JavaScriptParser(),
            'typescript': JavaScriptParser(),  # Similar enough for basic parsing
            'java': JavaParser(),
            'go': GoParser(),
        }
    
    def parse(self, filepath: str, content: str = None) -> Dict[str, Any]:
        """Parse a file and extract structural information."""
        filepath = Path(filepath)
        
        # Detect language
        language = self._detect_language(filepath)
        
        # Read content if not provided
        if content is None:
            try:
                content = filepath.read_text(encoding='utf-8')
            except:
                return {}
        
        # Use appropriate parser
        parser = self.parsers.get(language, BaseParser())
        return parser.parse(content, filepath)
    
    def _detect_language(self, filepath: Path) -> str:
        """Detect language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
        }
        return ext_map.get(filepath.suffix.lower(), 'unknown')


class BaseParser:
    """Base parser with common functionality."""
    
    def parse(self, content: str, filepath: Path) -> Dict[str, Any]:
        """Parse content and extract structure."""
        return {
            'classes': self.find_classes(content),
            'functions': self.find_functions(content),
            'imports': self.find_imports(content),
            'exports': self.find_exports(content),
            'variables': self.find_variables(content),
            'api_calls': self.find_api_calls(content),
            'db_operations': self.find_db_operations(content),
            'file_operations': self.find_file_operations(content),
        }
    
    def find_classes(self, content: str) -> List[Dict[str, Any]]:
        """Find class definitions."""
        return []
    
    def find_functions(self, content: str) -> List[Dict[str, Any]]:
        """Find function definitions."""
        return []
    
    def find_imports(self, content: str) -> List[str]:
        """Find import statements."""
        return []
    
    def find_exports(self, content: str) -> List[str]:
        """Find export statements."""
        return []
    
    def find_variables(self, content: str) -> List[str]:
        """Find variable declarations."""
        return []
    
    def find_api_calls(self, content: str) -> List[Dict[str, str]]:
        """Find API/HTTP calls."""
        patterns = [
            r'fetch\(["\']([^"\']+)',
            r'axios\.\w+\(["\']([^"\']+)',
            r'requests\.\w+\(["\']([^"\']+)',
            r'http\.\w+\(["\']([^"\']+)',
            r'urllib\.request\.urlopen\(["\']([^"\']+)',
        ]
        
        calls = []
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                calls.append({
                    'type': 'http',
                    'url': match.group(1)
                })
        return calls
    
    def find_db_operations(self, content: str) -> List[Dict[str, str]]:
        """Find database operations."""
        patterns = [
            r'SELECT\s+.*?\s+FROM\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'UPDATE\s+(\w+)\s+SET',
            r'DELETE\s+FROM\s+(\w+)',
            r'CREATE\s+TABLE\s+(\w+)',
            r'DROP\s+TABLE\s+(\w+)',
        ]
        
        operations = []
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                operations.append({
                    'type': 'database',
                    'table': match.group(1)
                })
        return operations
    
    def find_file_operations(self, content: str) -> List[Dict[str, str]]:
        """Find file operations."""
        patterns = [
            r'open\(["\']([^"\']+)',
            r'readFile\(["\']([^"\']+)',
            r'writeFile\(["\']([^"\']+)',
            r'fs\.\w+\(["\']([^"\']+)',
            r'Path\(["\']([^"\']+)',
        ]
        
        operations = []
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                operations.append({
                    'type': 'file',
                    'path': match.group(1)
                })
        return operations


class PythonParser(BaseParser):
    """Python-specific parser using AST."""
    
    def parse(self, content: str, filepath: Path) -> Dict[str, Any]:
        """Parse Python code using AST."""
        try:
            tree = ast.parse(content)
            return {
                'classes': self._extract_classes(tree),
                'functions': self._extract_functions(tree),
                'imports': self._extract_imports(tree),
                'exports': self._extract_exports(tree),
                'variables': self._extract_variables(tree),
                'api_calls': self.find_api_calls(content),
                'db_operations': self.find_db_operations(content),
                'file_operations': self.find_file_operations(content),
            }
        except:
            # Fallback to regex-based parsing
            return super().parse(content, filepath)
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'args': [arg.arg for arg in item.args.args],
                            'decorators': [self._get_decorator_name(d) for d in item.decorator_list]
                        })
                
                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'bases': [self._get_name(base) for base in node.bases],
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                })
        return classes
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip methods (functions inside classes)
                parent = self._get_parent_node(tree, node)
                if not isinstance(parent, ast.ClassDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'async': isinstance(node, ast.AsyncFunctionDef)
                    })
        return functions
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)
        return imports
    
    def _extract_exports(self, tree: ast.AST) -> List[str]:
        """Extract exported names (from __all__)."""
        exports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            for item in node.value.elts:
                                if isinstance(item, ast.Constant):
                                    exports.append(item.value)
        return exports
    
    def _extract_variables(self, tree: ast.AST) -> List[str]:
        """Extract global variable names."""
        variables = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        return variables
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return 'unknown'
    
    def _get_decorator_name(self, node: ast.AST) -> str:
        """Get decorator name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return 'unknown'
    
    def _get_parent_node(self, tree: ast.AST, target: ast.AST) -> Optional[ast.AST]:
        """Get parent node of target in tree."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child == target:
                    return node
        return None


class JavaScriptParser(BaseParser):
    """JavaScript/TypeScript parser using regex."""
    
    def find_classes(self, content: str) -> List[Dict[str, Any]]:
        """Find class definitions."""
        classes = []
        pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(pattern, content):
            classes.append({
                'name': match.group(1),
                'extends': match.group(2) if match.group(2) else None,
                'methods': self._find_class_methods(content, match.group(1))
            })
        return classes
    
    def find_functions(self, content: str) -> List[Dict[str, Any]]:
        """Find function definitions."""
        functions = []
        patterns = [
            r'function\s+(\w+)\s*\((.*?)\)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\((.*?)\)\s*=>',
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                functions.append({
                    'name': match.group(1),
                    'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                    'async': 'async' in match.group(0)
                })
        return functions
    
    def find_imports(self, content: str) -> List[str]:
        """Find import statements."""
        imports = []
        patterns = [
            r'import\s+.*?\s+from\s+["\']([^"\']+)',
            r'import\s+["\']([^"\']+)',
            r'require\(["\']([^"\']+)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                imports.append(match.group(1))
        return imports
    
    def find_exports(self, content: str) -> List[str]:
        """Find export statements."""
        exports = []
        patterns = [
            r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)',
            r'export\s+\{([^}]+)\}',
            r'module\.exports\s*=\s*(\w+)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                if pattern == patterns[1]:  # Export list
                    exports.extend([e.strip() for e in match.group(1).split(',')])
                else:
                    exports.append(match.group(1))
        return exports
    
    def _find_class_methods(self, content: str, class_name: str) -> List[Dict[str, str]]:
        """Find methods within a class."""
        methods = []
        # Simplified method detection
        class_pattern = rf'class\s+{class_name}.*?\{{(.*?)\n\}}'
        class_match = re.search(class_pattern, content, re.DOTALL)
        
        if class_match:
            class_body = class_match.group(1)
            method_pattern = r'(?:async\s+)?(\w+)\s*\((.*?)\)'
            for match in re.finditer(method_pattern, class_body):
                if match.group(1) not in ['if', 'for', 'while', 'switch']:
                    methods.append({
                        'name': match.group(1),
                        'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
                    })
        return methods


class JavaParser(BaseParser):
    """Java parser using regex."""
    
    def find_classes(self, content: str) -> List[Dict[str, Any]]:
        """Find class definitions."""
        classes = []
        pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?'
        for match in re.finditer(pattern, content):
            classes.append({
                'name': match.group(1),
                'extends': match.group(2) if match.group(2) else None,
                'implements': [i.strip() for i in match.group(3).split(',')] if match.group(3) else []
            })
        return classes
    
    def find_functions(self, content: str) -> List[Dict[str, Any]]:
        """Find method definitions."""
        functions = []
        pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\((.*?)\)'
        for match in re.finditer(pattern, content):
            if match.group(1) not in ['if', 'for', 'while', 'switch', 'catch']:
                functions.append({
                    'name': match.group(1),
                    'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
                })
        return functions
    
    def find_imports(self, content: str) -> List[str]:
        """Find import statements."""
        imports = []
        pattern = r'import\s+([\w.]+(?:\.\*)?);'
        for match in re.finditer(pattern, content):
            imports.append(match.group(1))
        return imports


class GoParser(BaseParser):
    """Go parser using regex."""
    
    def find_functions(self, content: str) -> List[Dict[str, Any]]:
        """Find function definitions."""
        functions = []
        pattern = r'func\s+(?:\(.*?\)\s+)?(\w+)\s*\((.*?)\)'
        for match in re.finditer(pattern, content):
            functions.append({
                'name': match.group(1),
                'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
            })
        return functions
    
    def find_imports(self, content: str) -> List[str]:
        """Find import statements."""
        imports = []
        # Single import
        pattern = r'import\s+"([^"]+)"'
        for match in re.finditer(pattern, content):
            imports.append(match.group(1))
        
        # Multiple imports
        multi_pattern = r'import\s+\((.*?)\)'
        for match in re.finditer(multi_pattern, content, re.DOTALL):
            import_block = match.group(1)
            for line in import_block.split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    # Extract package name from quotes
                    pkg_match = re.search(r'"([^"]+)"', line)
                    if pkg_match:
                        imports.append(pkg_match.group(1))
        return imports


class CodeScanner:
    """High-level code scanner that coordinates parsing and analysis."""
    
    def __init__(self):
        self.parser = MultiLanguageParser()
        self.cache = {}
    
    def scan_file(self, filepath: str, use_cache: bool = True) -> Dict[str, Any]:
        """Scan a single file and extract all information."""
        filepath = Path(filepath)
        
        # Check cache
        if use_cache and str(filepath) in self.cache:
            return self.cache[str(filepath)]
        
        # Parse file
        result = self.parser.parse(filepath)
        
        # Add metadata
        result['filepath'] = str(filepath)
        result['filename'] = filepath.name
        result['directory'] = str(filepath.parent)
        result['size'] = filepath.stat().st_size if filepath.exists() else 0
        
        # Cache result
        if use_cache:
            self.cache[str(filepath)] = result
        
        return result
    
    def scan_directory(self, directory: str, pattern: str = "**/*", exclude: List[str] = None) -> List[Dict[str, Any]]:
        """Scan all files in a directory."""
        directory = Path(directory)
        exclude = exclude or ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        results = []
        
        for filepath in directory.glob(pattern):
            # Skip directories
            if filepath.is_dir():
                continue
            
            # Skip excluded paths
            if any(ex in str(filepath) for ex in exclude):
                continue
            
            # Skip binary files
            try:
                filepath.read_text(encoding='utf-8')
            except:
                continue
            
            # Scan file
            try:
                result = self.scan_file(filepath)
                results.append(result)
            except Exception as e:
                # Log error but continue
                print(f"Error scanning {filepath}: {e}")
        
        return results
    
    def find_dependencies(self, scan_result: Dict[str, Any]) -> List[str]:
        """Find all dependencies of a scanned file."""
        dependencies = []
        
        # Add imports as dependencies
        dependencies.extend(scan_result.get('imports', []))
        
        # Add API calls as external dependencies
        for api_call in scan_result.get('api_calls', []):
            dependencies.append(f"api:{api_call['url']}")
        
        # Add database dependencies
        for db_op in scan_result.get('db_operations', []):
            dependencies.append(f"db:{db_op['table']}")
        
        # Add file dependencies
        for file_op in scan_result.get('file_operations', []):
            dependencies.append(f"file:{file_op['path']}")
        
        return list(set(dependencies))  # Remove duplicates