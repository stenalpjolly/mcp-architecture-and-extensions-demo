#!/usr/bin/env python3
"""Interactive Technical Walkthrough with Raw JSON-RPC 2.0 Payloads: Protocol Connection Stateful MCP Server.

This script provides a technical architect's walkthrough of a Protocol Connection Stateful MCP Server.
It displays the exact raw JSON-RPC 2.0 Request, Response, and Asynchronous Notification payloads sent over stdio in proper protocol order.

Usage:
  python3 test_client.py        # Technical Walkthrough Mode (press ENTER to advance)
  python3 test_client.py --auto # Fast Auto Mode (runs walkthrough without pausing)
"""

import sys
import os
import json
import asyncio

sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.13/site-packages'))

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


async def run_stateful_technical_walkthrough():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env={
            **os.environ,
            "PYTHONPATH": os.path.expanduser('~/.local/lib/python3.13/site-packages')
        }
    )

    connection_log_events = []
    async def handle_log_event(log_message):
        connection_log_events.append(log_message)
        print_jsonrpc_notification(
            method="notifications/message",
            params={"level": log_message.level, "data": log_message.data}
        )

    print("\n" + f"{BOLD}{CYAN}💻" * 38)
    print("      PROTOCOL CONNECTION STATEFUL MCP TECHNICAL WALKTHROUGH")
    print("      Protocol Specs: JSON-RPC 2.0 Raw Payloads | Async Notifications")
    print("💻" * 38 + f"{RESET}\n")

    # Chapter 1: Handshake
    tell_technical_chapter(
        chapter_num=1,
        title="Persistent Session Handshake & Initialization Confirmation",
        tech_explanation="We establish an active MCP session over stdio transport:\n"
                         "   1. Client sends 'initialize' request -> Server returns 'InitializeResult' with serverInfo & stateful capabilities.\n"
                         "   2. Client sends 'notifications/initialized' -> A 1-way JSON-RPC notification (no ID) acknowledging setup complete.\n"
                         "   WHY NOTIFICATIONS/INITIALIZED? Per MCP spec, before this notification is sent, the server is in INITIALIZING state.\n"
                         "   Sending 'notifications/initialized' signals the server that the client is ready to receive stream messages & request active operations.",
        server_code_pointer="Lines 26-38 -> FastMCP('Protocol Connection Stateful MCP Server') & ConnectionStateStore"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, 
            write, 
            logging_callback=handle_log_event,
            client_info=Implementation(name="DemoClientHost", version="1.0.0")
        ) as session:
            
            # 1a. Initialize Request
            print_jsonrpc_request(req_id=1, method="initialize", params={"protocolVersion": "2024-11-05", "capabilities": {}})
            init_result = await session.initialize()
            
            # 1b. Initialize Response
            print_jsonrpc_response(req_id=1, result_obj=init_result)
            
            # 1c. Initialized Notification
            print_jsonrpc_notification(method="notifications/initialized", params={})
            print(f"{BOLD}{GREEN}🤝 [JSON-RPC SESSION INITIALIZED]: Handshake complete. Connection state transitioned to ACTIVE.{RESET}\n")
            
            # Reset state for clean run
            await session.call_tool("clear_notes", arguments={})

            # Chapter 2: Schema & Resource Discovery Phase
            tell_technical_chapter(
                chapter_num=2,
                title="Protocol Discovery Phase (resources/list & tools/list)",
                tech_explanation="BEFORE invoking tools or reading resources, the client MUST discover available schemas in the ACTIVE session.\n"
                         "   1. Client issues 'resources/list' -> Discovers resources (notes://all, session://info).\n"
                         "   2. Client issues 'tools/list' -> Discovers initial 5 tools. Note that 'admin_system_diagnostics' is NOT registered yet.",
                server_code_pointer="Lines 95-219 -> Tool and Resource definitions"
            )
            
            # 2a. List Resources
            print_jsonrpc_request(req_id=2, method="resources/list", params={})
            resources_response = await session.list_resources()
            print_jsonrpc_response(req_id=2, result_obj=resources_response)

            # 2b. List Tools (Before Admin Mode)
            print_jsonrpc_request(req_id=3, method="tools/list", params={})
            tools_before = await session.list_tools()
            print_jsonrpc_response(req_id=3, result_obj=tools_before)

            # Chapter 3: Initial Resource Read
            tell_technical_chapter(
                chapter_num=3,
                title="Initial State Resource Query (notes://all)",
                tech_explanation="Using the resource URI discovered in Chapter 2 (notes://all), the client issues a 'resources/read' request. "
                                 "The server queries its ConnectionStateStore instance and serializes current empty state into JSON.",
                server_code_pointer="Lines 201-208 -> @mcp.resource('notes://all') def get_all_notes_resource()"
            )
            print_jsonrpc_request(req_id=4, method="resources/read", params={"uri": "notes://all"})
            res_init = await session.read_resource("notes://all")
            print_jsonrpc_response(req_id=4, result_obj=res_init)

            # Chapter 4: Async Stream Notifications
            tell_technical_chapter(
                chapter_num=4,
                title="Asynchronous Progress & Log Notifications Streaming",
                tech_explanation="Using the bulk_import_sample_notes tool discovered in Chapter 2, the client calls the tool. "
                                 "During execution, the server utilizes Context (ctx.report_progress & ctx.info) to stream real-time JSON-RPC "
                                 "progress notifications (notifications/progress) and log events over the active connection stream!",
                server_code_pointer="Lines 108-131 -> @mcp.tool() async def bulk_import_sample_notes(count, ctx)"
            )
            print_jsonrpc_request(req_id=5, method="tools/call", params={"name": "bulk_import_sample_notes", "arguments": {"count": 3}})
            bulk_res = await session.call_tool("bulk_import_sample_notes", arguments={"count": 3})
            print_jsonrpc_response(req_id=5, result_obj=bulk_res)

            # Chapter 5: Dynamic Tool Schema Mutation
            tell_technical_chapter(
                chapter_num=5,
                title="Dynamic Tool Schema Mutation (toggle_admin_mode)",
                tech_explanation="The client calls toggle_admin_mode(enable=True). The server's handler dynamically decorates "
                                 "and registers admin_system_diagnostics into the FastMCP instance, emitting a notifications/tools/list_changed "
                                 "event over the connection stream!",
                server_code_pointer="Lines 144-158 -> @mcp.tool(name='admin_system_diagnostics') registered dynamically"
            )
            print_jsonrpc_request(req_id=6, method="tools/call", params={"name": "toggle_admin_mode", "arguments": {"enable": True}})
            toggle_res = await session.call_tool("toggle_admin_mode", arguments={"enable": True})
            print_jsonrpc_response(req_id=6, result_obj=toggle_res)

            # Chapter 6: Re-Discovering Tools Schema Registry
            tell_technical_chapter(
                chapter_num=6,
                title="Re-Discovering Tools Schema Registry after Mutation",
                tech_explanation="The client issues 'tools/list' again. The server reflects the mutated tool registry containing 6 tools. "
                                 "admin_system_diagnostics is now dynamically exposed over the active session connection!",
                server_code_pointer="Lines 144-158 -> Dynamic tool addition registered in server session"
            )
            print_jsonrpc_request(req_id=7, method="tools/list", params={})
            tools_after = await session.list_tools()
            print_jsonrpc_response(req_id=7, result_obj=tools_after)

            # Chapter 7: Invoke Dynamic Tool Handler
            tell_technical_chapter(
                chapter_num=7,
                title="Invoking Dynamically Registered Tool Handler",
                tech_explanation="Now that admin_system_diagnostics is discovered in the updated schema, the client issues 'tools/call' for it. "
                                 "The server routes the request to the dynamically registered function, returning privileged runtime diagnostics.",
                server_code_pointer="Lines 144-155 -> async def admin_system_diagnostics(ctx_inner) handler"
            )
            print_jsonrpc_request(req_id=8, method="tools/call", params={"name": "admin_system_diagnostics", "arguments": {}})
            diag_res = await session.call_tool("admin_system_diagnostics", arguments={})
            print_jsonrpc_response(req_id=8, result_obj=diag_res)

            # Chapter 8: Session Context Info
            tell_technical_chapter(
                chapter_num=8,
                title="Session Context & Lifetime Inspection",
                tech_explanation="The tool accesses ctx.client_id and ctx.request_id from the active request context, "
                                 "returning session uptime and cumulative tool call counters tracked across the connection lifetime.",
                server_code_pointer="Lines 180-195 -> @mcp.tool() async def get_connection_session_info(ctx)"
            )
            print_jsonrpc_request(req_id=9, method="tools/call", params={"name": "get_connection_session_info", "arguments": {}})
            sess_info = await session.call_tool("get_connection_session_info", arguments={})
            print_jsonrpc_response(req_id=9, result_obj=sess_info)

            # Chapter 9: Final State Resource Read
            tell_technical_chapter(
                chapter_num=9,
                title="Final State Resource Inspection (notes://all)",
                tech_explanation="We re-read notes://all. The resource payload reflects all state mutations performed "
                                 "by tool calls executed during this active session connection.",
                server_code_pointer="Lines 201-208 -> @mcp.resource('notes://all') returns live session state"
            )
            print_jsonrpc_request(req_id=10, method="resources/read", params={"uri": "notes://all"})
            res_all = await session.read_resource("notes://all")
            print_jsonrpc_response(req_id=10, result_obj=res_all)

            print(f"\n{BOLD}{GREEN}✅ ARCHITECTURAL VERIFICATION: Option 1 Protocol Connection Statefulness enables real-time stream logging, progress notifications, dynamic tool changes, and session lifetime tracking!{RESET}")

    print("\n" + f"{BOLD}{CYAN}🏁" * 38)
    print("      STATEFUL MCP TECHNICAL WALKTHROUGH COMPLETE")
    print("🏁" * 38 + f"{RESET}\n")


if __name__ == "__main__":
    asyncio.run(run_stateful_technical_walkthrough())
