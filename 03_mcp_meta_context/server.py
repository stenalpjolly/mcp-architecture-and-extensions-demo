#!/usr/bin/env python3
"""MCP Server with Request Metadata (_meta) Context Processing.

This server demonstrates how MCP handlers inspect out-of-band request metadata (`_meta`).
In Model Context Protocol, the `_meta` reserved parameter allows host clients to inject:
1. Client & User Identification (`client_id`, `user_id`)
2. Multi-tenant isolation (`tenant_id`)
3. Distributed tracing & telemetry (`trace_id`)
4. Session authorization tokens (`auth_token`)

Without polluting the functional argument schema (`inputSchema`) of tools and resources!
"""

import sys
import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp.server.lowlevel.server import NotificationOptions

# Initialize FastMCP Server with Request Metadata Configuration
mcp = FastMCP("Request Metadata (_meta) MCP Server", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Enable notification capabilities in initialization options
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


# Simulated Multi-Tenant Database Store
TENANT_DATABASE: Dict[str, Dict[str, Any]] = {
    "tenant_acme_corp": {
        "company": "Acme Corporation",
        "region": "us-east-1",
        "records": ["Invoice #1001", "Purchase Order #4402", "Contract #9901"]
    },
    "tenant_globex_inc": {
        "company": "Globex Inc",
        "region": "eu-west-1",
        "records": ["GDPR Consent #7701", "EU Order #2204"]
    }
}

# In-Memory Audit Trace Log Store
AUDIT_LOGS = []


# Helper function to extract _meta dictionary from Context
def extract_meta(ctx: Context) -> Dict[str, Any]:
    """Helper function to extract raw _meta parameters from Context."""
    if not ctx or not ctx.request_context or not ctx.request_context.meta:
        return {}
    meta_obj = ctx.request_context.meta
    if hasattr(meta_obj, "model_dump"):
        return meta_obj.model_dump(exclude_none=True)
    elif isinstance(meta_obj, dict):
        return meta_obj
    return {}


# ==============================================================================
# TOOLS (Inspecting _meta Metadata)
# ==============================================================================

@mcp.tool()
async def get_user_profile(include_security_groups: bool = False, ctx: Context = None) -> dict:
    """Retrieve user profile. Uses _meta to extract caller identity without exposing auth parameters in tool schema."""
    meta = extract_meta(ctx)
    
    client_id = ctx.client_id if (ctx and ctx.client_id) else meta.get("client_id", "anonymous_client")
    user_id = meta.get("user_id", "guest_user")
    tenant_id = meta.get("tenant_id", "default_tenant")
    trace_id = meta.get("trace_id", str(uuid.uuid4())[:8])
    auth_token = meta.get("auth_token", "None")
    
    if ctx:
        await ctx.info(f"[_meta Trace {trace_id}] Accessing profile for user '{user_id}' on tenant '{tenant_id}'")

    # Record audit log trace
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "client_id": client_id,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "action": "get_user_profile"
    }
    AUDIT_LOGS.append(log_entry)

    return {
        "user_id": user_id,
        "client_id": client_id,
        "tenant_id": tenant_id,
        "trace_id": trace_id,
        "auth_verified": auth_token != "None",
        "profile": {
            "name": f"User {user_id}",
            "role": "Senior Engineer" if "admin" in user_id or "stenalp" in user_id else "Member",
            "security_groups": ["devs", "mcp-operators", "sys-admins"] if include_security_groups else ["devs"]
        }
    }


@mcp.tool()
async def execute_tenant_query(query_category: str, ctx: Context = None) -> dict:
    """Execute query against isolated tenant database. Tenant context is enforced via _meta.tenant_id."""
    meta = extract_meta(ctx)
    tenant_id = meta.get("tenant_id")
    trace_id = meta.get("trace_id", str(uuid.uuid4())[:8])
    
    if not tenant_id:
        if ctx:
            await ctx.info(f"[_meta Trace {trace_id}] Access denied: Missing _meta.tenant_id parameter")
        return {"error": "Access Denied: Missing _meta.tenant_id parameter in request payload."}

    if tenant_id not in TENANT_DATABASE:
        return {"error": f"Invalid tenant_id '{tenant_id}'."}

    tenant_data = TENANT_DATABASE[tenant_id]
    
    if ctx:
        await ctx.info(f"[_meta Trace {trace_id}] Executed tenant query for '{tenant_data['company']}'")

    # Record audit log trace
    AUDIT_LOGS.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "tenant_id": tenant_id,
        "action": "execute_tenant_query",
        "category": query_category
    })

    return {
        "tenant_id": tenant_id,
        "trace_id": trace_id,
        "company": tenant_data["company"],
        "region": tenant_data["region"],
        "records_count": len(tenant_data["records"]),
        "records": tenant_data["records"]
    }


@mcp.tool()
async def audit_system_access(action_name: str, ctx: Context = None) -> dict:
    """Record administrative audit trail entry using caller's _meta tracing headers."""
    meta = extract_meta(ctx)
    trace_id = meta.get("trace_id", str(uuid.uuid4())[:8])
    client_id = ctx.client_id if (ctx and ctx.client_id) else meta.get("client_id", "unknown")
    user_id = meta.get("user_id", "unknown")
    
    if ctx:
        await ctx.info(f"[_meta Trace {trace_id}] Audit logged: Action '{action_name}' by user '{user_id}'")

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "client_id": client_id,
        "user_id": user_id,
        "action": action_name,
        "status": "LOGGED"
    }
    AUDIT_LOGS.append(entry)
    
    return entry


# ==============================================================================
# RESOURCES (Inspecting _meta in URI evaluations)
# ==============================================================================

@mcp.resource("audit://access_logs")
async def get_audit_logs_resource() -> str:
    """Read-only resource returning system audit logs generated by _meta traced requests."""
    return json.dumps({
        "resource": "audit://access_logs",
        "total_events": len(AUDIT_LOGS),
        "events": AUDIT_LOGS
    }, indent=2)


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
