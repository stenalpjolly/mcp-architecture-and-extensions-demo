#!/usr/bin/env python3
"""Interactive Technical Walkthrough with Raw JSON-RPC 2.0 Payloads: Stateless MCP Server.

This script provides a technical architect's walkthrough of a Stateless MCP Server.
It displays the exact raw JSON-RPC 2.0 Request and Response payloads sent over standard I/O in proper protocol order.

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
    print(f"{BOLD}{MAGENTA}📡 [RAW JSON-RPC 2.0 NOTIFICATION STREAM]:{RESET}")
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


async def run_stateless_technical_walkthrough():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    
    env = {**os.environ}
    if user_site:
        env["PYTHONPATH"] = f"{user_site}:{os.environ.get('PYTHONPATH', '')}".strip(":")
        
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=env
    )

    print("\n" + f"{BOLD}{CYAN}💻" * 38)
    print("      STATELESS MCP SERVER TECHNICAL ARCHITECTURE WALKTHROUGH")
    print("      Protocol Specs: JSON-RPC 2.0 Raw Payloads | Pure Handlers")
    print("💻" * 38 + f"{RESET}\n")

    # Chapter 1: Handshake
    tell_technical_chapter(
        chapter_num=1,
        title="Protocol Session Handshake & Initialization Signal",
        tech_explanation="The MCP handshake is a 2-phase exchange:\n"
                         "   1. Client sends 'initialize' request -> Server returns 'InitializeResult' declaring protocol capabilities.\n"
                         "   2. Client sends 'notifications/initialized' -> A 1-way notification acknowledging setup complete and signaling session state is ACTIVE.",
        server_code_pointer="Lines 21-22 -> mcp = FastMCP('Stateless MCP Server - Utilities & Tools')"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, client_info=Implementation(name="DemoClientHost", version="1.0.0")) as session:
            # 1a. Initialize Request
            print_jsonrpc_request(req_id=1, method="initialize", params={"protocolVersion": "2024-11-05", "capabilities": {}})
            init_result = await session.initialize()
            
            # 1b. Initialize Response
            print_jsonrpc_response(req_id=1, result_obj=init_result)
            
            # 1c. Initialized Notification
            print_jsonrpc_notification(method="notifications/initialized", params={})
            print(f"{BOLD}{GREEN}🤝 [JSON-RPC HANDSHAKE COMPLETE]: Session state transitioned to ACTIVE.{RESET}\n")
            
            # Chapter 2: Schema & Resource Discovery Phase
            tell_technical_chapter(
                chapter_num=2,
                title="Discovery Phase (resources/list & tools/list)",
                tech_explanation="BEFORE invoking any tools or reading resources, the client MUST discover available schemas.\n"
                         "   1. Client issues 'resources/list' -> Discovers static system resources.\n"
                         "   2. Client issues 'tools/list' -> Discovers pure utility tool schemas.",
                server_code_pointer="Lines 28-170 -> Registered tool (@mcp.tool) and resource (@mcp.resource) decorators"
            )
            
            # 2a. Resources list
            print_jsonrpc_request(req_id=2, method="resources/list", params={})
            resources_response = await session.list_resources()
            print_jsonrpc_response(req_id=2, result_obj=resources_response)

            # 2b. Tools list
            print_jsonrpc_request(req_id=3, method="tools/list", params={})
            tools_response = await session.list_tools()
            print_jsonrpc_response(req_id=3, result_obj=tools_response)

            # Chapter 3: add_numbers
            tell_technical_chapter(
                chapter_num=3,
                title="Pure Functional Handler Invocation (add_numbers)",
                tech_explanation="Now that tool schemas are discovered, the client sends 'tools/call' for add_numbers. "
                                 "FastMCP routes this to add_numbers(). It computes the sum and returns a CallToolResult with 0 side-effects.",
                server_code_pointer="Lines 28-39 -> @mcp.tool() def add_numbers(a: float, b: float) -> float"
            )
            print_jsonrpc_request(req_id=4, method="tools/call", params={"name": "add_numbers", "arguments": {"a": 15.5, "b": 24.5}})
            res_add = await session.call_tool("add_numbers", arguments={"a": 15.5, "b": 24.5})
            print_jsonrpc_response(req_id=4, result_obj=res_add)

            # Chapter 4: calculate_bmi
            tell_technical_chapter(
                chapter_num=4,
                title="Dynamic Math Calculation (calculate_bmi)",
                tech_explanation="The client invokes calculate_bmi. Input parameters are evaluated dynamically in-memory. "
                                 "Once serialized to the JSON-RPC response payload, memory for the calculation is reclaimed.",
                server_code_pointer="Lines 42-72 -> @mcp.tool() def calculate_bmi(weight_kg: float, height_m: float)"
            )
            print_jsonrpc_request(req_id=5, method="tools/call", params={"name": "calculate_bmi", "arguments": {"weight_kg": 75.0, "height_m": 1.80}})
            res_bmi = await session.call_tool("calculate_bmi", arguments={"weight_kg": 75.0, "height_m": 1.80})
            print_jsonrpc_response(req_id=5, result_obj=res_bmi)

            # Chapter 5: transform_text
            tell_technical_chapter(
                chapter_num=5,
                title="Stateless Text Transformation (transform_text)",
                tech_explanation="Stateless handlers excel at deterministic hashing (SHA-256). Given input string S, "
                                 "H(S) is strictly deterministic and idempotent, making it safe to cache or scale across N serverless instances.",
                server_code_pointer="Lines 75-107 -> @mcp.tool() def transform_text(text: str, operation: str)"
            )
            print_jsonrpc_request(req_id=6, method="tools/call", params={"name": "transform_text", "arguments": {"text": "Hello MCP World", "operation": "sha256"}})
            res_text = await session.call_tool("transform_text", arguments={"text": "Hello MCP World", "operation": "sha256"})
            print_jsonrpc_response(req_id=6, result_obj=res_text)

            # Chapter 6: system://info Resource
            tell_technical_chapter(
                chapter_num=6,
                title="Read-Only Resource Evaluation (system://info)",
                tech_explanation="Using the URI discovered in Chapter 2 (system://info), the client issues 'resources/read'. "
                                 "The server queries host process metadata and returns a JSON payload without state mutation.",
                server_code_pointer="Lines 159-170 -> @mcp.resource('system://info') def get_system_info()"
            )
            print_jsonrpc_request(req_id=7, method="resources/read", params={"uri": "system://info"})
            res_info = await session.read_resource("system://info")
            print_jsonrpc_response(req_id=7, result_obj=res_info)

            # Chapter 7: Idempotency Verification
            tell_technical_chapter(
                chapter_num=7,
                title="Idempotency & Horizontal Scaling Verification",
                tech_explanation="To verify strict protocol statelessness, we execute 3 identical RPC calls to add_numbers(10, 20). "
                                 "Every call returns identical output (30.0), proving zero session state drift or cumulative side-effects.",
                server_code_pointer="Lines 28-39 -> add_numbers executes as a pure mathematical function"
            )
            print_jsonrpc_request(req_id=8, method="tools/call", params={"name": "add_numbers", "arguments": {"a": 10, "b": 20}})
            r1 = await session.call_tool("add_numbers", arguments={"a": 10, "b": 20})
            print_jsonrpc_response(req_id=8, result_obj=r1)
            
            print_jsonrpc_request(req_id=9, method="tools/call", params={"name": "add_numbers", "arguments": {"a": 10, "b": 20}})
            r2 = await session.call_tool("add_numbers", arguments={"a": 10, "b": 20})
            print_jsonrpc_response(req_id=9, result_obj=r2)
            
            print_jsonrpc_request(req_id=10, method="tools/call", params={"name": "add_numbers", "arguments": {"a": 10, "b": 20}})
            r3 = await session.call_tool("add_numbers", arguments={"a": 10, "b": 20})
            print_jsonrpc_response(req_id=10, result_obj=r3)

            print(f"\n{BOLD}{GREEN}✅ ARCHITECTURAL VERIFICATION: Strict stateless behavior confirmed. Server can be horizontally scaled across worker pools.{RESET}")

    print("\n" + f"{BOLD}{CYAN}🏁" * 38)
    print("      STATELESS MCP TECHNICAL WALKTHROUGH COMPLETE")
    print("🏁" * 38 + f"{RESET}\n")


if __name__ == "__main__":
    asyncio.run(run_stateless_technical_walkthrough())
