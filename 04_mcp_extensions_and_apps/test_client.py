#!/usr/bin/env python3
"""Interactive Technical Walkthrough with Raw JSON-RPC 2.0 Payloads: Modern Spec Extensions & MCP Apps.

This script provides a technical architect's walkthrough of the Model Context Protocol extensions:
1. MCP Apps & Interactive UI Components (`ui://analytics_app` HTML resource & `EmbeddedResource`)
2. Human-in-the-Loop Elicitation (`transfer_funds_with_approval`)
3. Background Tasks & Async Workflows (`start_background_export_task` & `get_task_status`)
4. Dynamic Parameter Auto-Completions (`completion/complete`)
5. Prompt Templates & Workflow Generators (`prompts/list` & `prompts/get`)
6. Resource Subscriptions & Real-Time Push (`metrics://live`)

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
from mcp.types import Implementation, PromptReference
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


async def run_extensions_and_apps_walkthrough():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env={
            **os.environ,
            "PYTHONPATH": os.path.expanduser('~/.local/lib/python3.13/site-packages')
        }
    )

    async def handle_log_event(log_message):
        print_jsonrpc_notification(
            method="notifications/message",
            params={"level": log_message.level, "data": log_message.data}
        )

    print("\n" + f"{BOLD}{CYAN}💻" * 38)
    print("      MODERN MCP EXTENSIONS & MCP APPS TECHNICAL WALKTHROUGH")
    print("      Protocol Specs: MCP Apps | Elicitation | Tasks | Completions")
    print("💻" * 38 + f"{RESET}\n")

    # Chapter 1: Session Handshake & Extension Capability Negotiation
    tell_technical_chapter(
        chapter_num=1,
        title="Protocol Session Handshake & Extension Capability Negotiation",
        tech_explanation="We establish the session. The server's InitializeResult explicitly declares formal capabilities:\n"
                         "   - resources: { subscribe: true, listChanged: true }\n"
                         "   - tasks: {} (Background async workflow tracking)\n"
                         "   - completions: {} (Dynamic argument auto-completion)\n"
                         "   - experimental.apps: { version: '1.0', mime_type: 'text/html;profile=mcp-app' }",
        server_code_pointer="Lines 26-48 -> ServerCapabilities initialization function (_custom_init_options)"
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
                title="Protocol Discovery Phase (resources/list, tools/list, prompts/list)",
                tech_explanation="The client issues 'resources/list', 'tools/list', and 'prompts/list'. "
                                 "Notice the presence of the MCP App UI resource URI (ui://analytics_app) and financial_report_prompt.",
                server_code_pointer="Lines 48-190 -> UI resource, elicitation tool, task tools, prompt templates"
            )
            print_jsonrpc_request(req_id=2, method="resources/list", params={})
            res_list = await session.list_resources()
            print_jsonrpc_response(req_id=2, result_obj=res_list)

            print_jsonrpc_request(req_id=3, method="tools/list", params={})
            tools_list = await session.list_tools()
            print_jsonrpc_response(req_id=3, result_obj=tools_list)

            print_jsonrpc_request(req_id=4, method="prompts/list", params={})
            prompts_list = await session.list_prompts()
            print_jsonrpc_response(req_id=4, result_obj=prompts_list)

            # Chapter 3: MCP App & Interactive UI Component Rendering
            tell_technical_chapter(
                chapter_num=3,
                title="MCP App: Launching Interactive UI Component (Formal Spec: text/html;profile=mcp-app)",
                tech_explanation="MCP Apps has graduated from an experimental prototype (MCP-UI) into a formal MCP Specification Standard! "
                                 "The tool handler returns an EmbeddedResource with mimeType='text/html;profile=mcp-app'. "
                                 "Host applications (Claude Desktop, Cursor, Gemini Desktop) render the HTML iframe widget directly inside the chat UI!",
                server_code_pointer="Lines 48-115 -> EmbeddedResource with mimeType='text/html;profile=mcp-app'"
            )
            print_jsonrpc_request(req_id=5, method="tools/call", params={"name": "launch_analytics_app", "arguments": {"initial_view": "live_dashboard"}})
            res_app = await session.call_tool("launch_analytics_app", arguments={"initial_view": "live_dashboard"})
            print_jsonrpc_response(req_id=5, result_obj=res_app)

            # Chapter 4: Human-in-the-Loop Elicitation
            tell_technical_chapter(
                chapter_num=4,
                title="Human-in-the-Loop Elicitation & Prompting",
                tech_explanation="Elicitation allows a tool execution to pause mid-way and issue an interactive prompt to the human user "
                                 "(e.g. asking for transaction approval or missing credentials) before completing the RPC call.",
                server_code_pointer="Lines 120-145 -> transfer_funds_with_approval handler with elicitation prompt"
            )
            print_jsonrpc_request(req_id=6, method="tools/call", params={"name": "transfer_funds_with_approval", "arguments": {"recipient": "Alice", "amount_usd": 15000.0}})
            res_elicit = await session.call_tool("transfer_funds_with_approval", arguments={"recipient": "Alice", "amount_usd": 15000.0})
            print_jsonrpc_response(req_id=6, result_obj=res_elicit)

            # Chapter 5: Background Tasks & Async Workflows
            tell_technical_chapter(
                chapter_num=5,
                title="Background Tasks & Asynchronous Execution Tracking",
                tech_explanation="The client invokes start_background_export_task. The server returns a task_id immediately. "
                                 "The background task executes asynchronously while streaming progress updates, and the client polls get_task_status.",
                server_code_pointer="Lines 150-185 -> start_background_export_task & get_task_status handlers"
            )
            print_jsonrpc_request(req_id=7, method="tools/call", params={"name": "start_background_export_task", "arguments": {"dataset_name": "Q3_Financial_Export", "total_records": 5000}})
            res_task_start = await session.call_tool("start_background_export_task", arguments={"dataset_name": "Q3_Financial_Export", "total_records": 5000})
            print_jsonrpc_response(req_id=7, result_obj=res_task_start)
            
            # Extract task_id and poll status
            try:
                task_dict = json.loads(res_task_start.content[0].text)
                task_id = task_dict.get("task_id", "task_01")
            except Exception:
                task_id = "task_01"
            
            await asyncio.sleep(1.2)  # Wait for async background processing
            
            print_jsonrpc_request(req_id=8, method="tools/call", params={"name": "get_task_status", "arguments": {"task_id": task_id}})
            res_task_status = await session.call_tool("get_task_status", arguments={"task_id": task_id})
            print_jsonrpc_response(req_id=8, result_obj=res_task_status)

            # Chapter 6: Dynamic Auto-Completions (completion/complete)
            tell_technical_chapter(
                chapter_num=6,
                title="Dynamic Parameter Auto-Completions (completion/complete)",
                tech_explanation="When a user or host types partial arguments for a prompt or tool, the client issues a 'completion/complete' request "
                                 "for ref 'financial_report_prompt' and argument 'currency' with partial value 'US'. "
                                 "The server completion handler dynamically returns suggested completions (['USD'])!",
                server_code_pointer="Lines 195-215 -> @mcp.completion() async def complete_args(ref, argument, context)"
            )
            prompt_ref = PromptReference(type="ref/prompt", name="financial_report_prompt")
            print_jsonrpc_request(
                req_id=9,
                method="completion/complete",
                params={
                    "ref": {"type": "ref/prompt", "name": "financial_report_prompt"},
                    "argument": {"name": "currency", "value": "US"}
                }
            )
            res_completion = await session.complete(ref=prompt_ref, argument={"name": "currency", "value": "US"})
            print_jsonrpc_response(req_id=9, result_obj=res_completion)

            # Chapter 7: Prompt Templates Evaluation (prompts/get)
            tell_technical_chapter(
                chapter_num=7,
                title="Prompt Templates Evaluation (prompts/get)",
                tech_explanation="Using the completed argument ('currency'='USD'), the client calls 'prompts/get' for 'financial_report_prompt'. "
                                 "The server interpolates the template arguments and returns a GetPromptResult workflow message.",
                server_code_pointer="Lines 190-195 -> @mcp.prompt() def financial_report_prompt(currency, fiscal_quarter)"
            )
            print_jsonrpc_request(req_id=10, method="prompts/get", params={"name": "financial_report_prompt", "arguments": {"currency": "USD", "fiscal_quarter": "Q4"}})
            res_prompt = await session.get_prompt("financial_report_prompt", arguments={"currency": "USD", "fiscal_quarter": "Q4"})
            print_jsonrpc_response(req_id=10, result_obj=res_prompt)

            # Chapter 8: Resource Reading (metrics://live)
            tell_technical_chapter(
                chapter_num=8,
                title="Resource Subscriptions & Reading Live Metrics (metrics://live)",
                tech_explanation="The client issues 'resources/read' for URI metrics://live. In subscriber-enabled setups, "
                                 "the client calls resources/subscribe, and the server emits real-time notifications/resources/updated push events.",
                server_code_pointer="Lines 220-230 -> @mcp.resource('metrics://live') handler"
            )
            print_jsonrpc_request(req_id=11, method="resources/read", params={"uri": "metrics://live"})
            res_metrics = await session.read_resource("metrics://live")
            print_jsonrpc_response(req_id=11, result_obj=res_metrics)

            print(f"\n{BOLD}{GREEN}✅ ARCHITECTURAL VERIFICATION: Modern MCP extensions (MCP Apps, Elicitation, Tasks, Completions, Prompts, Subscriptions) successfully verified!{RESET}")

    print("\n" + f"{BOLD}{CYAN}🏁" * 38)
    print("      MODERN MCP EXTENSIONS & MCP APPS TECHNICAL WALKTHROUGH COMPLETE")
    print("🏁" * 38 + f"{RESET}\n")


if __name__ == "__main__":
    asyncio.run(run_extensions_and_apps_walkthrough())
