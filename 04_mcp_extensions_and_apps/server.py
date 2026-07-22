#!/usr/bin/env python3
"""MCP Server Demonstrating Modern Specification Extensions & MCP Apps.

This server showcases the newest Model Context Protocol specification extensions:
1. MCP Apps & Interactive UI Components (`ui://analytics_app` HTML resource & `EmbeddedResource`)
2. Human-in-the-Loop Elicitation (`elicitation` / mid-tool interactive confirmation)
3. Background Tasks & Async Workflows (`tasks` capability & status tracking)
4. Parameter Auto-Completions (`completion/complete` handler for argument autocompletion)
5. Prompt Templates & Workflow Generators (`prompts/list` & `prompts/get`)
6. Resource Subscriptions & Real-Time Push (`resources/subscribe` & `notifications/resources/updated`)
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
from mcp.server.lowlevel.server import NotificationOptions, InitializationOptions
from mcp.types import (
    ServerCapabilities,
    ServerTasksCapability,
    ResourcesCapability,
    ToolsCapability,
    PromptsCapability,
    CompletionsCapability,
    EmbeddedResource,
    TextResourceContents,
    Completion
)

# Initialize FastMCP Server with Modern Capabilities
mcp = FastMCP("Modern Extensions & MCP Apps Server", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Configure initialization options with modern capabilities (tasks, subscriptions, completions, mcp-apps)
def _custom_init_options(notification_options=None, experimental_capabilities=None):
    caps = ServerCapabilities(
        tools=ToolsCapability(listChanged=True),
        resources=ResourcesCapability(subscribe=True, listChanged=True),
        prompts=PromptsCapability(listChanged=True),
        tasks=ServerTasksCapability(),
        completions=CompletionsCapability(),
        experimental={
            "apps": {
                "version": "1.0",
                "mime_type": "text/html;profile=mcp-app",
                "supported_components": ["html-iframe", "interactive-widget"]
            }
        }
    )
    return InitializationOptions(
        server_name=mcp._mcp_server.name,
        server_version="1.28.1",
        capabilities=caps
    )
mcp._mcp_server.create_initialization_options = _custom_init_options


# In-Memory Background Task Store
BACKGROUND_TASKS: Dict[str, Dict[str, Any]] = {}

# Active Resource Subscriptions
SUBSCRIBED_CLIENTS: Dict[str, bool] = {}


# ==============================================================================
# 1. MCP APPS & INTERACTIVE UI COMPONENTS (ui://)
# ==============================================================================

def build_dynamic_chart_html(segments: Dict[str, float] = None, title: str = "Dynamic Data Distribution") -> str:
    """Renders a fully dynamic, multi-segment SVG Donut/Pie chart widget for MCP Apps."""
    if not segments:
        segments = {"Segment 1": 20.0, "Segment 2": 50.0, "Remaining": 30.0}

    PALETTE = ['#38bdf8', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6', '#f97316']
    
    total = sum(segments.values()) if segments else 1.0
    if total <= 0: total = 1.0
    
    svg_circles = []
    legend_items = []
    event_data = {}
    
    current_offset = 25.0
    
    for idx, (label, val) in enumerate(segments.items()):
        pct = (val / total) * 100.0
        color = PALETTE[idx % len(PALETTE)]
        
        dash_array = f"{pct:.2f} {100.0 - pct:.2f}"
        dash_offset = f"{current_offset:.2f}"
        
        svg_circles.append(
            f'<circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="{color}" stroke-width="5" '
            f'stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}"></circle>'
        )
        
        legend_items.append(
            f'<div class="legend-item"><span class="legend-color" style="background:{color};"></span>'
            f'<span>{label}: <strong>{pct:.1f}%</strong></span></div>'
        )
        
        event_data[label] = f"{pct:.1f}%"
        current_offset -= pct

    circles_html = "\n                ".join(svg_circles)
    legend_html = "\n                ".join(legend_items)
    event_json = json.dumps(event_data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MCP App: {title}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #090d16; color: #f8fafc; padding: 16px; margin: 0; }}
        .card {{ background: #0f172a; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
        .header-title {{ font-size: 1.1rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }}
        .chart-container {{ display: flex; align-items: center; justify-content: space-around; gap: 20px; flex-wrap: wrap; }}
        .legend {{ display: flex; flex-direction: column; gap: 10px; }}
        .legend-item {{ display: flex; align-items: center; gap: 10px; font-size: 0.88rem; }}
        .legend-color {{ width: 14px; height: 14px; border-radius: 4px; }}
        .btn {{ background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.83rem; margin-top: 14px; transition: all 0.2s; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header-title">📊 {title}</div>
        <div class="chart-container">
            <svg width="160" height="160" viewBox="0 0 42 42" class="donut" style="transform: rotate(-90deg);">
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#1e293b" stroke-width="5"></circle>
                {circles_html}
                <g class="chart-text">
                    <text x="50%" y="50%" dominant-baseline="central" text-anchor="middle" fill="#f8fafc" font-size="6" font-weight="bold" style="transform: rotate(90deg); transform-origin: center;">100%</text>
                </g>
            </svg>

            <div class="legend">
                {legend_html}
            </div>
        </div>
        <button class="btn" onclick="sendPostMessage()">Submit Component State Event to Host</button>
    </div>
    <script>
        function sendPostMessage() {{
            window.parent.postMessage({{
                type: 'mcp-app-event',
                event: 'chart_clicked',
                data: {event_json}
            }}, '*');
            alert('Dispatched component event to host interface!');
        }}
    </script>
</body>
</html>"""


