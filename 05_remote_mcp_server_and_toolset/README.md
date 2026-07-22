# 🗺️ Demo 5: Remote MCP Server & Streamable HTTP Toolset

## Architecture Overview

This demo showcases connecting to a **Remote MCP Server** via **Streamable HTTP & SSE Transport** using custom header authentication (`X-Goog-Api-Key`).

```
┌──────────────────────────────────────┐          Streamable HTTP          ┌───────────────────────────────────────┐
│       Client Host / MCP Toolset       │  ────────────────────────────►  │     Remote Maps MCP Server (Port 8005) │
│ (headers={"X-Goog-Api-Key": key})     │  ◄────────────────────────────  │  • geocode_address                   │
└──────────────────────────────────────┘     SSE Stream & POST Messages   │  • search_places                     │
                                                                           │  • calculate_route                   │
                                                                           │  • launch_maps_app (ui://maps_app)   │
                                                                           └───────────────────────────────────────┘
```

## Features

1. **Header-Based Authentication**:
   Client toolsets connect with custom headers like `X-Goog-Api-Key` or `Authorization`.

2. **Streamable HTTP Connection**:
   Uses `MCPToolset` with `StreamableHTTPConnectionParams` to route RPC calls over SSE and POST channels.

3. **Remote Maps Tools**:
   - `geocode_address`: Converts location text into latitude/longitude coordinates.
   - `search_places`: Searches for points of interest nearby.
   - `calculate_route`: Calculates distance, travel time, and turn-by-turn directions.
   - `launch_maps_app`: Renders an embedded interactive HTML Map widget (`ui://maps_app`).

## Quickstart

Run the server independently:
```bash
python3 server.py --sse --port 8005
```

Test the remote toolset client:
```bash
python3 mcp_toolset_client.py
```
