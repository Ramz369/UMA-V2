"""
CogniMap Fingerprint System - Unique semantic identity for every file.
"""

import uuid
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib

logger = logging.getLogger(__name__)


class Fingerprint:
    """Represents a unique semantic fingerprint for a code file."""
    
    def __init__(self, filepath: str, content: str = None):
        self.filepath = Path(filepath)
        self.content = content or self._read_file()
        self.data = self._extract_existing() or self._generate_new()
        
    def _read_file(self) -> str:
        """Read file content."""
        try:
            return self.filepath.read_text(encoding='utf-8')
        except:
            return ""
    
    def _extract_existing(self) -> Optional[Dict[str, Any]]:
        """Extract existing fingerprint from file."""
        patterns = [
            r'@cognimap:fingerprint\n(.*?)@end:cognimap',  # Python/JS comment
            r'/\*\s*@cognimap:fingerprint\n(.*?)@end:cognimap\s*\*/',  # C-style
            r'#\s*@cognimap:fingerprint\n(.*?)#\s*@end:cognimap',  # Shell/YAML
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.content, re.DOTALL)
            if match:
                try:
                    # Parse YAML-like format
                    fingerprint_text = match.group(1)
                    return self._parse_fingerprint_text(fingerprint_text)
                except:
                    continue
        return None
    
    def _parse_fingerprint_text(self, text: str) -> Dict[str, Any]:
        """Parse fingerprint text into dictionary."""
        data = {}
        for line in text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Parse different value types
                if value.startswith('[') and value.endswith(']'):
                    # List
                    value = [v.strip() for v in value[1:-1].split(',')]
                elif value in ('true', 'false'):
                    # Boolean
                    value = value == 'true'
                elif value.replace('.', '').replace('-', '').isdigit():
                    # Number or date
                    pass
                
                data[key] = value
        return data
    
    def _generate_new(self) -> Dict[str, Any]:
        """Generate a new fingerprint for the file."""
        file_hash = hashlib.sha256(self.content.encode()).hexdigest()[:8]
        
        return {
            'id': str(uuid.uuid4()),
            'birth': datetime.utcnow().isoformat() + 'Z',
            'parent': self._detect_parent(),
            'intent': self._extract_intent(),
            'semantic_tags': self._generate_tags(),
            'version': '1.0.0',
            'last_sync': datetime.utcnow().isoformat() + 'Z',
            'hash': file_hash,
            'language': self._detect_language(),
            'type': self._detect_component_type()
        }
    
    def _detect_parent(self) -> Optional[str]:
        """Detect parent component that created this file."""
        # Check git blame for creator
        # For now, return None
        return None
    
    def _extract_intent(self) -> str:
        """Extract intent from docstring or comments."""
        # Python docstring
        docstring_match = re.search(r'"""(.*?)"""', self.content, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1).strip().split('\n')[0]
        
        # JavaScript/TypeScript comment
        comment_match = re.search(r'/\*\*(.*?)\*/', self.content, re.DOTALL)
        if comment_match:
            return comment_match.group(1).strip().split('\n')[0]
        
        # Single line comment at top
        first_comment = re.search(r'^[#/]+\s*(.+)$', self.content, re.MULTILINE)
        if first_comment:
            return first_comment.group(1).strip()
        
        return "Purpose to be determined"
    
    def _generate_tags(self) -> List[str]:
        """Generate semantic tags based on content."""
        tags = []
        
        # Common patterns and their tags
        patterns = {
            'authentication': r'(auth|login|password|token|credential)',
            'database': r'(database|db|sql|query|table|postgres|mysql)',
            'api': r'(api|endpoint|route|rest|graphql)',
            'testing': r'(test|spec|mock|fixture|assert)',
            'ui': r'(render|component|view|template|html|css)',
            'service': r'(service|handler|manager|controller)',
            'model': r'(model|schema|entity|dto)',
            'utility': r'(util|helper|common|shared)',
            'configuration': r'(config|settings|env|options)',
            'security': r'(security|encrypt|decrypt|hash|salt)',
        }
        
        content_lower = self.content.lower()
        for tag, pattern in patterns.items():
            if re.search(pattern, content_lower):
                tags.append(tag)
        
        return tags
    
    def _detect_language(self) -> str:
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
            '.kt': 'kotlin',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
        }
        
        suffix = self.filepath.suffix.lower()
        return ext_map.get(suffix, 'unknown')
    
    def _detect_component_type(self) -> str:
        """Detect the type of component (agent, tool, service, etc.)."""
        name = self.filepath.stem.lower()
        path_str = str(self.filepath).lower()
        
        # Check path patterns
        if 'agent' in path_str:
            return 'agent'
        elif 'tool' in path_str:
            return 'tool'
        elif 'service' in path_str:
            return 'service'
        elif 'model' in path_str:
            return 'model'
        elif 'test' in path_str:
            return 'test'
        elif 'config' in path_str:
            return 'configuration'
        elif 'protocol' in path_str:
            return 'protocol'
        
        # Check class names in content
        if re.search(r'class \w*Agent', self.content):
            return 'agent'
        elif re.search(r'class \w*Tool', self.content):
            return 'tool'
        elif re.search(r'class \w*Service', self.content):
            return 'service'
        elif re.search(r'class \w*Model', self.content):
            return 'model'
        
        return 'component'
    
    def to_text(self) -> str:
        """Convert fingerprint to text format for injection."""
        lines = []
        for key, value in self.data.items():
            if isinstance(value, list):
                value = '[' + ', '.join(str(v) for v in value) + ']'
            elif isinstance(value, bool):
                value = 'true' if value else 'false'
            lines.append(f"{key}: {value}")
        return '\n'.join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get fingerprint as dictionary."""
        return self.data.copy()


class FingerprintCleaner:
    """Handles removal of fingerprints from files."""
    
    @staticmethod
    def clean(filepath: str) -> bool:
        """Remove fingerprint from a file."""
        try:
            filepath = Path(filepath)
            content = filepath.read_text(encoding='utf-8')
            
            # Check if file has fingerprint
            if '@cognimap:fingerprint' not in content:
                return True  # Already clean
            
            # Find and remove fingerprint block
            lines = content.split('\n')
            cleaned_lines = []
            in_fingerprint = False
            skip_next_empty = False
            
            for i, line in enumerate(lines):
                if '@cognimap:fingerprint' in line:
                    in_fingerprint = True
                    # Also remove the opening comment marker (previous line)
                    if cleaned_lines and (cleaned_lines[-1].strip() in ('"""', '/*', '<!--', '#')):
                        cleaned_lines.pop()
                    continue
                elif '@end:cognimap' in line:
                    in_fingerprint = False
                    skip_next_empty = True
                    # Skip the closing comment marker on next line
                    continue
                elif in_fingerprint:
                    continue
                elif skip_next_empty:
                    # Skip closing comment markers and empty lines after fingerprint
                    if line.strip() in ('"""', '*/', '-->', '') or (line.strip() == '' and i < len(lines) - 1):
                        skip_next_empty = False
                        continue
                    else:
                        skip_next_empty = False
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            # Remove extra empty lines at the beginning
            while cleaned_lines and cleaned_lines[0].strip() == '':
                cleaned_lines.pop(0)
            
            # Write cleaned content
            cleaned_content = '\n'.join(cleaned_lines)
            filepath.write_text(cleaned_content, encoding='utf-8')
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean fingerprint from {filepath}: {e}")
            return False


