import pytest
from tools.ecosystem.protocols.native_bridge import NativeBridge
from tools.ecosystem.protocols.mcp_bridge import MCPBridge, MCPMessage

@pytest.mark.asyncio
async def test_native_bridge_executes_registered_tool():
    bridge = NativeBridge()
    def sample_tool(x, y):
        return x + y
    tool = bridge.create_tool_wrapper(sample_tool)
    bridge.register_tool(tool)
    result = await bridge.execute_tool('sample_tool', 2, 3)
    assert result.success and result.data == 5


@pytest.mark.asyncio
async def test_native_bridge_query_not_implemented():
    bridge = NativeBridge()
    with pytest.raises(NotImplementedError):
        await bridge.query("test")

@pytest.mark.asyncio
async def test_mcp_bridge_send_and_handler():
    bridge = MCPBridge()
    called = {}
    async def handler(msg: MCPMessage):
        called['data'] = msg.content
        return {'ok': True}
    bridge.register_handler('ping', handler)
    await bridge.connect()
    resp = await bridge.send_message(MCPMessage(type='ping', content={'a':1}))
    assert resp.success and resp.data == {'ok': True}
    assert called['data'] == {'a':1}
