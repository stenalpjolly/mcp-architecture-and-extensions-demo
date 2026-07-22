#!/usr/bin/env python3
"""Booth Demo Host Launcher.

This launcher spawns all 4 real Python MCP servers over SSE HTTP transport (Ports 8001-8004)
and serves the single-page Booth Web Host Application at http://127.0.0.1:8000.

No mocking! Connects real web host clients to real running MCP servers over SSE HTTP streams.

Usage:
  python3 launcher.py
"""

import sys
import os
import time
import subprocess
import http.server
import socketserver
import threading

import site

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

DEMO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVERS = [
    {
        "name": "⚡ Demo 1: Stateless MCP Server",
        "path": os.path.join(DEMO_DIR, "01_stateless_mcp_server", "server.py"),
        "port": 8001
    },
    {
        "name": "📡 Demo 2: Option 1 Protocol Connection Stateful Server",
        "path": os.path.join(DEMO_DIR, "02_stateful_mcp_server", "server.py"),
        "port": 8002
    },
    {
        "name": "🔐 Demo 3: Out-of-Band _meta Request Metadata Server",
        "path": os.path.join(DEMO_DIR, "03_mcp_meta_context", "server.py"),
        "port": 8003
    },
    {
        "name": "🚀 Demo 4: Modern Spec Extensions & Formal MCP Apps Server",
        "path": os.path.join(DEMO_DIR, "04_mcp_extensions_and_apps", "server.py"),
        "port": 8004
    }
]

processes = []


def launch_mcp_servers():
    print(f"\n{BOLD}{CYAN}🚀 Launching 4 Real MCP SSE Servers (No Mocking)...{RESET}\n")
    
    env = {**os.environ}
    if user_site:
        env["PYTHONPATH"] = f"{user_site}:{os.environ.get('PYTHONPATH', '')}".strip(":")

    for s in SERVERS:
        cmd = [sys.executable, s["path"], "--sse", "--port", str(s["port"])]
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(proc)
        print(f"  {GREEN}✔ {s['name']}{RESET} -> SSE Endpoint: {BOLD}http://127.0.0.1:{s['port']}/sse{RESET}")
        time.sleep(0.4)
        
    print(f"\n{BOLD}{GREEN}✅ All 4 Real MCP Servers online over HTTP SSE transport!{RESET}")


def serve_web_host():
    host_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(host_dir)
    
    class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Quiet HTTP logs
            
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    port = 8000
    try:
        httpd = ReusableTCPServer(("0.0.0.0", port), QuietHTTPHandler)
    except OSError:
        port = 8080
        httpd = ReusableTCPServer(("0.0.0.0", port), QuietHTTPHandler)

    with httpd:
        print(f"\n{BOLD}{MAGENTA}========================================================================={RESET}")
        print(f"{BOLD}{YELLOW}🖥️  MCP BOOTH DEMO WEB HOST APPLICATION ONLINE!{RESET}")
        print(f"{BOLD}{MAGENTA}========================================================================={RESET}")
        print(f"👉 Local Access:     {BOLD}{CYAN}http://127.0.0.1:{port}/index.html{RESET}")
        print(f"👉 Network Access:   {BOLD}{CYAN}http://stenalpjolly.c.googlers.com:{port}/index.html{RESET}")
        print(f"👉 Select any of the 4 MCP Servers in the dropdown to connect live RPC!")
        print(f"{BOLD}{MAGENTA}========================================================================={RESET}\n")
        print("Press [CTRL+C] to stop all servers and shutdown host application.\n")
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        launch_mcp_servers()
        serve_web_host()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Shutting down processes...{RESET}")
        for p in processes:
            p.terminate()
        sys.exit(0)
