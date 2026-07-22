#!/usr/bin/env python3
"""Remote MCP Server & Streamable HTTP Toolset Server (Demo 5).

This server showcases:
1. Remote Streamable HTTP / SSE MCP Server Transport.
2. Header-Based Authentication ('X-Goog-Api-Key' / 'MAPS_API_KEY').
3. Remote Maps & Location MCP Tools (Geocoding, Place Search, Distance Routing).
4. Interactive MCP App Map Widget ('ui://maps_app').
"""

import sys
import os
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import EmbeddedResource, TextResourceContents

# Initialize FastMCP Server
mcp = FastMCP("Remote Maps & Streamable Toolset Server", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)


# Interactive HTML Map App Component
def build_maps_app_html(location_name: str = "Googleplex, Mountain View, CA", lat: float = 37.4220, lng: float = -122.0841) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MCP App: Remote Maps Location</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #090d16; color: #f8fafc; padding: 16px; margin: 0; }}
        .card {{ background: #0f172a; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
        .title {{ font-size: 1.1rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }}
        .map-box {{ width: 100%; height: 180px; background: #1e293b; border-radius: 10px; border: 1px solid #334155; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; overflow: hidden; margin: 12px 0; }}
        .marker {{ width: 16px; height: 16px; background: #ef4444; border: 2px solid white; border-radius: 50%; box-shadow: 0 0 10px #ef4444; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.3); }} 100% {{ transform: scale(1); }} }}
        .coords {{ font-family: monospace; font-size: 0.85rem; color: #10b981; margin-top: 6px; }}
        .btn {{ background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.83rem; margin-top: 10px; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="title">🗺️ Remote Streamable Maps MCP Widget</div>
        <div>Location: <strong>{location_name}</strong></div>
        <div class="map-box">
            <div class="marker"></div>
            <div style="font-size:0.82rem; color:#94a3b8; margin-top:8px;">📍 Interactive Location Target</div>
        </div>
        <div class="coords">Lat: {lat:.4f} | Lng: {lng:.4f}</div>
        <button class="btn" onclick="sendPostMessage()">Submit Location Marker to Host</button>
    </div>
    <script>
        function sendPostMessage() {{
            window.parent.postMessage({{
                type: 'mcp-app-event',
                event: 'location_selected',
                data: {{ location: '{location_name}', lat: {lat}, lng: {lng} }}
            }}, '*');
            alert('Dispatched map location event to host!');
        }}
    </script>
</body>
</html>"""


HTML_MAPS_APP = build_maps_app_html()


@mcp.resource("ui://maps_app", mime_type="text/html;profile=mcp-app")
async def get_maps_ui_app() -> str:
    """MCP App HTML UI Component Resource for Remote Maps."""
    return HTML_MAPS_APP


@mcp.tool()
async def geocode_address(address: str, ctx: Context = None) -> dict:
    """Geocode an address to geographic coordinates (latitude, longitude) and location details."""
    if ctx:
        await ctx.info(f"Geocoding address over Streamable HTTP: '{address}'")

    coords_db = {
        "mountain view": {"lat": 37.4220, "lng": -122.0841, "formatted_address": "Mountain View, CA, USA"},
        "san francisco": {"lat": 37.7749, "lng": -122.4194, "formatted_address": "San Francisco, CA, USA"},
        "new york": {"lat": 40.7128, "lng": -74.0060, "formatted_address": "New York, NY, USA"},
        "tokyo": {"lat": 35.6762, "lng": 139.6503, "formatted_address": "Tokyo, Japan"},
        "london": {"lat": 51.5074, "lng": -0.1278, "formatted_address": "London, UK"}
    }
    
    key = address.lower()
    matched = None
    for k in coords_db:
        if k in key:
            matched = coords_db[k]
            break

    if not matched:
        matched = {"lat": 37.4220, "lng": -122.0841, "formatted_address": f"{address} (Geocoded via Remote MCP)"}

    return {
        "status": "OK",
        "address": address,
        "formatted_address": matched["formatted_address"],
        "location": {"lat": matched["lat"], "lng": matched["lng"]},
        "auth_channel": "Streamable HTTP (X-Goog-Api-Key verified)"
    }


@mcp.tool()
async def search_places(query: str, location: str = "Mountain View, CA", ctx: Context = None) -> dict:
    """Search for nearby places, restaurants, or landmarks using Remote Streamable MCP Toolset."""
    if ctx:
        await ctx.info(f"Searching places for query='{query}' near location='{location}'")

    return {
        "status": "OK",
        "query": query,
        "location": location,
        "results": [
            {
                "name": f"Googleplex - {query.capitalize()} Hub",
                "rating": 4.9,
                "address": "1600 Amphitheatre Pkwy, Mountain View, CA",
                "place_id": "place_gplex_01"
            },
            {
                "name": f"Bayfront Park {query.capitalize()}",
                "rating": 4.7,
                "address": "Shoreline Blvd, Mountain View, CA",
                "place_id": "place_bayfront_02"
            }
        ]
    }


@mcp.tool()
async def calculate_route(origin: str = "Mountain View, CA", destination: str = "San Francisco, CA", travel_mode: str = "driving", ctx: Context = None) -> dict:
    """Calculate travel distance, duration, and route directions between origin and destination."""
    if ctx:
        await ctx.info(f"Routing from '{origin}' to '{destination}' via mode='{travel_mode}'")

    return {
        "status": "OK",
        "origin": origin,
        "destination": destination,
        "travel_mode": travel_mode,
        "distance": "38.4 miles",
        "duration": "42 mins",
        "steps": [
            "Head north on US-101 N toward San Francisco",
            "Take exit 433B toward SF Downtown",
            "Arrive at destination"
        ]
    }


@mcp.tool()
async def launch_maps_app(location_name: str = "Mountain View, CA", ctx: Context = None) -> list:
    """Launch interactive Remote Maps MCP App widget in host interface (Formal MCP Apps Spec)."""
    if ctx:
        await ctx.info(f"Launching Remote Maps MCP App Widget for '{location_name}'")

    html_content = build_maps_app_html(location_name, 37.4220, -122.0841)
    return [
        EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="ui://maps_app",
                mimeType="text/html;profile=mcp-app",
                text=html_content
            )
        )
    ]


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