class FingerprintInjector:
    """Injects fingerprints into code files."""
    
    @staticmethod
    def inject(filepath: str, fingerprint: Fingerprint, force: bool = False) -> bool:
        """Inject fingerprint into file."""
        filepath = Path(filepath)
        
        # Check if file already has fingerprint
        content = filepath.read_text(encoding='utf-8')
        if '@cognimap:fingerprint' in content and not force:
            return False
        
        # Determine comment style based on language
        language = fingerprint.data.get('language', 'unknown')
        fingerprint_text = fingerprint.to_text()
        
        # Format fingerprint based on language
        if language in ('python', 'ruby', 'perl'):
            formatted = f'"""\n@cognimap:fingerprint\n{fingerprint_text}\n@end:cognimap\n"""\n\n'
        elif language in ('javascript', 'typescript', 'java', 'c', 'cpp', 'csharp', 'go', 'rust'):
            formatted = f'/*\n@cognimap:fingerprint\n{fingerprint_text}\n@end:cognimap\n*/\n\n'
        elif language in ('yaml', 'shell', 'bash'):
            formatted = '\n'.join(f'# {line}' for line in [
                '@cognimap:fingerprint',
                *fingerprint_text.split('\n'),
                '@end:cognimap'
            ]) + '\n\n'
        elif language in ('html', 'xml'):
            formatted = f'<!--\n@cognimap:fingerprint\n{fingerprint_text}\n@end:cognimap\n-->\n\n'
        else:
            # Default to hash comment
            formatted = '\n'.join(f'# {line}' for line in [
                '@cognimap:fingerprint',
                *fingerprint_text.split('\n'),
                '@end:cognimap'
            ]) + '\n\n'
        
        # Remove old fingerprint if force update
        if force and '@cognimap:fingerprint' in content:
            content = re.sub(
                r'(.*?@cognimap:fingerprint.*?@end:cognimap.*?\n\n)',
                '',
                content,
                flags=re.DOTALL
            )
        
        # Inject at the top of file (after shebang if present)
        lines = content.split('\n')
        insert_pos = 0
        
        # Skip shebang
        if lines and lines[0].startswith('#!'):
            insert_pos = 1
        
        # Skip encoding declarations
        if insert_pos < len(lines) and 'coding' in lines[insert_pos]:
            insert_pos += 1
        
        # Insert fingerprint
        new_content = '\n'.join(lines[:insert_pos]) + '\n' + formatted + '\n'.join(lines[insert_pos:])
        
        # Write back to file
        filepath.write_text(new_content, encoding='utf-8')
        return True
    
    @staticmethod
    def update(filepath: str) -> bool:
        """Update existing fingerprint with fresh data."""
        fingerprint = Fingerprint(filepath)
        return FingerprintInjector.inject(filepath, fingerprint, force=True)
    
    @staticmethod
    def batch_inject(directory: str, pattern: str = "**/*", exclude: List[str] = None) -> Dict[str, bool]:
        """Inject fingerprints into multiple files."""
        directory = Path(directory)
        exclude = exclude or ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        results = {}
        
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
            
            # Generate and inject fingerprint
            try:
                fingerprint = Fingerprint(filepath)
                success = FingerprintInjector.inject(filepath, fingerprint)
                results[str(filepath)] = success
            except Exception as e:
                results[str(filepath)] = False
        
        return results