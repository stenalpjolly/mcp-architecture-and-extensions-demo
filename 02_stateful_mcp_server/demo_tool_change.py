#!/usr/bin/env python3
"""Standalone Demo: Dynamic Tool Mutation in Demo 2.

This script isolates and demonstrates how an MCP server dynamically adds and removes
tools over an active connection session in real time.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.13/site-packages'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_tool_change_demo():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env={
            **os.environ,
            "PYTHONPATH": os.path.expanduser('~/.local/lib/python3.13/site-packages')
        }
    )

    print("=" * 70)
    print("🎯 DEMO: DYNAMIC TOOL MUTATION OVER ACTIVE MCP CONNECTION")
    print("=" * 70)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Protocol Session Initialized!\n")

            # 1. Check tools before dynamic mutation
            print("1️⃣ STEP 1: Querying initial tool list from server...")
            tools1 = await session.list_tools()
            names1 = [t.name for t in tools1.tools]
            print(f"   Tools ({len(names1)}): {names1}")
            print(f"   --> 'admin_system_diagnostics' present? {'admin_system_diagnostics' in names1}\n")

            # 2. Trigger dynamic tool addition
            print("2️⃣ STEP 2: Executing 'toggle_admin_mode(enable=True)'...")
            await session.call_tool("toggle_admin_mode", arguments={"enable": True})
            print("   --> Server dynamically registered 'admin_system_diagnostics' into active session!\n")

            # 3. Query tools after dynamic mutation
            print("3️⃣ STEP 3: Querying tool list again to verify dynamic addition...")
            tools2 = await session.list_tools()
            names2 = [t.name for t in tools2.tools]
            print(f"   Tools ({len(names2)}): {names2}")
            print(f"   --> 'admin_system_diagnostics' present? {'admin_system_diagnostics' in names2}\n")

            # 4. Execute the newly registered tool
            print("4️⃣ STEP 4: Calling the dynamically added 'admin_system_diagnostics' tool...")
            diag_res = await session.call_tool("admin_system_diagnostics", arguments={})
            print(f"   Result: {diag_res.content[0].text}\n")

            # 5. Trigger dynamic tool removal
            print("5️⃣ STEP 5: Executing 'toggle_admin_mode(enable=False)'...")
            await session.call_tool("toggle_admin_mode", arguments={"enable": False})
            print("   --> Server dynamically removed 'admin_system_diagnostics' from session!\n")

            # 6. Verify tool removal
            print("6️⃣ STEP 6: Querying tool list to verify dynamic removal...")
            tools3 = await session.list_tools()
            names3 = [t.name for t in tools3.tools]
            print(f"   Tools ({len(names3)}): {names3}")
            print(f"   --> 'admin_system_diagnostics' present? {'admin_system_diagnostics' in names3}\n")

    print("=" * 70)
    print("✨ DYNAMIC TOOL MUTATION DEMO COMPLETED!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tool_change_demo())
