#!/usr/bin/env python3
"""Remote MCP Toolset Client Example (Demo 5).

Demonstrates configuring an MCPToolset with StreamableHTTPConnectionParams
and custom authentication headers ('X-Goog-Api-Key').
"""

import sys
import os
import site
import dotenv
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

MAPS_MCP_URL = os.getenv("MAPS_MCP_URL", "https://maps.mcp.googleapis.com/mcp/v1/sse")


@dataclass
class StreamableHTTPConnectionParams:
    url: str
    headers: Dict[str, str] = field(default_factory=dict)


class MCPToolset:
    def __init__(self, connection_params: StreamableHTTPConnectionParams):
        self.connection_params = connection_params
        self.url = connection_params.url
        self.headers = connection_params.headers
        print(f"✔ MCP Toolset configured for Streamable HTTP connection to {self.url}")

    def get_tools(self):
        print(f"Connecting to remote MCP server at {self.url} with headers {list(self.headers.keys())}...")
        return self


def get_maps_mcp_toolset() -> MCPToolset:
    dotenv.load_dotenv()
    maps_api_key = os.getenv('MAPS_API_KEY', os.getenv('GEMINI_API_KEY', 'no_api_found'))
    
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={    
                "X-Goog-Api-Key": maps_api_key
            }
        )
    )
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools


if __name__ == "__main__":
    toolset = get_maps_mcp_toolset()
    toolset.get_tools()
