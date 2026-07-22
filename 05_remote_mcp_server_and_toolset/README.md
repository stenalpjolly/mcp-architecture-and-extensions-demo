# 🗺️ Demo 5: Remote MCP Server with MCPToolset & Streamable HTTP

## Architecture Overview

This demo demonstrates configuring an **`MCPToolset`** with **`StreamableHTTPConnectionParams`** to connect to a **Remote MCP Server** using custom header authentication (`X-Goog-Api-Key`).

```python
def get_maps_mcp_toolset():
  dotenv.load_dotenv()
  maps_api_key = os.getenv('MAPS_API_KEY', 'no_api_found')

  tools = MCPToolset(
      connection_params=StreamableHTTPConnectionParams(
          url=MAPS_MCP_URL, headers={'X-Goog-Api-Key': maps_api_key}
      )
  )
  print('MCP Toolset configured for Streamable HTTP connection.')
  return tools
```

## Features

1. **Remote MCP Connection**:
   Connects directly to remote Streamable HTTP / SSE endpoints (`MAPS_MCP_URL`).

2. **Custom Header Authentication**:
   Passes custom authorization headers (`X-Goog-Api-Key`) for authenticated remote MCP tool execution.

3. **No Local Tools**:
   Zero local `@mcp.tool()` definitions — all tools are dynamically retrieved from the remote MCP server!

## Execution

Run the toolset client:
```bash
python3 mcp_toolset_client.py
```
