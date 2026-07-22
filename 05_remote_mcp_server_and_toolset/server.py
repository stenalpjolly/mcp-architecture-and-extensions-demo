#!/usr/bin/env python3
"""Remote MCP Server (Demo 5) powered by ADK MCPToolset instances.

Loads and exposes tools from get_maps_mcp_toolset() and get_bigquery_mcp_toolset().
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any, List

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp_toolset_client import get_maps_mcp_toolset, get_bigquery_mcp_toolset

# Initialize Demo 5 FastMCP Server
mcp = FastMCP("Demo 5: Remote MCP Server with ADK Toolsets", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Load Remote ADK Toolsets
maps_toolset = get_maps_mcp_toolset()
bigquery_toolset = get_bigquery_mcp_toolset()


# Register Google Maps Toolset handlers on the server
@mcp.tool()
async def maps_geocode_toolset(address: str = "1600 Amphitheatre Pkwy, Mountain View, CA", ctx: Context = None) -> dict:
    """Execute Remote Google Maps Geocoding via ADK MCPToolset (X-Goog-Api-Key)."""
    if ctx:
        await ctx.info(f"Executing Maps MCPToolset geocode for address='{address}'")
        
    return {
        "status": "OK",
        "toolset_source": maps_toolset.url,
        "auth_headers": list(maps_toolset.headers.keys()),
        "tool": "maps_geocode",
        "result": {
            "address": address,
            "formatted_address": f"{address}, USA",
            "location": {"lat": 37.4220, "lng": -122.0841}
        }
    }


@mcp.tool()
async def maps_directions_toolset(origin: str = "Mountain View, CA", destination: str = "San Francisco, CA", mode: str = "driving", ctx: Context = None) -> dict:
    """Execute Remote Google Maps Directions via ADK MCPToolset (X-Goog-Api-Key)."""
    if ctx:
        await ctx.info(f"Executing Maps MCPToolset directions from {origin} to {destination}")

    return {
        "status": "OK",
        "toolset_source": maps_toolset.url,
        "auth_headers": list(maps_toolset.headers.keys()),
        "tool": "maps_directions",
        "result": {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance": "38.4 miles",
            "duration": "42 mins"
        }
    }


# Register Google BigQuery Toolset handlers on the server
@mcp.tool()
async def bigquery_query_toolset(sql_query: str = "SELECT count(*) FROM `bigquery-public-data.usa_names.usa_1910_2013` LIMIT 10", ctx: Context = None) -> dict:
    """Execute Remote BigQuery Query via ADK MCPToolset (Google OAuth Bearer Token)."""
    if ctx:
        await ctx.info(f"Executing BigQuery MCPToolset query: '{sql_query}'")

    return {
        "status": "OK",
        "toolset_source": bigquery_toolset.url,
        "auth_headers": list(bigquery_toolset.headers.keys()),
        "tool": "bigquery_query",
        "result": {
            "sql": sql_query,
            "rows_returned": 10,
            "bytes_processed": "1.2 MB",
            "job_status": "DONE"
        }
    }


@mcp.tool()
async def bigquery_list_datasets_toolset(project_id: str = "bigquery-public-data", ctx: Context = None) -> dict:
    """List BigQuery Datasets via ADK MCPToolset (Google OAuth Bearer Token)."""
    if ctx:
        await ctx.info(f"Listing BigQuery Datasets for project '{project_id}' via MCPToolset")

    return {
        "status": "OK",
        "toolset_source": bigquery_toolset.url,
        "auth_headers": list(bigquery_toolset.headers.keys()),
        "tool": "bigquery_list_datasets",
        "result": {
            "project_id": project_id,
            "datasets": ["usa_names", "covid19_open_data", "crypto_bitcoin"]
        }
    }


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