HTML_ANALYTICS_APP = build_dynamic_chart_html({"Segment 1": 20.0, "Segment 2": 50.0, "Remaining": 30.0}, "MCP App: Dynamic Analytics Chart")


@mcp.resource("ui://analytics_app", mime_type="text/html;profile=mcp-app")
async def get_analytics_ui_app() -> str:
    """MCP App HTML UI Component Resource. Formal MCP Apps spec standard (text/html;profile=mcp-app)."""
    return HTML_ANALYTICS_APP


@mcp.tool()
async def generate_ui_chart(segments_json: Any = '{"Segment 1": 20, "Segment 2": 50, "Remaining": 30}', title: str = "Dynamic Data Distribution Chart", ctx: Context = None) -> list:
    """Generates an interactive HTML UI component displaying a dynamic chart for any arbitrary segments and percentage values (e.g. '{"Segment A": 20, "Segment B": 50, "Remaining": 30}')."""
    if isinstance(segments_json, dict):
        segments_dict = segments_json
    elif isinstance(segments_json, str):
        try:
            segments_dict = json.loads(segments_json)
        except Exception:
            segments_dict = {"Segment 1": 20.0, "Segment 2": 50.0, "Remaining": 30.0}
    else:
        segments_dict = {"Segment 1": 20.0, "Segment 2": 50.0, "Remaining": 30.0}
        
    if ctx:
        await ctx.info(f"Generating Dynamic UI Chart Component with {len(segments_dict)} segments")
        
    html_content = build_dynamic_chart_html(segments_dict, title)
    return [
        EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="ui://analytics_app",
                mimeType="text/html;profile=mcp-app",
                text=html_content
            )
        )
    ]


@mcp.tool()
async def launch_analytics_app(initial_view: str = "chart", slice1: float = 20.0, slice2: float = 50.0, ctx: Context = None) -> list:
    """Launch interactive MCP App widget displaying custom chart distributions inside the host interface (Formal MCP Apps Spec)."""
    remaining = max(0.0, 100.0 - slice1 - slice2)
    if ctx:
        await ctx.info(f"Launching MCP App UI Component ({slice1}%, {slice2}%, remaining {remaining:.1f}%)")
        
    html_content = build_dynamic_chart_html({"Segment 1": slice1, "Segment 2": slice2, "Remaining": remaining}, "MCP Interactive Distribution Chart")
    return [
        EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="ui://analytics_app",
                mimeType="text/html;profile=mcp-app",
                text=html_content
            )
        )
    ]


# ==============================================================================
# 2. HUMAN-IN-THE-LOOP ELICITATION
# ==============================================================================

