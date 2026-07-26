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
