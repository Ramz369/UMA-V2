"""
Tools Ecosystem Protocols
Provides bridge interfaces for tool communication
"""

from .native_bridge import NativeBridge, ToolProtocol, ToolResult
from .mcp_bridge import MCPBridge

__all__ = ['NativeBridge', 'ToolProtocol', 'ToolResult', 'native_bridge', 'MCPBridge', 'mcp_bridge']

# Legacy compatibility
native_bridge = NativeBridge()
mcp_bridge = MCPBridge()