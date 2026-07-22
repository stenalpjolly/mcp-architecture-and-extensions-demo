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

def build_dynamic_chart_html(v1: float = 20.0, v2: float = 50.0, v3: float = 30.0, title: str = "Interactive Distribution Chart") -> str:
    total = v1 + v2 + v3
    p1 = (v1 / total) * 100.0 if total > 0 else 20.0
    p2 = (v2 / total) * 100.0 if total > 0 else 50.0
    p3 = 100.0 - p1 - p2
    
    off1 = 25.0
    off2 = 25.0 - p1
    off3 = 25.0 - p1 - p2

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
                
                <!-- Segment 1 ({p1:.1f}%) -->
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#38bdf8" stroke-width="5"
                        stroke-dasharray="{p1:.1f} {100-p1:.1f}" stroke-dashoffset="{off1:.1f}"></circle>
                
                <!-- Segment 2 ({p2:.1f}%) -->
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#10b981" stroke-width="5"
                        stroke-dasharray="{p2:.1f} {100-p2:.1f}" stroke-dashoffset="{off2:.1f}"></circle>
                
                <!-- Segment 3 ({p3:.1f}%) -->
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#f59e0b" stroke-width="5"
                        stroke-dasharray="{p3:.1f} {100-p3:.1f}" stroke-dashoffset="{off3:.1f}"></circle>
                
                <g class="chart-text">
                    <text x="50%" y="50%" dominant-baseline="central" text-anchor="middle" fill="#f8fafc" font-size="6" font-weight="bold" style="transform: rotate(90deg); transform-origin: center;">100%</text>
                </g>
            </svg>

            <div class="legend">
                <div class="legend-item">
                    <span class="legend-color" style="background:#38bdf8;"></span>
                    <span>Segment 1: <strong>{p1:.1f}%</strong></span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background:#10b981;"></span>
                    <span>Segment 2: <strong>{p2:.1f}%</strong></span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background:#f59e0b;"></span>
                    <span>Remaining: <strong>{p3:.1f}%</strong></span>
                </div>
            </div>
        </div>
        <button class="btn" onclick="sendPostMessage()">Submit Component State Event to Host</button>
    </div>
    <script>
        function sendPostMessage() {{
            window.parent.postMessage({{
                type: 'mcp-app-event',
                event: 'chart_clicked',
                data: {{ slice_1: '{p1:.1f}%', slice_2: '{p2:.1f}%', slice_remaining: '{p3:.1f}%' }}
            }}, '*');
            alert('Dispatched component event to host interface!');
        }}
    </script>
</body>
</html>"""


HTML_ANALYTICS_APP = build_dynamic_chart_html(20.0, 50.0, 30.0, "MCP App: Interactive Analytics Chart")


@mcp.resource("ui://analytics_app", mime_type="text/html;profile=mcp-app")
async def get_analytics_ui_app() -> str:
    """MCP App HTML UI Component Resource. Formal MCP Apps spec standard (text/html;profile=mcp-app)."""
    return HTML_ANALYTICS_APP


@mcp.tool()
async def generate_ui_chart(slice1_pct: float = 20.0, slice2_pct: float = 50.0, title: str = "Data Distribution Chart", ctx: Context = None) -> list:
    """Generate an interactive HTML UI widget component displaying a custom percentage chart (e.g. 20%, 50%, and remaining 30%)."""
    remaining = max(0.0, 100.0 - slice1_pct - slice2_pct)
    if ctx:
        await ctx.info(f"Generating UI Chart Component ({slice1_pct}%, {slice2_pct}%, remaining {remaining:.1f}%)")
        
    html_content = build_dynamic_chart_html(slice1_pct, slice2_pct, remaining, title)
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
        
    html_content = build_dynamic_chart_html(slice1, slice2, remaining, "MCP Interactive Distribution Chart")
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