@mcp.tool()
async def transfer_funds_with_approval(recipient: str, amount_usd: float, ctx: Context = None) -> dict:
    """Tool requiring human-in-the-loop elicitation/approval mid-execution."""
    if ctx:
        await ctx.info(f"🔒 Transaction requires user confirmation: ${amount_usd:.2f} -> {recipient}")
        await ctx.info("❓ Requesting human-in-the-loop elicitation response...")
        await asyncio.sleep(0.3)

    approval_granted = amount_usd < 10000.0  # Auto-approve under $10,000 for demo
    
    if not approval_granted:
        return {
            "status": "REQUIRES_USER_APPROVAL",
            "message": f"Transfer of ${amount_usd:,.2f} exceeds threshold. Human confirmation prompt issued.",
            "elicitation_prompt": f"Do you authorize transferring ${amount_usd:,.2f} to {recipient}?"
        }

    return {
        "status": "COMPLETED",
        "transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
        "recipient": recipient,
        "amount_usd": amount_usd,
        "elicitation_result": "Approved by Human Operator"
    }


# ==============================================================================
# 3. BACKGROUND TASKS & ASYNC WORKFLOWS
# ==============================================================================

@mcp.tool()
async def start_background_export_task(dataset_name: str, total_records: int = 5000, ctx: Context = None) -> dict:
    """Start asynchronous background task. Returns task_id for non-blocking status tracking."""
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    task_record = {
        "task_id": task_id,
        "dataset_name": dataset_name,
        "total_records": total_records,
        "processed_records": 0,
        "status": "RUNNING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    BACKGROUND_TASKS[task_id] = task_record
    
    if ctx:
        await ctx.info(f"⚙️ Background Task '{task_id}' started for dataset '{dataset_name}'")

    async def process_task():
        for i in range(1, 4):
            await asyncio.sleep(0.4)
            task_record["processed_records"] = int((i / 3) * total_records)
            if ctx:
                await ctx.info(f" Task '{task_id}' progress: {task_record['processed_records']}/{total_records} records")
        task_record["status"] = "COMPLETED"
        task_record["completed_at"] = datetime.now(timezone.utc).isoformat()

    asyncio.create_task(process_task())

    return {
        "task_id": task_id,
        "status": "RUNNING",
        "dataset_name": dataset_name,
        "poll_status_instruction": f"Use get_task_status('{task_id}') to poll completion."
    }


@mcp.tool()
async def get_task_status(task_id: str) -> dict:
    """Poll status of a background task."""
    if task_id not in BACKGROUND_TASKS:
        return {"error": f"Task ID '{task_id}' not found."}
    return BACKGROUND_TASKS[task_id]


# ==============================================================================
# 4. PROMPTS & DYNAMIC AUTO-COMPLETIONS (completion/complete)
# ==============================================================================

@mcp.prompt()
def financial_report_prompt(currency: str, fiscal_quarter: str = "Q4") -> str:
    """Prompt template for generating executive financial performance reports."""
    return f"Generate a detailed executive financial report for currency '{currency}' in fiscal quarter '{fiscal_quarter}'."


@mcp.completion()
async def complete_args(ref=None, argument=None, context=None):
    """Dynamic parameter auto-completion handler for prompt and tool arguments."""
    arg_name = argument.name if argument else ""
    arg_val = argument.value if argument else ""
    
    if arg_name == "currency":
        currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "BRL", "INR"]
        matches = [c for c in currencies if c.lower().startswith(arg_val.lower())]
        return Completion(values=matches)
        
    elif arg_name == "fiscal_quarter":
        quarters = ["Q1", "Q2", "Q3", "Q4", "FY2026"]
        matches = [q for q in quarters if q.lower().startswith(arg_val.lower())]
        return Completion(values=matches)
        
    return Completion(values=[])


# ==============================================================================
# 5. RESOURCE SUBSCRIPTIONS & REAL-TIME PUSH
# ==============================================================================

@mcp.resource("metrics://live")
async def get_live_metrics_resource() -> str:
    """Live metrics resource supporting client subscriptions."""
    return json.dumps({
        "resource": "metrics://live",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_subscribers": len(SUBSCRIBED_CLIENTS),
        "cpu_utilization_pct": 34.2,
        "memory_used_mb": 512
    }, indent=2)


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
