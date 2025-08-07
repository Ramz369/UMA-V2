"""
Native Bridge Protocol
Provides interface between tools and the ecosystem
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import json


@dataclass
class ToolResult:
    """Result from a tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolProtocol:
    """Base protocol for all tools"""
    
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the tool"""
        self.initialized = True
        return True
        
    async def execute(self, *args, **kwargs) -> ToolResult:
        """Execute the tool"""
        raise NotImplementedError
        
    async def cleanup(self) -> None:
        """Clean up resources"""
        pass


class NativeBridge:
    """
    Bridge between native Python tools and the ecosystem.
    Handles tool registration, execution, and result marshalling.
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolProtocol] = {}
        self.enabled = True
        
    def register_tool(self, tool: ToolProtocol) -> None:
        """Register a tool with the bridge"""
        self.tools[tool.name] = tool
        
    def get_tool(self, name: str) -> Optional[ToolProtocol]:
        """Get a registered tool"""
        return self.tools.get(name)
        
    async def execute_tool(self, name: str, *args, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool '{name}' not found"
            )
            
        if not tool.initialized:
            await tool.initialize()
            
        try:
            return await tool.execute(*args, **kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def marshal_result(self, result: Any) -> str:
        """Marshal a result to JSON"""
        if isinstance(result, ToolResult):
            return json.dumps({
                'success': result.success,
                'data': result.data,
                'error': result.error,
                'metadata': result.metadata
            })
        return json.dumps(result)
        
    def unmarshal_result(self, data: str) -> Any:
        """Unmarshal JSON to result"""
        parsed = json.loads(data)
        if isinstance(parsed, dict) and 'success' in parsed:
            return ToolResult(**parsed)
        return parsed
        
    def create_tool_wrapper(self, func: callable) -> ToolProtocol:
        """Create a tool wrapper for a function"""
        class FunctionTool(ToolProtocol):
            def __init__(self):
                super().__init__(func.__name__)
                self.func = func
                
            async def execute(self, *args, **kwargs) -> ToolResult:
                try:
                    result = self.func(*args, **kwargs)
                    return ToolResult(success=True, data=result)
                except Exception as e:
                    return ToolResult(success=False, data=None, error=str(e))
                    
        return FunctionTool()
    
    def enable(self) -> None:
        """Enable the bridge"""
        self.enabled = True
        
    def disable(self) -> None:
        """Disable the bridge"""
        self.enabled = False
        
    def is_enabled(self) -> bool:
        """Check if bridge is enabled"""
        return self.enabled
        
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.tools.keys())
        
    def clear_tools(self) -> None:
        """Clear all registered tools"""
        self.tools.clear()