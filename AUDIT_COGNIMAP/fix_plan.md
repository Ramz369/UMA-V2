1. `cognimap/core/protocol.py` ➜ audit external imports ➜ ensure protocols only depend on bridge interfaces ➜ medium
2. `tools/ecosystem/protocols/native_bridge.py` ➜ add logging for tool registration failures ➜ low
3. `tools/ecosystem/protocols/mcp_bridge.py` ➜ handle reconnect logic for `connect` method ➜ medium
4. `cognimap/graph/graph_builder.py` ➜ extend to include classes/functions for node granularity ➜ high
