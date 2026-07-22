# 📡 Model Context Protocol (MCP) Server & Booth Demo Suite

[![MCP Standard](https://img.shields.io/badge/MCP-Standard_v1.0-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Booth Demo](https://img.shields.io/badge/Booth__Demo-Web__Host__App-purple.svg)](./booth_demo_host/)
[![Demos Suite](https://img.shields.io/badge/Demos-Stateless_|_Stateful_|_Request__Metadata_|_MCP__Apps-green.svg)](./)

A complete demonstration suite showcasing **Stateless MCP Servers**, **Option 1: Protocol Connection Stateful MCP Servers**, **Out-of-Band Request Metadata (`_meta`)**, **Modern Spec Extensions & Formal MCP Apps**, and a **Single-Page Interactive Web Host Dashboard for Booth Presentations** using Python [`FastMCP`](https://github.com/modelcontextprotocol/python-sdk).

---

## 📂 Repository Structure

```
~/temp/demo/
├── README.md                           # Main repository guide
├── booth_demo_host/                    # 🎪 Booth Presentation Web Host Application
│   ├── launcher.py                     # Launcher spawning all 4 MCP SSE servers & web host
│   ├── index.html                      # Single-page interactive web dashboard (HTML/JS/CSS)
│   └── README.md                       # Booth presentation instructions
├── 01_stateless_mcp_server/            # Demo 1: Stateless MCP Server (Pure functions)
│   ├── server.py                       # Pure request-response tool & resource handlers
│   ├── test_client.py                  # Interactive technical architect test walkthrough
│   └── README.md                       # Stateless documentation
├── 02_stateful_mcp_server/             # Demo 2: Protocol Connection Stateful MCP Server (Option 1)
│   ├── server.py                       # Session context, progress streams, dynamic tool mutations
│   ├── test_client.py                  # Interactive technical architect test walkthrough
│   └── README.md                       # Connection stateful documentation
├── 03_mcp_meta_context/                # Demo 3: Request Metadata (_meta) Context Processing
│   ├── server.py                       # Out-of-band _meta handlers for Auth, Multitenancy & Tracing
│   ├── test_client.py                  # Interactive technical architect test walkthrough
│   └── README.md                       # Out-of-band _meta documentation
└── 04_mcp_extensions_and_apps/        # Demo 4: Modern Spec Extensions & Formal MCP Apps
    ├── server.py                       # Formal MCP Apps (UI widgets), Elicitation, Tasks, Completions
    ├── test_client.py                  # Interactive technical architect test walkthrough
    └── README.md                       # Modern spec extensions documentation
```

---

## 🎪 Quickstart: Launching the Interactive Booth Demo Host Dashboard

Run `launcher.py` to spawn all 4 real MCP servers over SSE HTTP transport (Ports 8001-8004) and open the interactive web host app at `http://127.0.0.1:8000/index.html`:

```bash
python3 ~/temp/mcp-architecture-and-extensions-demo/booth_demo_host/launcher.py
```

### Live Features in the Booth Host Dashboard:
* **Server Selection Dropdown**: Switch live connections between Demo 1, Demo 2, Demo 3, and Demo 4.
* **Embedded MCP App Webview Container**: Renders interactive web widgets (`text/html;profile=mcp-app` / `ui://analytics_app`) inside a sandboxed iframe.
* **Out-of-Band `_meta` Injector**: Inject `client_id`, `user_id`, `tenant_id`, and `trace_id` headers live.
* **Real-Time JSON-RPC 2.0 Terminal Inspector**: Inspect raw request, response, and notification stream payloads in real time.
* **Dynamic Schema Mutation**: Toggle admin mode and watch the tool list update dynamically upon receiving `notifications/tools/list_changed`.

---

## 📊 Feature Comparison Matrix Across All Demos

| Dimension | Demo 1: Stateless (`01_stateless_mcp_server`) | Demo 2: Connection Stateful (`02_stateful_mcp_server`) | Demo 3: Request Metadata (`03_mcp_meta_context`) | Demo 4: Extensions & MCP Apps (`04_mcp_extensions_and_apps`) |
| :--- | :--- | :--- | :--- | :--- |
| **Protocol Focus** | Pure functional request-response | Active connection state & streaming | Out-of-band request metadata (`_meta`) | **Modern Extensions & Formal MCP Apps Standard** |
| **UI Component Rendering** | Plain Text Output | Plain Text Output | Plain Text Output | **Interactive Webviews (`ui://analytics_app` HTML Widgets)** |
| **Human Approval / Elicitation** | None | None | None | **Interactive Elicitation Prompts (`transfer_funds_with_approval`)** |
| **Task Execution Model** | Synchronous | Stream Progress | Synchronous | **Async Non-Blocking Tasks (`task_id` & `get_task_status`)** |
| **Parameter Auto-Completions** | None | None | None | **Dynamic Argument Completions (`completion/complete`)** |
| **Authentication & Auth** | Explicit parameters | Handshake `clientInfo` | **`_meta.auth_token` & `_meta.user_id`** | Experimental `apps` & `tasks` Capabilities |

---

## 💻 Technical Walkthrough Scripts (Terminal Mode)

```bash
# 1. Run Stateless MCP Server Walkthrough
python3 01_stateless_mcp_server/test_client.py

# 2. Run Option 1: Protocol Connection Stateful MCP Server Walkthrough
python3 02_stateful_mcp_server/test_client.py

# 3. Run Request Metadata (_meta) MCP Server Walkthrough
python3 03_mcp_meta_context/test_client.py

# 4. Run Modern Spec Extensions & Formal MCP Apps Walkthrough
python3 04_mcp_extensions_and_apps/test_client.py
```
