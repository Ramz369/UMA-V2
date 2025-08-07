#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: ac96c1ab-5909-4089-824f-a6f5994240bc
birth: 2025-08-07T07:23:38.074092Z
parent: None
intent: Tool Taxonomy System for COGPLAN
semantic_tags: [api, testing, model, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.074839Z
hash: dc94ee1d
language: python
type: tool
@end:cognimap
"""

"""
Tool Taxonomy System for COGPLAN

Classifies tools into atomic (simple) and composite (complex) categories,
enabling proper organization and agent orchestration.
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod


class ToolType(Enum):
    """Primary tool classification."""
    ATOMIC = "atomic"              # Single function, direct execution
    COMPOSITE = "composite"        # Multi-step workflow
    PIPELINE = "pipeline"          # Sequential tool chain
    ORCHESTRATED = "orchestrated"  # Agent-managed execution
    FLOW = "flow"                  # Parallel/branching execution


class ToolComplexity(Enum):
    """Tool complexity levels."""
    SIMPLE = 1      # Direct execution, no processing
    MODERATE = 2    # Some data processing required
    COMPLEX = 3     # Multiple steps, decision points
    INTELLIGENT = 4 # Requires reasoning/analysis


class ToolDomain(Enum):
    """Tool domain categories."""
    SYSTEM = "system"              # OS/filesystem operations
    NETWORK = "network"            # Network/API calls
    DATA = "data"                  # Data processing/transformation
    RESEARCH = "research"          # Information gathering/analysis
    SEO = "seo"                    # SEO/marketing analysis
    SCRAPING = "scraping"          # Web scraping/extraction
    INTELLIGENCE = "intelligence"  # AI/ML operations
    MONITORING = "monitoring"      # System/data monitoring
    AUTOMATION = "automation"      # Task automation


@dataclass
class ToolMetadata:
    """Metadata for tool classification."""
    name: str
    type: ToolType
    complexity: ToolComplexity
    domain: ToolDomain
    description: str
    requires_agents: List[str] = None
    dependencies: List[str] = None
    credit_multiplier: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "complexity": self.complexity.value,
            "domain": self.domain.value,
            "description": self.description,
            "requires_agents": self.requires_agents or [],
            "dependencies": self.dependencies or [],
            "credit_multiplier": self.credit_multiplier
        }


class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self.execution_count = 0
        self.total_credits_used = 0
        self.average_execution_time = 0
        
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        pass
    
    @abstractmethod
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate input parameters."""
        pass
    
    def get_credit_cost(self, **kwargs) -> float:
        """Calculate credit cost for execution."""
        base_cost = 1.0
        
        # Adjust by complexity
        complexity_multipliers = {
            ToolComplexity.SIMPLE: 1.0,
            ToolComplexity.MODERATE: 2.0,
            ToolComplexity.COMPLEX: 5.0,
            ToolComplexity.INTELLIGENT: 10.0
        }
        
        base_cost *= complexity_multipliers[self.metadata.complexity]
        base_cost *= self.metadata.credit_multiplier
        
        return base_cost


class AtomicTool(BaseTool):
    """
    Atomic tools are simple, single-purpose functions.
    They execute directly without orchestration.
    """
    
    def __init__(self, metadata: ToolMetadata, function: Callable):
        super().__init__(metadata)
        self.function = function
        
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the atomic function."""
        if not await self.validate_inputs(**kwargs):
            return {"error": "Invalid inputs"}
        
        try:
            result = await self.function(**kwargs)
            self.execution_count += 1
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Basic input validation."""
        # Can be overridden for specific validation
        return True


class CompositeTool(BaseTool):
    """
    Composite tools combine multiple atomic tools or steps.
    They may require agent orchestration.
    """
    
    def __init__(self, metadata: ToolMetadata):
        super().__init__(metadata)
        self.steps: List[Dict[str, Any]] = []
        self.atomic_tools: Dict[str, AtomicTool] = {}
        
    def add_step(self, name: str, tool: Optional[AtomicTool] = None, 
                 function: Optional[Callable] = None, **kwargs):
        """Add a step to the composite workflow."""
        step = {
            "name": name,
            "tool": tool,
            "function": function,
            "params": kwargs
        }
        self.steps.append(step)
        
        if tool:
            self.atomic_tools[name] = tool
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the composite workflow."""
        if not await self.validate_inputs(**kwargs):
            return {"error": "Invalid inputs"}
        
        results = {}
        context = kwargs.copy()
        
        for step in self.steps:
            step_name = step["name"]
            
            if step["tool"]:
                # Execute atomic tool
                result = await step["tool"].execute(**context)
            elif step["function"]:
                # Execute function
                result = await step["function"](context, **step["params"])
            else:
                result = {"error": f"No implementation for step {step_name}"}
            
            results[step_name] = result
            
            # Update context with results for next steps
            if result.get("success"):
                context[f"{step_name}_result"] = result.get("result")
            else:
                # Stop on failure
                return {
                    "success": False,
                    "failed_step": step_name,
                    "error": result.get("error"),
                    "partial_results": results
                }
        
        self.execution_count += 1
        return {
            "success": True,
            "results": results,
            "final_output": self.synthesize_results(results)
        }
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate inputs for composite workflow."""
        # Override in subclasses for specific validation
        return True
    
    def synthesize_results(self, results: Dict[str, Any]) -> Any:
        """Synthesize results from all steps."""
        # Override in subclasses for specific synthesis
        return results


class PipelineTool(CompositeTool):
    """
    Pipeline tools execute steps sequentially,
    passing output from one step as input to the next.
    """
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute pipeline sequentially."""
        if not await self.validate_inputs(**kwargs):
            return {"error": "Invalid inputs"}
        
        current_input = kwargs
        results = []
        
        for i, step in enumerate(self.steps):
            step_name = step["name"]
            
            if step["tool"]:
                result = await step["tool"].execute(**current_input)
            elif step["function"]:
                result = await step["function"](current_input, **step["params"])
            else:
                result = {"error": f"No implementation for step {step_name}"}
            
            results.append({
                "step": step_name,
                "result": result
            })
            
            if result.get("success"):
                # Use output as next input
                current_input = result.get("result", current_input)
            else:
                return {
                    "success": False,
                    "failed_step": step_name,
                    "error": result.get("error"),
                    "completed_steps": results
                }
        
        self.execution_count += 1
        return {
            "success": True,
            "pipeline_results": results,
            "final_output": current_input
        }


