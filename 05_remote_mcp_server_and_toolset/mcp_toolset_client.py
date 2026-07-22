#!/usr/bin/env python3
"""Remote MCP Toolsets for Google Maps & BigQuery (Demo 5).

Demonstrates initializing Remote MCP Toolsets using Google ADK / Streamable HTTP connections:
1. Maps MCP Toolset with 'X-Goog-Api-Key' authentication.
2. BigQuery MCP Toolset with OAuth Bearer Token & 'x-goog-user-project' authentication.
"""

import sys
import os
import site
import dotenv
from typing import Dict, Any, Optional

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

import google.auth
import google.auth.transport.requests

try:
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
except ImportError:
    from dataclasses import dataclass, field

    @dataclass
    class StreamableHTTPConnectionParams:
        url: str
        headers: Dict[str, str] = field(default_factory=dict)
        timeout: float = 30.0
        sse_read_timeout: float = 300.0

    class MCPToolset:
        def __init__(self, connection_params: StreamableHTTPConnectionParams):
            self.connection_params = connection_params
            self.url = connection_params.url
            self.headers = connection_params.headers
            print(f"✔ MCPToolset initialized for URL: {self.url}")


MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp" 
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" 


def get_maps_mcp_toolset() -> MCPToolset:
    dotenv.load_dotenv()
    maps_api_key = os.getenv('MAPS_API_KEY', 'no_api_found')
    
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={    
                "X-Goog-Api-Key": maps_api_key
            },
            timeout=30.0,          
            sse_read_timeout=300.0
        )
    )
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools


def get_bigquery_mcp_toolset() -> MCPToolset:   
    try:
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        oauth_token = credentials.token
    except Exception as e:
        print(f"⚠️ Google Auth Default fallback: {e}")
        oauth_token = os.getenv("GOOGLE_OAUTH_TOKEN", "mock_oauth_token")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "mock-gcp-project")
        
    HEADERS_WITH_OAUTH = {
        "Authorization": f"Bearer {oauth_token}",
        "x-goog-user-project": str(project_id)
    }

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=HEADERS_WITH_OAUTH,
            timeout=30.0,          
            sse_read_timeout=300.0
        )
    )
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools


if __name__ == "__main__":
    print("--- 1. Initializing Remote Maps MCP Toolset ---")
    maps_tools = get_maps_mcp_toolset()
    
    print("\n--- 2. Initializing Remote BigQuery MCP Toolset ---")
    bq_tools = get_bigquery_mcp_toolset()
