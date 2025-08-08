import os
import re
import json
from pathlib import Path

from .pattern_detector import detect_patterns
from .gap_finder import find_gaps
from .deepseek_integration import request_improvements


class SemanticAnalyzer:
    """Builds a symbol graph and performs semantic analysis using a
    simplified Serena MCP style approach.

    The analyzer avoids reading full files where possible.  Instead it uses
    lightweight regex based extraction to discover symbols and then scans the
    project for references to those symbols.  The resulting relationships and
    fingerprints are persisted so later agents can build on this knowledge.
    """

    SYMBOL_REGEX = re.compile(r"^(class|def)\s+(?P<name>\w+)")

    def __init__(self, root_path: str, memory_path: str = "reports/cognimap/semantic"):
        self.root_path = Path(root_path)
        self.memory_path = Path(memory_path)
        self.symbols = {}
        self.connections = {}
        self.fingerprints = {}

        self.memory_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Symbol discovery
    # ------------------------------------------------------------------
    def scan_symbols(self):
        """Scan the repository for top level class and function symbols."""
        # Skip common directories that shouldn't be scanned
        skip_dirs = {'node_modules', '__pycache__', '.git', '.venv', 'venv', 'dist', 'build'}
        
        for path in self.root_path.rglob("*.py"):
            # Skip if path contains any of the skip directories
            if any(skip_dir in path.parts for skip_dir in skip_dirs):
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    match = self.SYMBOL_REGEX.match(line)
                    if match:
                        name = match.group("name")
                        sym_type = match.group(1)
                        symbol_id = f"{path}:{name}"
                        self.symbols[symbol_id] = {
                            "name": name,
                            "type": sym_type,
                            "file": str(path),
                            "references": []
                        }

    # ------------------------------------------------------------------
    # Reference mapping
    # ------------------------------------------------------------------
    def map_references(self):
        """For each discovered symbol find referencing files."""
        file_cache = {}
        for symbol in self.symbols.values():
            pattern = re.compile(r"\b" + re.escape(symbol["name"]) + r"\b")
            for path in self.root_path.rglob("*.py"):
                # lazily read files to avoid repeated IO
                if path not in file_cache:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        file_cache[path] = fh.read()
                if pattern.search(file_cache[path]):
                    symbol["references"].append(str(path))
                    self.connections.setdefault(symbol["file"], {"outgoing": set(), "incoming": set()})
                    self.connections.setdefault(str(path), {"outgoing": set(), "incoming": set()})
                    self.connections[symbol["file"]]["outgoing"].add(str(path))
                    self.connections[str(path)]["incoming"].add(symbol["file"])

    # ------------------------------------------------------------------
    # Semantic fingerprinting and gaps
    # ------------------------------------------------------------------
    def build_fingerprints(self):
        for symbol_id, data in self.symbols.items():
            name = data["name"].lower()
            tags = []
            for token in ["user", "auth", "payment", "repo", "controller"]:
                if token in name:
                    tags.append(token)
            self.fingerprints[symbol_id] = {
                "tags": tags,
                "pattern": detect_patterns(data["name"])
            }

    def analyze_gaps(self):
        return find_gaps(self.symbols, self.connections, self.fingerprints)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save_reports(self, gaps):
        symbol_graph = {
            sid: {"name": data["name"], "type": data["type"], "file": data["file"],
                  "references": data["references"]}
            for sid, data in self.symbols.items()
        }
        with open(self.memory_path / "symbol_graph.json", "w", encoding="utf-8") as fh:
            json.dump(symbol_graph, fh, indent=2)

        with open(self.memory_path / "semantic_gaps.json", "w", encoding="utf-8") as fh:
            json.dump(gaps, fh, indent=2)

        pattern_info = {sid: fp["pattern"] for sid, fp in self.fingerprints.items()}
        with open(self.memory_path / "pattern_analysis.json", "w", encoding="utf-8") as fh:
            json.dump(pattern_info, fh, indent=2)

        with open(self.memory_path / "improvement_roadmap.md", "w", encoding="utf-8") as fh:
            fh.write("# Improvement Roadmap\n\n")
            fh.write("Generated suggestions will appear here.\n")

        # Memory files for later agents
        memories = {
            "architectural_patterns.json": pattern_info,
            "semantic_connections.json": {
                k: {"incoming": list(v["incoming"]), "outgoing": list(v["outgoing"])}
                for k, v in self.connections.items()
            },
            "gap_analysis.json": gaps,
            "improvement_suggestions.json": []
        }
        for filename, content in memories.items():
            with open(self.memory_path / filename, "w", encoding="utf-8") as fh:
                json.dump(content, fh, indent=2)

    # ------------------------------------------------------------------
    def run(self):
        self.scan_symbols()
        self.map_references()
        self.build_fingerprints()
        gaps = self.analyze_gaps()
        self.save_reports(gaps)
        request_improvements(self.memory_path / "symbol_graph.json")
        return gaps


if __name__ == "__main__":
    analyzer = SemanticAnalyzer(root_path=".")
    analyzer.run()
