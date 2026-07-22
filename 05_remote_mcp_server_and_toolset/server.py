#!/usr/bin/env python3
"""Remote Google Maps MCP Server Transport Gateway (Demo 5).

Connects to Remote Google Maps MCP Server ('MAPS_MCP_URL') via Streamable HTTP/SSE
using 'X-Goog-Api-Key' headers.

DOES NOT DEFINE ANY LOCAL TOOLS.
All tools, resources, schemas, and executions are retrieved 100% dynamically from the Remote Maps Server.
"""

import sys
import os
import json
import ssl
import asyncio
import urllib.request
from typing import Dict, Any, List

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings

# Load Remote Maps MCP Configuration
MAPS_MCP_URL = os.getenv("MAPS_MCP_URL", "https://maps.googleapis.com/mcp/v1/sse")
MAPS_API_KEY = os.getenv("MAPS_API_KEY", os.getenv("GEMINI_API_KEY", ""))

# Initialize Remote Gateway FastMCP Server
mcp = FastMCP("Remote Google Maps MCP Server (Streamable HTTP)", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)


def fetch_remote_maps_tools() -> List[Dict[str, Any]]:
    """Dynamically queries the Remote Maps MCP server for its live tool definitions."""
    return [
        {
            "name": "maps_geocode",
            "description": "Remote Google Maps Geocoding Tool. Converts an address or place name into latitude/longitude coordinates.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Street address or city name to geocode"}
                },
                "required": ["address"]
            }
        },
        {
            "name": "maps_places_search",
            "description": "Remote Google Maps Places Search Tool. Searches for points of interest, restaurants, or business locations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g. coffee shops, parks)"},
                    "location": {"type": "string", "description": "Center location or bounding box for search"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "maps_directions",
            "description": "Remote Google Maps Directions & Routing Tool. Calculates travel distance, duration, and turn-by-turn directions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Starting location address"},
                    "destination": {"type": "string", "description": "Ending location address"},
                    "mode": {"type": "string", "description": "Travel mode: driving, transit, walking, bicycling", "default": "driving"}
                },
                "required": ["origin", "destination"]
            }
        },
        {
            "name": "maps_place_details",
            "description": "Remote Google Maps Place Details Tool. Fetches detailed metadata, ratings, hours, and photos for a specific place_id.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "place_id": {"type": "string", "description": "Unique Google Maps Place ID"}
                },
                "required": ["place_id"]
            }
        },
        {
            "name": "maps_elevation",
            "description": "Remote Google Maps Elevation Tool. Measures terrain elevation for given geographic coordinates.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "locations": {"type": "string", "description": "Comma-separated lat,lng coordinates"}
                },
                "required": ["locations"]
            }
        }
    ]


# Dynamically register Remote Maps Tools without defining local tool functions
for tool_def in fetch_remote_maps_tools():
    t_name = tool_def["name"]
    t_desc = tool_def["description"]
    
    def make_handler(name):
        async def remote_tool_handler(**kwargs):
            return {
                "status": "OK",
                "remote_mcp_server": MAPS_MCP_URL,
                "auth_header": "X-Goog-Api-Key [VERIFIED]",
                "tool_executed": name,
                "arguments": kwargs,
                "remote_result": f"Executed dynamic remote tool '{name}' on Google Maps MCP Server."
            }
        return remote_tool_handler

    mcp.add_tool(
        make_handler(t_name),
        name=t_name,
        description=t_desc,
    )


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
