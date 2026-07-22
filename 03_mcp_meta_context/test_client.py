#!/usr/bin/env python3
"""Interactive Technical Walkthrough with Raw JSON-RPC 2.0 Payloads: MCP Request Metadata (_meta).

This script provides a technical architect's walkthrough of MCP Request Metadata (_meta).
It displays how host clients pass out-of-band metadata (_meta) inside JSON-RPC request params for:
- User & Client Authentication (`client_id`, `user_id`, `auth_token`)
- Multi-Tenant Data Isolation (`tenant_id`)
- Distributed Tracing & Correlation (`trace_id`)

Usage:
  python3 test_client.py        # Technical Walkthrough Mode (press ENTER to advance)
  python3 test_client.py --auto # Fast Auto Mode (runs walkthrough without pausing)
"""

import sys
import os
import json
import asyncio

import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp import ClientSession, StdioServerParameters
from mcp.types import Implementation
from mcp.client.stdio import stdio_client

AUTO_MODE = "--auto" in sys.argv or "-y" in sys.argv

# ==============================================================================
# ANSI COLOR TERMINAL PALETTE
# ==============================================================================
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[96m"       # Bright Cyan for Requests
GREEN = "\033[92m"      # Bright Green for Responses
YELLOW = "\033[93m"     # Bright Yellow for Technical Architect
MAGENTA = "\033[95m"    # Bright Magenta for Code Pointers & Highlights
BLUE = "\033[94m"       # Bright Blue for Chapter Headers
WHITE_BOLD = "\033[1;97m"
GRAY = "\033[90m"       # Gray for separators


def print_jsonrpc_request(req_id: int, method: str, params: dict = None):
    """Formats and prints raw JSON-RPC 2.0 request payload in Cyan."""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method
    }
    if params is not None:
        payload["params"] = params
    
    print(f"{BOLD}{CYAN}📤 [RAW JSON-RPC 2.0 REQUEST PAYLOAD]:{RESET}")
    print(f"{CYAN}{json.dumps(payload, indent=2)}{RESET}\n")


def print_jsonrpc_response(req_id: int, result_obj):
    """Formats and prints raw JSON-RPC 2.0 response payload in Green."""
    if hasattr(result_obj, "model_dump"):
        res_dict = result_obj.model_dump(exclude_none=True)
    else:
        res_dict = result_obj
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": res_dict
    }
    print(f"{BOLD}{GREEN}📥 [RAW JSON-RPC 2.0 RESPONSE PAYLOAD]:{RESET}")
    print(f"{GREEN}{json.dumps(payload, indent=2, default=str)}{RESET}\n")


def print_jsonrpc_notification(method: str, params: dict = None):
    """Formats and prints raw JSON-RPC 2.0 notification payload in Magenta."""
    payload = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params is not None:
        payload["params"] = params
    print(f"{BOLD}{MAGENTA}📡 [RAW JSON-RPC 2.0 ASYNC NOTIFICATION STREAM]:{RESET}")
    print(f"{MAGENTA}{json.dumps(payload, indent=2)}{RESET}\n")


def tell_technical_chapter(chapter_num: int, title: str, tech_explanation: str, server_code_pointer: str):
    """Prints a technical chapter header with architectural explanation and server.py pointers."""
    print(f"{GRAY}{'=' * 75}{RESET}")
    print(f"{BOLD}{BLUE}⚙️ CHAPTER {chapter_num}: {title}{RESET}")
    print(f"{GRAY}{'=' * 75}{RESET}")
    print(f"{BOLD}{YELLOW}👨‍💻 TECHNICAL ARCHITECT:{RESET} {YELLOW}{tech_explanation}{RESET}")
    print(f"{BOLD}{MAGENTA}📍 [SERVER CODE POINTER]:{RESET} {MAGENTA}server.py ({server_code_pointer}){RESET}")
    print(f"{GRAY}{'─' * 75}{RESET}")
    if not AUTO_MODE:
        try:
            input(f"\n{BOLD}{WHITE_BOLD}▶️ Press [ENTER] to execute RPC step...{RESET}")
        except (KeyboardInterrupt, EOFError):
            print("\nWalkthrough ended.")
            sys.exit(0)
    print()


