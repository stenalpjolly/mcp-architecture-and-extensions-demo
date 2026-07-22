# 🎪 MCP Interactive Booth Demo Host Dashboard

![MCP Protocol](https://img.shields.io/badge/MCP-1.28.1-blue.svg)
![Transport](https://img.shields.io/badge/Transport-HTTP__SSE-green.svg)
![UI](https://img.shields.io/badge/UI-Single__Page__Booth__Dashboard-purple.svg)

## 📌 Executive Summary

The **MCP Booth Demo Host Application** is a web-based client host dashboard built to demonstrate live, real-time Model Context Protocol communication across multiple servers in a booth or presentation environment.

**No Mocking!** The web dashboard connects over real HTTP Server-Sent Events (SSE) to **4 live Python `FastMCP` servers** running concurrently:

1. **⚡ Server 1 (Port 8001)**: Stateless MCP Server (`01_stateless_mcp_server`)
2. **📡 Server 2 (Port 8002)**: Option 1 Protocol Connection Stateful Server (`02_stateful_mcp_server`)
3. **🔐 Server 3 (Port 8003)**: Out-of-Band `_meta` Request Metadata Context Server (`03_mcp_meta_context`)
4. **🚀 Server 4 (Port 8004)**: Modern Spec Extensions & Formal MCP Apps Server (`04_mcp_extensions_and_apps`)

---

## 🏗️ Architecture Flow

```mermaid
sequenceDiagram
    autonumber
    actor Presenter as Booth Presenter / Web UI
    participant Host as Web Host App
    participant S4 as MCP Apps & Extensions Server

    Presenter->>Host: Select Server in Dropdown & Click Connect Host RPC
    Host->>S4: Establish SSE Connection (GET /sse)
    S4-->>Host: Return Message Endpoint URI
    Host->>S4: Send "initialize" Request
    S4-->>Host: Return InitializeResult with capabilities
    Host->>S4: Send "notifications/initialized"
    Host->>S4: Perform Discovery Phase (tools/list, resources/list)
    Presenter->>Host: Execute "launch_analytics_app" with _meta Context
    Host->>S4: tools/call with params & _meta
    S4-->>Host: Return EmbeddedResource with text/html;profile=mcp-app
    Note over Host: Host renders interactive web widget inside iframe container
```

---

## 🚀 Running the Booth Demo

Simply execute `launcher.py` to start all 4 MCP SSE servers and launch the Web Host Application:

```bash
python3 ~/temp/mcp-architecture-and-extensions-demo/booth_demo_host/launcher.py
```

### Output:

```text
🚀 Launching 4 Real MCP SSE Servers (No Mocking)...

  ✔ ⚡ Demo 1: Stateless MCP Server -> SSE Endpoint: http://127.0.0.1:8001/sse
  ✔ 📡 Demo 2: Option 1 Protocol Connection Stateful Server -> SSE Endpoint: http://127.0.0.1:8002/sse
  ✔ 🔐 Demo 3: Out-of-Band _meta Request Metadata Server -> SSE Endpoint: http://127.0.0.1:8003/sse
  ✔ 🚀 Demo 4: Modern Spec Extensions & Formal MCP Apps Server -> SSE Endpoint: http://127.0.0.1:8004/sse

=========================================================================
🖥️  MCP BOOTH DEMO WEB HOST APPLICATION ONLINE!
=========================================================================
👉 Open in browser: http://127.0.0.1:8000/index.html
👉 Select any of the 4 MCP Servers in the dropdown to connect live RPC!
=========================================================================
```

---

## 🎪 Booth Demo Highlights to Present to Audience

1. **Live Server Switching**: Use the top dropdown to seamlessly switch between Stateless, Connection Stateful, Metadata, and Extensions servers.
2. **Real-Time JSON-RPC 2.0 Stream Inspector**: Watch raw `initialize`, `notifications/initialized`, `tools/call`, `resources/read`, and `notifications/tools/list_changed` payloads stream live in the terminal panel.
3. **Out-of-Band `_meta` Injector**: Demonstrate passing caller identity (`client_id`, `user_id`, `tenant_id`, `trace_id`) out-of-band without changing public tool schemas.
4. **Embedded MCP App Widget (Iframe Container)**: Execute `launch_analytics_app` or read `ui://analytics_app` to watch the host render the interactive web widget (`text/html;profile=mcp-app`) inside a sandboxed iframe.
5. **Dynamic Schema Mutation**: Toggle `toggle_admin_mode` in Server 2 and watch the Tool Dropdown update dynamically in real time when `notifications/tools/list_changed` is emitted over SSE.
