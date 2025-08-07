#!/usr/bin/env python3
"""
CogniMap CLI - Command-line interface for architecture visualization.
"""

import click
import yaml
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging
from typing import Optional

from cognimap.core import Fingerprint, FingerprintInjector, CodeScanner, SemanticAnalyzer
from cognimap.collectors import SerenaMCPCollector

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """CogniMap - Living Architecture Visualization System"""
    pass


@cli.command()
@click.option('--path', '-p', default='.', help='Project root path')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--mode', '-m', type=click.Choice(['full', 'incremental']), default='full', help='Analysis mode')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def init(path: str, config: Optional[str], mode: str, verbose: bool):
    """Initialize CogniMap for a project."""
    
    console.print(f"[bold blue]🧠 Initializing CogniMap[/bold blue]")
    console.print(f"Project path: {Path(path).absolute()}")
    
    # Load configuration
    config_data = _load_config(config)
    
    # Create CogniMap directory
    cognimap_dir = Path(path) / '.cognimap'
    cognimap_dir.mkdir(exist_ok=True)
    
    # Initialize collector
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Discover files
        task1 = progress.add_task("Discovering files...", total=None)
        scanner = CodeScanner()
        files = list(Path(path).rglob('*'))
        code_files = [f for f in files if f.is_file() and _is_code_file(f)]
        progress.update(task1, completed=True)
        console.print(f"✅ Found {len(code_files)} code files")
        
        # Step 2: Generate fingerprints
        task2 = progress.add_task("Generating fingerprints...", total=len(code_files))
        fingerprints = {}
        for filepath in code_files:
            fp = Fingerprint(str(filepath))
            fingerprints[str(filepath)] = fp
            progress.update(task2, advance=1)
        console.print(f"✅ Generated {len(fingerprints)} fingerprints")
        
        # Step 3: Inject fingerprints
        if config_data.get('fingerprint', {}).get('inject_on_init', True):
            task3 = progress.add_task("Injecting fingerprints...", total=len(code_files))
            injected = 0
            for filepath, fp in fingerprints.items():
                if FingerprintInjector.inject(filepath, fp):
                    injected += 1
                progress.update(task3, advance=1)
            console.print(f"✅ Injected {injected} fingerprints")
        
        # Step 4: Analyze semantically
        task4 = progress.add_task("Analyzing code...", total=len(code_files))
        analyzer = SemanticAnalyzer()
        analyses = {}
        for filepath in code_files:
            scan_result = scanner.scan_file(str(filepath))
            analysis = analyzer.analyze_file(str(filepath), scan_result)
            analyses[str(filepath)] = analysis
            progress.update(task4, advance=1)
        console.print(f"✅ Analyzed {len(analyses)} files")
    
    # Save initial state
    state = {
        'project_path': str(Path(path).absolute()),
        'files_count': len(code_files),
        'fingerprints_count': len(fingerprints),
        'mode': mode,
        'initialized_at': Path(cognimap_dir / 'state.json').stat().st_mtime if (cognimap_dir / 'state.json').exists() else None
    }
    
    with open(cognimap_dir / 'state.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    console.print("[bold green]✨ CogniMap initialized successfully![/bold green]")
    console.print(f"Run [bold]cognimap serve[/bold] to start the visualization server")


@cli.command()
@click.option('--path', '-p', default='.', help='Project root path')
@click.option('--since', '-s', default='last_commit', help='Update files changed since')
@click.option('--force', '-f', is_flag=True, help='Force update all files')
def update(path: str, since: str, force: bool):
    """Update fingerprints for changed files."""
    
    console.print(f"[bold blue]🔄 Updating CogniMap[/bold blue]")
    
    # Check if initialized
    cognimap_dir = Path(path) / '.cognimap'
    if not cognimap_dir.exists():
        console.print("[red]❌ CogniMap not initialized. Run 'cognimap init' first.[/red]")
        return
    
    # Get changed files (simplified for now)
    if force:
        console.print("Force updating all files...")
        code_files = [f for f in Path(path).rglob('*') if f.is_file() and _is_code_file(f)]
    else:
        # This would use git to find changed files
        console.print(f"Finding files changed since {since}...")
        code_files = []  # Would be populated by git diff
    
    if not code_files:
        console.print("[yellow]No files to update[/yellow]")
        return
    
    # Update fingerprints
    updated = 0
    for filepath in code_files:
        if FingerprintInjector.update(str(filepath)):
            updated += 1
    
    console.print(f"✅ Updated {updated} fingerprints")


@cli.command()
@click.option('--path', '-p', default='.', help='Project root path')
@click.option('--port', default=8080, help='Server port')
@click.option('--host', default='localhost', help='Server host')
@click.option('--no-browser', is_flag=True, help="Don't open browser automatically")
def serve(path: str, port: int, host: str, no_browser: bool):
    """Start the visualization server."""
    
    console.print(f"[bold blue]🌐 Starting CogniMap visualization server[/bold blue]")
    console.print(f"URL: http://{host}:{port}")
    
    # Check if initialized
    cognimap_dir = Path(path) / '.cognimap'
    if not cognimap_dir.exists():
        console.print("[red]❌ CogniMap not initialized. Run 'cognimap init' first.[/red]")
        return
    
    # Start server (simplified - would start FastAPI server)
    console.print("[yellow]Server implementation pending...[/yellow]")
    console.print("In production, this would start the FastAPI server with:")
    console.print(f"  - WebSocket support for real-time updates")
    console.print(f"  - REST API for graph queries")
    console.print(f"  - Static file serving for frontend")


@cli.command()
@click.option('--path', '-p', default='.', help='Project root path')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'table']), default='table', help='Output format')
def status(path: str, format: str):
    """Show CogniMap status for the project."""
    
    cognimap_dir = Path(path) / '.cognimap'
    if not cognimap_dir.exists():
        console.print("[red]❌ CogniMap not initialized[/red]")
        return
    
    # Load state
    state_file = cognimap_dir / 'state.json'
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
    else:
        state = {}
    
    if format == 'table':
        table = Table(title="CogniMap Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Project Path", state.get('project_path', 'Unknown'))
        table.add_row("Files Tracked", str(state.get('files_count', 0)))
        table.add_row("Fingerprints", str(state.get('fingerprints_count', 0)))
        table.add_row("Analysis Mode", state.get('mode', 'Unknown'))
        table.add_row("Initialized", state.get('initialized_at', 'Unknown'))
        
        console.print(table)
    elif format == 'json':
        console.print_json(data=state)
    elif format == 'yaml':
        console.print(yaml.dump(state, default_flow_style=False))