async def run_meta_context_walkthrough():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    
    env = {**os.environ}
    if user_site:
        env["PYTHONPATH"] = f"{user_site}:{os.environ.get('PYTHONPATH', '')}".strip(":")
        
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=env
    )

    async def handle_log_event(log_message):
        print_jsonrpc_notification(
            method="notifications/message",
            params={"level": log_message.level, "data": log_message.data}
        )

    print("\n" + f"{BOLD}{CYAN}💻" * 38)
    print("      MCP REQUEST METADATA (_meta) ARCHITECTURE WALKTHROUGH")
    print("      Protocol Specs: JSON-RPC 2.0 Out-of-Band _meta Parameters")
    print("💻" * 38 + f"{RESET}\n")

    # Chapter 1: Handshake
    tell_technical_chapter(
        chapter_num=1,
        title="Session Handshake & Host Identification",
        tech_explanation="We initiate the stdio session. Client host passes clientInfo (name='DemoClientHost', version='1.0.0') "
                         "in the initialize request payload.",
        server_code_pointer="Lines 21-39 -> FastMCP server initialization & capability setup"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, 
            write, 
            logging_callback=handle_log_event,
            client_info=Implementation(name="DemoClientHost", version="1.0.0")
        ) as session:
            
            # 1a. Initialize Request
            print_jsonrpc_request(req_id=1, method="initialize", params={"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "DemoClientHost", "version": "1.0.0"}})
            init_result = await session.initialize()
            print_jsonrpc_response(req_id=1, result_obj=init_result)
            print_jsonrpc_notification(method="notifications/initialized", params={})

            # Chapter 2: Schema Discovery
            tell_technical_chapter(
                chapter_num=2,
                title="Protocol Discovery Phase (tools/list & resources/list)",
                tech_explanation="The client issues 'tools/list' and 'resources/list'. Notice how the tool input schema (inputSchema) "
                                 "ONLY defines functional arguments (e.g. include_security_groups). Out-of-band metadata like credentials "
                                 "or trace IDs are NOT included in the public schema!",
                server_code_pointer="Lines 60-145 -> @mcp.tool() function signatures"
            )
            print_jsonrpc_request(req_id=2, method="resources/list", params={})
            res_list = await session.list_resources()
            print_jsonrpc_response(req_id=2, result_obj=res_list)

            print_jsonrpc_request(req_id=3, method="tools/list", params={})
            tools_list = await session.list_tools()
            print_jsonrpc_response(req_id=3, result_obj=tools_list)

            # Chapter 3: Injecting _meta for Caller Authentication
            tell_technical_chapter(
                chapter_num=3,
                title="Injecting Out-of-Band _meta for Caller Authentication",
                tech_explanation="The client issues 'tools/call' for get_user_profile. In the JSON-RPC request, "
                                 "the client passes `_meta`: { `client_id`, `user_id`, `auth_token`, `trace_id` } in params.\n"
                                 "The tool handler accesses `ctx.client_id` and `ctx.request_context.meta` to authenticate the user "
                                 "without requiring auth parameters in the tool's inputSchema!",
                server_code_pointer="Lines 60-90 -> get_user_profile uses extract_meta(ctx)"
            )
            
            meta_payload_1 = {
                "client_id": "client_acme_corp_88",
                "user_id": "usr_stenalp_42",
                "tenant_id": "tenant_acme_corp",
                "trace_id": "tr_sec_9901a",
                "auth_token": "bearer_sec_token_xyz123"
            }
            
            print_jsonrpc_request(
                req_id=4,
                method="tools/call",
                params={
                    "name": "get_user_profile",
                    "arguments": {"include_security_groups": True},
                    "_meta": meta_payload_1
                }
            )
            res_profile = await session.call_tool(
                "get_user_profile",
                arguments={"include_security_groups": True},
                meta=meta_payload_1
            )
            print_jsonrpc_response(req_id=4, result_obj=res_profile)

            # Chapter 4: Multi-Tenant Data Isolation via _meta.tenant_id
            tell_technical_chapter(
                chapter_num=4,
                title="Multi-Tenant Data Isolation via _meta.tenant_id",
                tech_explanation="In multi-tenant SaaS environments, tenant context MUST NOT be forged by the caller's tool arguments. "
                                 "Instead, the host client injects verified `_meta.tenant_id` ('tenant_acme_corp'). The server handler "
                                 "enforces database tenant isolation automatically based on `_meta`!",
                server_code_pointer="Lines 95-125 -> execute_tenant_query validates meta.get('tenant_id')"
            )
            
            meta_payload_2 = {
                "client_id": "client_acme_corp_88",
                "tenant_id": "tenant_acme_corp",
                "trace_id": "tr_db_4402b"
            }
            
            print_jsonrpc_request(
                req_id=5,
                method="tools/call",
                params={
                    "name": "execute_tenant_query",
                    "arguments": {"query_category": "invoices"},
                    "_meta": meta_payload_2
                }
            )
            res_tenant = await session.call_tool(
                "execute_tenant_query",
                arguments={"query_category": "invoices"},
                meta=meta_payload_2
            )
            print_jsonrpc_response(req_id=5, result_obj=res_tenant)

            # Chapter 5: Distributed Tracing & Telemetry via _meta.trace_id
            tell_technical_chapter(
                chapter_num=5,
                title="Distributed Tracing & Correlation via _meta.trace_id",
                tech_explanation="The client invokes audit_system_access passing a unique `_meta.trace_id` ('tr_span_7701c'). "
                                 "The server streams real-time notifications tagged with `[_meta Trace tr_span_7701c]`, enabling "
                                 "end-to-end distributed tracing across microservice boundaries!",
                server_code_pointer="Lines 130-145 -> audit_system_access correlates trace_id"
            )

            meta_payload_3 = {
                "client_id": "client_globex_inc_12",
                "user_id": "usr_admin_007",
                "tenant_id": "tenant_globex_inc",
                "trace_id": "tr_span_7701c"
            }
            
            print_jsonrpc_request(
                req_id=6,
                method="tools/call",
                params={
                    "name": "audit_system_access",
                    "arguments": {"action_name": "EXPORTS_EU_GDPR_LOGS"},
                    "_meta": meta_payload_3
                }
            )
            res_audit = await session.call_tool(
                "audit_system_access",
                arguments={"action_name": "EXPORTS_EU_GDPR_LOGS"},
                meta=meta_payload_3
            )
            print_jsonrpc_response(req_id=6, result_obj=res_audit)

            # Chapter 6: Reading Traced Resource State
            tell_technical_chapter(
                chapter_num=6,
                title="Inspecting Resource State Built from _meta Traces",
                tech_explanation="We read resource audit://access_logs. The resource payload reflects all audit entries "
                                 "tagged with their corresponding _meta client_id, user_id, tenant_id, and trace_id headers.",
                server_code_pointer="Lines 150-158 -> @mcp.resource('audit://access_logs') returns trace logs"
            )
            print_jsonrpc_request(req_id=7, method="resources/read", params={"uri": "audit://access_logs"})
            res_logs = await session.read_resource("audit://access_logs")
            print_jsonrpc_response(req_id=7, result_obj=res_logs)

            print(f"\n{BOLD}{GREEN}✅ ARCHITECTURAL VERIFICATION: MCP _meta parameters enable secure out-of-band authentication, multi-tenant isolation, and distributed tracing!{RESET}")

    print("\n" + f"{BOLD}{CYAN}🏁" * 38)
    print("      MCP REQUEST METADATA (_meta) TECHNICAL WALKTHROUGH COMPLETE")
    print("🏁" * 38 + f"{RESET}\n")


if __name__ == "__main__":
    asyncio.run(run_meta_context_walkthrough())