class OrchestratedTool(CompositeTool):
    """
    Orchestrated tools require agent intervention for decisions.
    Agents manage the execution flow based on intermediate results.
    """
    
    def __init__(self, metadata: ToolMetadata, orchestrator_agent: str):
        super().__init__(metadata)
        self.orchestrator_agent = orchestrator_agent
        self.decision_points: List[Dict[str, Any]] = []
        
    def add_decision_point(self, name: str, condition: Callable, 
                          branches: Dict[str, List[str]]):
        """Add a decision point requiring agent evaluation."""
        self.decision_points.append({
            "name": name,
            "condition": condition,
            "branches": branches
        })
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with agent orchestration."""
        if not await self.validate_inputs(**kwargs):
            return {"error": "Invalid inputs"}
        
        # This would interact with the actual agent
        # For now, simulate orchestration
        results = await super().execute(**kwargs)
        
        # Add orchestration metadata
        results["orchestrator"] = self.orchestrator_agent
        results["decisions_made"] = len(self.decision_points)
        
        return results


class ToolTaxonomy:
    """
    Manages the classification and organization of all tools.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.atomic_tools: Dict[str, AtomicTool] = {}
        self.composite_tools: Dict[str, CompositeTool] = {}
        self.taxonomy_map: Dict[ToolDomain, List[str]] = {
            domain: [] for domain in ToolDomain
        }
        
    def register_tool(self, tool: BaseTool):
        """Register a tool in the taxonomy."""
        name = tool.metadata.name
        self.tools[name] = tool
        
        # Classify by type
        if isinstance(tool, AtomicTool):
            self.atomic_tools[name] = tool
        elif isinstance(tool, CompositeTool):
            self.composite_tools[name] = tool
        
        # Organize by domain
        domain = tool.metadata.domain
        self.taxonomy_map[domain].append(name)
        
    def get_tools_by_domain(self, domain: ToolDomain) -> List[BaseTool]:
        """Get all tools in a domain."""
        tool_names = self.taxonomy_map.get(domain, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[BaseTool]:
        """Get all tools of a specific type."""
        return [
            tool for tool in self.tools.values()
            if tool.metadata.type == tool_type
        ]
    
    def get_tools_by_complexity(self, complexity: ToolComplexity) -> List[BaseTool]:
        """Get all tools of a specific complexity."""
        return [
            tool for tool in self.tools.values()
            if tool.metadata.complexity == complexity
        ]
    
    def suggest_tool_composition(self, goal: str) -> List[str]:
        """Suggest tools that could be composed for a goal."""
        # This would use semantic analysis in production
        # For now, return relevant tools based on keywords
        suggestions = []
        
        keywords = {
            "research": [ToolDomain.RESEARCH, ToolDomain.INTELLIGENCE],
            "seo": [ToolDomain.SEO, ToolDomain.SCRAPING],
            "data": [ToolDomain.DATA, ToolDomain.SCRAPING],
            "monitor": [ToolDomain.MONITORING, ToolDomain.AUTOMATION]
        }
        
        for keyword, domains in keywords.items():
            if keyword in goal.lower():
                for domain in domains:
                    tools = self.get_tools_by_domain(domain)
                    suggestions.extend([t.metadata.name for t in tools])
        
        return list(set(suggestions))
    
    def analyze_tool_usage(self) -> Dict[str, Any]:
        """Analyze tool usage patterns."""
        total_executions = sum(t.execution_count for t in self.tools.values())
        total_credits = sum(t.total_credits_used for t in self.tools.values())
        
        # Most used tools
        most_used = sorted(
            self.tools.values(),
            key=lambda t: t.execution_count,
            reverse=True
        )[:10]
        
        # Most expensive tools
        most_expensive = sorted(
            self.tools.values(),
            key=lambda t: t.total_credits_used,
            reverse=True
        )[:10]
        
        # Domain distribution
        domain_usage = {}
        for domain in ToolDomain:
            domain_tools = self.get_tools_by_domain(domain)
            domain_usage[domain.value] = {
                "count": len(domain_tools),
                "executions": sum(t.execution_count for t in domain_tools),
                "credits": sum(t.total_credits_used for t in domain_tools)
            }
        
        return {
            "total_tools": len(self.tools),
            "atomic_tools": len(self.atomic_tools),
            "composite_tools": len(self.composite_tools),
            "total_executions": total_executions,
            "total_credits_used": total_credits,
            "most_used_tools": [t.metadata.name for t in most_used],
            "most_expensive_tools": [t.metadata.name for t in most_expensive],
            "domain_distribution": domain_usage
        }


# Example atomic tools
def create_example_atomic_tools():
    """Create example atomic tools."""
    tools = []
    
    # System tool
    async def list_files(path: str = ".") -> List[str]:
        """List files in directory."""
        import os
        return os.listdir(path)
    
    ls_tool = AtomicTool(
        metadata=ToolMetadata(
            name="ls",
            type=ToolType.ATOMIC,
            complexity=ToolComplexity.SIMPLE,
            domain=ToolDomain.SYSTEM,
            description="List files in directory"
        ),
        function=list_files
    )
    tools.append(ls_tool)
    
    # Network tool
    async def fetch_url(url: str) -> str:
        """Fetch content from URL."""
        # Simplified for example
        return f"Content from {url}"
    
    fetch_tool = AtomicTool(
        metadata=ToolMetadata(
            name="fetch",
            type=ToolType.ATOMIC,
            complexity=ToolComplexity.SIMPLE,
            domain=ToolDomain.NETWORK,
            description="Fetch URL content"
        ),
        function=fetch_url
    )
    tools.append(fetch_tool)
    
    return tools


# Example composite tool
def create_example_composite_tool():
    """Create example composite research tool."""
    
    tool = CompositeTool(
        metadata=ToolMetadata(
            name="topic_researcher",
            type=ToolType.COMPOSITE,
            complexity=ToolComplexity.COMPLEX,
            domain=ToolDomain.RESEARCH,
            description="Research a topic comprehensively",
            requires_agents=["analyzer", "synthesizer"],
            credit_multiplier=2.5
        )
    )
    
    # Add workflow steps
    async def extract_keywords(context: Dict, **kwargs) -> Dict[str, Any]:
        topic = context.get("topic", "")
        keywords = topic.split()  # Simplified
        return {"success": True, "result": keywords}
    
    async def search_web(context: Dict, **kwargs) -> Dict[str, Any]:
        keywords = context.get("extract_keywords_result", [])
        results = [f"Result for {kw}" for kw in keywords]
        return {"success": True, "result": results}
    
    async def analyze_results(context: Dict, **kwargs) -> Dict[str, Any]:
        results = context.get("search_web_result", [])
        analysis = f"Analyzed {len(results)} results"
        return {"success": True, "result": analysis}
    
    tool.add_step("extract_keywords", function=extract_keywords)
    tool.add_step("search_web", function=search_web)
    tool.add_step("analyze_results", function=analyze_results)
    
    return tool


# Initialize global taxonomy
GLOBAL_TAXONOMY = ToolTaxonomy()


def initialize_taxonomy():
    """Initialize the taxonomy with example tools."""
    # Add atomic tools
    for tool in create_example_atomic_tools():
        GLOBAL_TAXONOMY.register_tool(tool)
    
    # Add composite tool
    GLOBAL_TAXONOMY.register_tool(create_example_composite_tool())
    
    return GLOBAL_TAXONOMY


if __name__ == "__main__":
    import asyncio
    
    # Initialize and test
    taxonomy = initialize_taxonomy()
    
    print("Tool Taxonomy System")
    print("=" * 50)
    
    # Show registered tools
    print(f"\nRegistered Tools: {len(taxonomy.tools)}")
    for name, tool in taxonomy.tools.items():
        print(f"  - {name}: {tool.metadata.type.value} / {tool.metadata.domain.value}")
    
    # Test atomic tool
    print("\nTesting Atomic Tool (ls):")
    ls_tool = taxonomy.atomic_tools.get("ls")
    if ls_tool:
        result = asyncio.run(ls_tool.execute(path="."))
        print(f"  Result: {result.get('success')}")
    
    # Test composite tool
    print("\nTesting Composite Tool (topic_researcher):")
    researcher = taxonomy.composite_tools.get("topic_researcher")
    if researcher:
        result = asyncio.run(researcher.execute(topic="AI safety"))
        print(f"  Result: {result.get('success')}")
        print(f"  Steps completed: {len(result.get('results', {}))}")
    
    # Analyze usage
    print("\nTaxonomy Analysis:")
    analysis = taxonomy.analyze_tool_usage()
    print(f"  Total tools: {analysis['total_tools']}")
    print(f"  Atomic: {analysis['atomic_tools']}")
    print(f"  Composite: {analysis['composite_tools']}")