@cli.command()
@click.option('--path', '-p', default='.', help='Project root path')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'graphml', 'dot']), default='json', help='Graph format')
def export(path: str, output: Optional[str], format: str):
    """Export the architecture graph."""
    
    console.print(f"[bold blue]📊 Exporting architecture graph[/bold blue]")
    
    # Check if initialized
    cognimap_dir = Path(path) / '.cognimap'
    if not cognimap_dir.exists():
        console.print("[red]❌ CogniMap not initialized. Run 'cognimap init' first.[/red]")
        return
    
    # Build graph (simplified)
    graph = {
        'nodes': [],
        'edges': [],
        'metadata': {
            'format': format,
            'project': str(Path(path).absolute())
        }
    }
    
    # Output
    if output:
        output_path = Path(output)
    else:
        output_path = Path(f"architecture.{format}")
    
    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(graph, f, indent=2)
    else:
        console.print(f"[yellow]Export format '{format}' not yet implemented[/yellow]")
        return
    
    console.print(f"✅ Graph exported to {output_path}")


@cli.command()
@click.option('--path', '-p', default='.', help='Project root path')
@click.option('--query', '-q', required=True, help='Query string')
@click.option('--format', '-f', type=click.Choice(['json', 'table']), default='table', help='Output format')
def query(path: str, query: str, format: str):
    """Query the architecture graph."""
    
    console.print(f"[bold blue]🔍 Querying architecture[/bold blue]")
    console.print(f"Query: {query}")
    
    # This would implement a query language
    console.print("[yellow]Query engine not yet implemented[/yellow]")
    console.print("Example queries that would work:")
    console.print("  - semantic_tags CONTAINS 'authentication'")
    console.print("  - complexity > 20")
    console.print("  - type = 'service'")
    console.print("  - has_circular_dependency = true")


def _load_config(config_path: Optional[str]) -> dict:
    """Load configuration from file or defaults."""
    if config_path:
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    # Load default config
    default_config = Path(__file__).parent / 'config' / 'default.yaml'
    if default_config.exists():
        with open(default_config) as f:
            return yaml.safe_load(f)
    
    return {}


def _is_code_file(filepath: Path) -> bool:
    """Check if file is a code file."""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx',
        '.java', '.go', '.rs', '.cpp', '.c',
        '.cs', '.rb', '.php', '.swift', '.kt'
    }
    
    # Skip common non-code directories
    if any(part in str(filepath) for part in [
        '__pycache__', 'node_modules', '.git',
        'venv', '.venv', 'dist', 'build'
    ]):
        return False
    
    return filepath.suffix.lower() in code_extensions


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()