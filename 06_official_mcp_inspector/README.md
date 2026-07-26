# 🔍 Demo 6: Using the Official Model Context Protocol Inspector UI

## Overview

This demo explains how to use the official **Model Context Protocol Inspector UI** (`@modelcontextprotocol/inspector`) to test, debug, and inspect custom MCP servers live during development and demonstrations.

The official inspector is an interactive visual developer interface provided by the Model Context Protocol team. It lets developers:
- Inspect all discovered **Tools**, **Resources**, and **Prompts**.
- Execute tools with real-time argument validation.
- Test `initialize` handshake, protocol capability negotiation, and metadata tracking.
- Test sampling, notifications, and client-server logging stream messages.

---

## 🚀 How to Launch the Official MCP Inspector

### Option 1: Stdio Transport Mode (Recommended for CLI / Local Dev)

The inspector spawns the MCP server executable directly as a child process over standard I/O (`stdio`):

```bash
npx -y @modelcontextprotocol/inspector python3 server.py
```

- Spawns the official web UI (typically on `http://localhost:5173`).
- Connects directly to `server.py` over stdin/stdout.

---

### Option 2: SSE Transport Mode (Recommended for Web / HTTP Services)

Start your Python MCP server in SSE mode on Port 8006:
```bash
python3 server.py --sse --port 8006
```

Then connect the official inspector to your SSE endpoint (`http://127.0.0.1:8006/sse`):
```bash
npx -y @modelcontextprotocol/inspector --transport sse --url http://127.0.0.1:8006/sse
```

Alternatively, launch via the provided helper script:
```bash
./launch_inspector.sh --sse
```

---

## 📺 Presenter Guide: Showcase Official Inspector Live

When running your demo on a remote Googler VM, Cloud Workstation, or SSH host, Chrome cannot directly reach `http://localhost:6277` proxy backend because port 6277 is running on the remote host, leading to `net::ERR_CONNECTION_TIMED_OUT`.

Follow these **2 simple steps** to showcase the official inspector live in Chrome:

### Step 1: Launch Inspector on Remote Host
Run the inspector command in your remote SSH session:
```bash
npx -y @modelcontextprotocol/inspector python3 06_official_mcp_inspector/server.py
```
> Outputs:
> `🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀`
> `🔑 Session token: <TOKEN>`

### Step 2: Forward Ports 6274 & 6277 to Local Machine
In your **local terminal** (Mac/Linux/Windows), run SSH port forwarding for both ports (`6274` web UI + `6277` proxy backend):

```bash
ssh -L 6274:localhost:6274 -L 6277:localhost:6277 stenalpjolly.c.googlers.com
```

### Step 3: Open in Chrome
Open the URL in Chrome on your laptop:
```text
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<TOKEN>
```
Now the official `@modelcontextprotocol/inspector` runs with 100% full functionality, zero connection errors, and live tool/resource testing!

---

## 🛠️ Testing Features in Official MCP Inspector

1. **Tools Tab**:
   - Execute `add_numbers(a: 15, b: 27)` to inspect JSON-RPC request & response frames.
   - Execute `inspect_system_metrics()` to inspect memory and protocol capabilities.
   - Execute `generate_inspector_card(title: "Health Check", severity: "info")` to test EmbeddedResource HTML widget rendering.

2. **Resources Tab**:
   - Inspect `memo://server_status` to view live JSON server diagnostic metadata.
   - Inspect `ui://inspector_app` to view text/html;profile=mcp-app components.

3. **Prompts Tab**:
   - Test `system_debug_prompt(component: "database_connection")`.
   - Test `code_review_prompt(language: "python")`.

---

## 💡 Best Practices for Building Demos with Official MCP Inspector

1. **Use `npx -y` Flag**:
   Add `-y` (`npx -y @modelcontextprotocol/inspector`) to automatically accept package installation without interactive CLI prompts.
2. **Environment Variable Port Override**:
   Set `CLIENT_PORT` and `SERVER_PORT` if default ports `5173` or `3000` conflict:
   ```bash
   CLIENT_PORT=5174 SERVER_PORT=3001 npx -y @modelcontextprotocol/inspector python3 server.py
   ```
3. **Cross-Platform Compatibility**:
   Ensure `python3` (or `python`) is in your PATH.
