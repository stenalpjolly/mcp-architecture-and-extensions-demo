# 🗺️ Demo 5: Remote MCP Toolsets (Google Maps & BigQuery)

## Architecture Overview

Demonstrates initializing Remote MCP Toolsets using **Google ADK** (`google.adk.tools.mcp_tool`) over **Streamable HTTP Connections**:

1. **Google Maps Remote MCP Toolset**:
   Authenticates using API Key headers (`X-Goog-Api-Key`).

2. **Google BigQuery Remote MCP Toolset**:
   Authenticates dynamically using Google OAuth Application Default Credentials (`google.auth.default`) and attaches `Authorization: Bearer <token>` and `x-goog-user-project` headers.

```python
import dotenv
import google.auth
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"


def get_maps_mcp_toolset():
  dotenv.load_dotenv()
  maps_api_key = os.getenv("MAPS_API_KEY", "no_api_found")

  tools = MCPToolset(
      connection_params=StreamableHTTPConnectionParams(
          url=MAPS_MCP_URL,
          headers={"X-Goog-Api-Key": maps_api_key},
          timeout=30.0,
          sse_read_timeout=300.0,
      )
  )
  print("MCP Toolset configured for Streamable HTTP connection.")
  return tools


def get_bigquery_mcp_toolset():
  credentials, project_id = google.auth.default(
      scopes=["https://www.googleapis.com/auth/bigquery"]
  )
  credentials.refresh(google.auth.transport.requests.Request())

  HEADERS_WITH_OAUTH = {
      "Authorization": f"Bearer {credentials.token}",
      "x-goog-user-project": project_id,
  }

  tools = MCPToolset(
      connection_params=StreamableHTTPConnectionParams(
          url=BIGQUERY_MCP_URL,
          headers=HEADERS_WITH_OAUTH,
          timeout=30.0,
          sse_read_timeout=300.0,
      )
  )
  print("MCP Toolset configured for Streamable HTTP connection.")
  return tools
```

## Running the Demo

Execute the client script:
```bash
python3 mcp_toolset_client.py
```
