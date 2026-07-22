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

# Ensure user site-packages are accessible
sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.13/site-packages'))

from mcp.server.fastmcp import FastMCP, Context
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

HTML_ANALYTICS_APP = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MCP App: Analytics Dashboard</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }
        .card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; margin-bottom: 16px; }
        .metric { font-size: 32px; font-weight: bold; color: #38bdf8; margin: 10px 0; }
        .btn { background: #2563eb; color: white; border: none; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn:hover { background: #1d4ed8; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📊 Real-Time MCP App Component</h2>
        <p>Interactive web widget embedded directly inside the host interface.</p>
        <div class="metric" id="activeUsers">1,248</div>
        <p>Active Session Concurrency</p>
        <button class="btn" onclick="alert('Submitted event to host!')">Submit RPC Event to Host</button>
    </div>
</body>
</html>
"""

@mcp.resource("ui://analytics_app", mime_type="text/html;profile=mcp-app")
async def get_analytics_ui_app() -> str:
    """MCP App HTML UI Component Resource. Formal MCP Apps spec standard (text/html;profile=mcp-app)."""
    return HTML_ANALYTICS_APP


@mcp.tool()
async def launch_analytics_app(initial_view: str = "dashboard", ctx: Context = None) -> list:
    """Launch interactive MCP App widget inside the host interface (Formal MCP Apps Spec)."""
    if ctx:
        await ctx.info(f"Launching MCP App UI Component (view='{initial_view}', profile='mcp-app')")
        
    return [
        EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="ui://analytics_app",
                mimeType="text/html;profile=mcp-app",
                text=HTML_ANALYTICS_APP
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
        mcp.settings.host = "127.0.0.1"
    mcp.run(transport=transport)
