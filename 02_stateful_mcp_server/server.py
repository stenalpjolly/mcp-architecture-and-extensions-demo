#!/usr/bin/env python3
"""Protocol Connection Stateful MCP Server Demo.

This server demonstrates Option 1: Protocol Connection & Session Statefulness.
It highlights native MCP protocol connection capabilities over an active session stream:
1. Connection Context & Session Tracking (Client ID, Request ID, Session Uptime).
2. Live Stream Connection Logging (ctx.info, ctx.warning).
3. Real-Time Progress Streaming (ctx.report_progress).
4. Dynamic Tool Mutation over Connection (notifications/tools/list_changed).
5. State persistence tied to active connection session lifecycle.
"""

import sys
import os
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp.server.lowlevel.server import NotificationOptions

# Initialize FastMCP Server with Connection Stateful Configuration
mcp = FastMCP("Protocol Connection Stateful MCP Server", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Enable stateful capability declarations in initialize response (tools_changed, resources_changed, prompts_changed)
_orig_init_options = mcp._mcp_server.create_initialization_options
def _custom_init_options(notification_options=None, experimental_capabilities=None):
    return _orig_init_options(
        notification_options=NotificationOptions(
            tools_changed=True,
            resources_changed=True,
            prompts_changed=True
        ),
        experimental_capabilities=experimental_capabilities
    )
mcp._mcp_server.create_initialization_options = _custom_init_options

DATA_FILE = os.path.join(os.path.dirname(__file__), "data_store.json")

# ==============================================================================
# CONNECTION SESSION & DATA STORE
# ==============================================================================

class ConnectionStateStore:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.session_start = datetime.now(timezone.utc).isoformat()
        self.total_tool_calls = 0
        self.admin_mode = False
        self.notes: Dict[str, dict] = {}
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.notes = data.get("notes", {})
                    self.total_tool_calls = data.get("total_tool_calls", 0)
            except Exception as e:
                print(f"[StateStore] Warning loading disk state: {e}", file=sys.stderr)

    def save_to_disk(self):
        data = {
            "session_start": self.session_start,
            "total_tool_calls": self.total_tool_calls,
            "admin_mode": self.admin_mode,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "notes": self.notes
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> dict:
        self.total_tool_calls += 1
        note_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc).isoformat()
        note = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": now,
            "updated_at": now
        }
        self.notes[note_id] = note
        self.save_to_disk()
        return note

    def get_notes(self) -> List[dict]:
        return list(self.notes.values())

    def clear(self):
        self.notes.clear()
        self.save_to_disk()


store = ConnectionStateStore(DATA_FILE)

# ==============================================================================
# PROTOCOL CONNECTION-AWARE TOOLS
# ==============================================================================

@mcp.tool()
async def create_note(title: str, content: str, tags: Optional[List[str]] = None, ctx: Context = None) -> dict:
    """Create a note with real-time connection log notifications."""
    if ctx:
        await ctx.info(f"⚡ Connection Event: Creating note '{title}'...")
    
    note = store.add_note(title=title, content=content, tags=tags)
    
    if ctx:
        await ctx.info(f"✅ Note created successfully with ID: {note['id']}")
    return note


@mcp.tool()
async def bulk_import_sample_notes(count: int = 3, ctx: Context = None) -> dict:
    """Demonstrates real-time progress streaming over active protocol connection."""
    if ctx:
        await ctx.info(f"🚀 Starting bulk import of {count} notes over connection stream...")
    
    imported = []
    for i in range(1, count + 1):
        # Simulate processing work
        await asyncio.sleep(0.1)
        
        note = store.add_note(
            title=f"Sample Note #{i}",
            content=f"Automatically generated sample note content for item {i}.",
            tags=["sample", "bulk-import"]
        )
        imported.append(note)
        
        if ctx:
            # Stream real-time progress notification (i out of count)
            await ctx.report_progress(i, count)
            await ctx.info(f"  [Progress {i}/{count}] Note '{note['id']}' imported.")
            
    return {"status": "Complete", "imported_count": len(imported), "notes": imported}


@mcp.tool()
async def toggle_admin_mode(enable: bool, ctx: Context = None) -> dict:
    """Dynamically register/enable tools over the active MCP protocol session connection."""
    store.admin_mode = enable
    
    if ctx:
        await ctx.info(f"⚙️ Connection state change: Admin Mode set to {enable}")
    
    if enable:
        # Dynamically register admin tool during connection session
        @mcp.tool(name="admin_system_diagnostics")
        async def admin_system_diagnostics(ctx_inner: Context = None) -> dict:
            """Admin-only tool dynamically enabled during active connection session."""
            if ctx_inner:
                await ctx_inner.info("Executing privileged system diagnostics over connection...")
            return {
                "status": "Healthy",
                "session_start": store.session_start,
                "total_tool_calls": store.total_tool_calls,
                "active_notes_count": len(store.notes),
                "admin_mode": True
            }
            
        if ctx:
            await ctx.info("✨ Dynamically registered tool 'admin_system_diagnostics' into session!")
    else:
        try:
            mcp.remove_tool("admin_system_diagnostics")
            if ctx:
                await ctx.info("❌ Removed tool 'admin_system_diagnostics' from session.")
        except Exception:
            pass
            
    return {"admin_mode": store.admin_mode, "status": f"Admin tools {'enabled' if enable else 'disabled'}"}


@mcp.tool()
async def clear_notes(ctx: Context = None) -> dict:
    """Clear all notes from connection state store."""
    if ctx:
        await ctx.info("🧹 Clearing all notes from connection state store...")
    store.clear()
    return {"status": "State cleared"}


@mcp.tool()
async def get_connection_session_info(ctx: Context = None) -> dict:
    """Inspect active MCP connection session parameters and metadata."""
    client_id = (ctx.client_id if (ctx and ctx.client_id) else "demo_authenticated_client_host")
    req_id = (ctx.request_id if ctx else "unknown")
    
    if ctx:
        await ctx.info(f"Inspecting session context for client '{client_id}', request '{req_id}'")
        
    return {
        "client_id": client_id,
        "request_id": req_id,
        "session_start": store.session_start,
        "admin_mode": store.admin_mode,
        "total_tool_calls": store.total_tool_calls,
        "total_notes": len(store.notes)
    }

# ==============================================================================
# RESOURCES (Connection State Resources)
# ==============================================================================

@mcp.resource("notes://all")
def get_all_notes_resource() -> str:
    """Dynamic resource reflecting connection state."""
    return json.dumps({
        "resource_type": "Connection Active Notes",
        "count": len(store.notes),
        "notes": store.get_notes()
    }, indent=2)


@mcp.resource("session://info")
def get_session_info_resource() -> str:
    """Dynamic resource reflecting protocol connection state metadata."""
    return json.dumps({
        "session_start": store.session_start,
        "admin_mode": store.admin_mode,
        "total_tool_calls": store.total_tool_calls,
        "total_notes": len(store.notes)
    }, indent=2)


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
