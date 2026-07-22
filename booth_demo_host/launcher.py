#!/usr/bin/env python3
"""Unified Booth Demo Host Launcher & Reverse Proxy.

This launcher spawns all 4 real Python MCP servers bound internally to loopback (Ports 8001-8004)
and acts as a Unified Reverse Proxy on Port 8000.

Client hosts do NOT connect directly to backend server ports.
All RPC connections, SSE streams, and static web dashboard files are served exclusively on Port 8000!

Proxied Endpoint Mappings:
  - GET  /                                  -> Booth Web Host Dashboard (index.html)
  - GET  /api/demo1/sse & POST /api/demo1/messages -> Proxied to 127.0.0.1:8001 (Stateless Server)
  - GET  /api/demo2/sse & POST /api/demo2/messages -> Proxied to 127.0.0.1:8002 (Stateful Server)
  - GET  /api/demo3/sse & POST /api/demo3/messages -> Proxied to 127.0.0.1:8003 (_meta Context Server)
  - GET  /api/demo4/sse & POST /api/demo4/messages -> Proxied to 127.0.0.1:8004 (Extensions & MCP Apps Server)

Usage:
  python3 launcher.py
"""

import sys
import os
import time
import subprocess
import http.server
import socketserver
import urllib.request
import urllib.error
import site

# Ensure portable site packages
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

# ANSI Palette
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
        "id": "demo1",
        "name": "⚡ Demo 1: Stateless MCP Server",
        "path": os.path.join(DEMO_DIR, "01_stateless_mcp_server", "server.py"),
        "port": 8001
    },
    {
        "id": "demo2",
        "name": "📡 Demo 2: Option 1 Protocol Connection Stateful Server",
        "path": os.path.join(DEMO_DIR, "02_stateful_mcp_server", "server.py"),
        "port": 8002
    },
    {
        "id": "demo3",
        "name": "🔐 Demo 3: Out-of-Band _meta Request Metadata Server",
        "path": os.path.join(DEMO_DIR, "03_mcp_meta_context", "server.py"),
        "port": 8003
    },
    {
        "id": "demo4",
        "name": "🚀 Demo 4: Modern Spec Extensions & Formal MCP Apps Server",
        "path": os.path.join(DEMO_DIR, "04_mcp_extensions_and_apps", "server.py"),
        "port": 8004
    }
]

processes = []


def launch_mcp_servers():
    print(f"\n{BOLD}{CYAN}🚀 Launching 4 Internal MCP SSE Backend Servers...{RESET}\n")
    
    env = {**os.environ}
    if user_site:
        env["PYTHONPATH"] = f"{user_site}:{os.environ.get('PYTHONPATH', '')}".strip(":")

    for s in SERVERS:
        cmd = [sys.executable, s["path"], "--sse", "--port", str(s["port"])]
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(proc)
        print(f"  {GREEN}✔ {s['name']}{RESET} -> Bound Internal: {BOLD}127.0.0.1:{s['port']}{RESET}")
        time.sleep(0.3)
        
    print(f"\n{BOLD}{GREEN}✅ All 4 Internal MCP Backend Servers online!{RESET}")


class UnifiedProxyHostHandler(http.server.SimpleHTTPRequestHandler):
    """Unified HTTP Handler serving web host UI and acting as a reverse proxy for MCP RPC connections."""

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, _meta")
        self.end_headers()

    def do_GET(self):
        """Route static files or proxy SSE requests upstream."""
        for s in SERVERS:
            route_prefix = f"/api/{s['id']}/sse"
            if self.path.startswith(route_prefix):
                self._proxy_sse_request(target_port=s["port"], demo_id=s["id"])
                return

        # Serve static web dashboard files (index.html)
        super().do_GET()

    def do_POST(self):
        """Proxy JSON-RPC tool/resource messages upstream."""
        for s in SERVERS:
            route_prefix = f"/api/{s['id']}/messages"
            if self.path.startswith(route_prefix):
                self._proxy_message_request(target_port=s["port"], demo_id=s["id"])
                return
        
        self.send_error(404, "Endpoint not found on proxy.")

    def _proxy_sse_request(self, target_port: int, demo_id: str):
        """Streams GET SSE requests upstream and rewrites the message endpoint URL."""
        upstream_url = f"http://127.0.0.1:{target_port}/sse"
        req = urllib.request.Request(upstream_url, headers={"Accept": "text/event-stream"})
        
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                while True:
                    line = resp.readline()
                    if not line:
                        break
                    line_str = line.decode("utf-8")
                    # Rewrite upstream message endpoint to proxied route
                    if line_str.startswith("data: /messages"):
                        line_str = line_str.replace("data: /messages", f"data: /api/{demo_id}/messages")
                        line = line_str.encode("utf-8")
                    
                    try:
                        self.wfile.write(line)
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            try:
                self.send_error(502, f"Bad Gateway (Proxy -> Server Port {target_port}): {e}")
            except (BrokenPipeError, ConnectionResetError):
                pass

    def _proxy_message_request(self, target_port: int, demo_id: str):
        """Forwards POST JSON-RPC payloads upstream."""
        upstream_path = self.path[len(f"/api/{demo_id}"):]
        upstream_url = f"http://127.0.0.1:{target_port}{upstream_path}"
        
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        
        req = urllib.request.Request(
            upstream_url, 
            data=body, 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(res_body)
        except urllib.error.HTTPError as he:
            self.send_response(he.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(he.read())
        except Exception as e:
            self.send_error(502, f"Proxy Error: {e}")

    def log_message(self, format, *args):
        pass  # Quiet HTTP logs


def serve_unified_proxy_host():
    host_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(host_dir)
    
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    port = 8000
    try:
        httpd = ReusableTCPServer(("0.0.0.0", port), UnifiedProxyHostHandler)
    except OSError:
        port = 8080
        httpd = ReusableTCPServer(("0.0.0.0", port), UnifiedProxyHostHandler)

    with httpd:
        print(f"\n{BOLD}{MAGENTA}========================================================================={RESET}")
        print(f"{BOLD}{YELLOW}🖥️  UNIFIED REVERSE PROXY & BOOTH DEMO HOST APPLICATION ONLINE!{RESET}")
        print(f"{BOLD}{MAGENTA}========================================================================={RESET}")
        print(f"👉 Web Dashboard Access: {BOLD}{CYAN}http://127.0.0.1:{port}/index.html{RESET}")
        print(f"👉 Unified Single-Port Architecture: All 4 MCP Servers proxied over Port {port}!")
        print(f"{BOLD}{MAGENTA}========================================================================={RESET}\n")
        print("Press [CTRL+C] to stop all servers and shutdown host application.\n")
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        launch_mcp_servers()
        serve_unified_proxy_host()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Shutting down processes...{RESET}")
        for p in processes:
            p.terminate()
        sys.exit(0)
