#!/usr/bin/env python3
"""Official MCP Inspector Server Demo (Demo 6).

Designed specifically for testing and inspection using the official
Model Context Protocol Inspector UI (@modelcontextprotocol/inspector).

Exposes:
1. Tools (add_numbers, inspect_system_metrics, generate_inspector_card)
2. Resources (memo://server_status, ui://inspector_app)
3. Prompts (system_debug_prompt, code_review_prompt)
"""

import sys
import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import EmbeddedResource, TextResourceContents

# Initialize Demo 6 FastMCP Server
mcp = FastMCP("Official MCP Inspector Target Server", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)


# Dynamic HTML Component for Inspector UI
INSPECTOR_APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Official MCP Inspector Widget</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #1e1f20; color: #e3e3e3; padding: 16px; margin: 0; }
        .card { background: #282a2c; border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }
        .title { color: #8ab4f8; font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
        .badge { background: rgba(138, 180, 248, 0.15); color: #8ab4f8; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; font-family: monospace; }
        .btn { background: #4285f4; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.82rem; margin-top: 12px; }
        .btn:hover { background: #1a73e8; }
    </style>
</head>
<body>
    <div class="card">
        <div class="title">🔍 Official MCP Inspector Widget <span class="badge">v0.15.0</span></div>
        <p style="font-size: 0.88rem; color: #c4c7c5; margin-bottom: 8px;">
            This interactive component was rendered by the official Model Context Protocol Inspector UI over SSE/Stdio transport.
        </p>
        <button class="btn" onclick="notifyHost()">Dispatch Inspector Notification</button>
    </div>
    <script>
        function notifyHost() {
            window.parent.postMessage({ type: 'mcp-app-event', event: 'inspector_clicked', timestamp: new Date().toISOString() }, '*');
            alert('Sent inspection telemetry to host!');
        }
    </script>
</body>
</html>"""


# Resources
@mcp.resource("memo://server_status")
async def get_server_status() -> str:
    """Live server diagnostics and uptime status metadata."""
    return json.dumps({
        "server_name": "Official MCP Inspector Server (Demo 6)",
        "protocol_version": "2024-11-05",
        "status": "HEALTHY",
        "active_transports": ["stdio", "sse"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2)


@mcp.resource("ui://inspector_app", mime_type="text/html;profile=mcp-app")
async def get_inspector_app_ui() -> str:
    """HTML UI Component resource for Official MCP Inspector testing."""
    return INSPECTOR_APP_HTML


# Prompts
@mcp.prompt()
async def system_debug_prompt(component: str = "database_connection") -> str:
    """Generates a debug prompt template for inspecting specific server components."""
    return f"""You are acting as an expert MCP protocol debugger inspecting component '{component}'.
Please run system diagnostics, check tools/list schema validation, and report any protocol compliance issues."""


@mcp.prompt()
async def code_review_prompt(language: str = "python") -> str:
    """Generates a code review prompt template for the specified programming language."""
    return f"""Perform a comprehensive code review for {language} code. Check for security vulnerabilities, error handling, performance bottlenecks, and adherence to PEP 8 / Google Style Guidelines."""


# Tools
@mcp.tool()
async def add_numbers(a: int = 15, b: int = 27, ctx: Context = None) -> dict:
    """Add two integers together. Demonstrates standard tool execution in Official MCP Inspector."""
    if ctx:
        await ctx.info(f"Adding numbers: {a} + {b}")
    return {
        "operation": "add_numbers",
        "a": a,
        "b": b,
        "sum": a + b
    }


@mcp.tool()
async def inspect_system_metrics(ctx: Context = None) -> dict:
    """Inspect live server telemetry, active transport connections, and memory metrics."""
    if ctx:
        await ctx.info("Gathering server telemetry metrics for Official MCP Inspector")
    return {
        "server": "Demo 6 Official MCP Inspector Target",
        "memory_usage": "34.2 MB",
        "active_transports": ["stdio", "sse"],
        "protocol_version": "2024-11-05",
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True,
            "logging": True
        }
    }


@mcp.tool()
async def generate_inspector_card(title: str = "System Health Report", severity: str = "info", ctx: Context = None) -> list:
    """Generates a dynamic HTML UI component displaying custom severity reports in Official MCP Inspector."""
    if ctx:
        await ctx.info(f"Generating Inspector Report Card: title='{title}' severity='{severity}'")

    card_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: sans-serif; background: #1e1f20; color: #e3e3e3; padding: 14px;">
    <div style="background: #282a2c; border-left: 4px solid {'#8ab4f8' if severity == 'info' else '#f28b82'}; padding: 14px; border-radius: 6px;">
        <h3 style="margin: 0 0 6px 0; color: #8ab4f8;">📋 {title}</h3>
        <p style="margin: 0; font-size: 0.85rem; color: #c4c7c5;">Severity Level: <strong style="text-transform: uppercase;">{severity}</strong></p>
    </div>
</body>
</html>"""

    return [
        EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="ui://inspector_app",
                mimeType="text/html;profile=mcp-app",
                text=card_html
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
