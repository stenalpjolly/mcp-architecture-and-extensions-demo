# Demo 04: Modern Spec Extensions & Formal MCP Apps Standard

![MCP Protocol](https://img.shields.io/badge/MCP-1.28.1-blue.svg)
![Feature](https://img.shields.io/badge/Feature-MCP__Apps_Formal__Spec-purple.svg)
![Extensions](https://img.shields.io/badge/Extensions-Elicitation_|_Tasks_|_Subscriptions_|_Completions-green.svg)

## 📌 Executive Summary

The Model Context Protocol ecosystem has expanded beyond simple text-based tool responses.

**MCP Apps** has officially graduated from an experimental prototype (formerly `MCP-UI`) into a **formal MCP Specification Standard**!

This demo showcases the **5 Core Specification Extensions**:

1. **Formal MCP Apps Standard (`ui://` & `text/html;profile=mcp-app`)**:
   - Standardized URI scheme (`ui://`) and MIME profile (`text/html;profile=mcp-app`).
   - Serves interactive HTML, CSS, JavaScript, canvas charts, and postMessage event handlers rendered inside sandboxed iframe containers.
2. **Human-in-the-Loop Elicitation (`elicitation/`)**:
   - Interactively requests user confirmation or missing inputs mid-tool-execution before completing high-risk operations.
3. **Background Tasks & Async Workflows (`tasks/`)**:
   - Manages non-blocking background task execution (`task_id`), progress updates, status polling (`RUNNING` $\rightarrow$ `COMPLETED`), and task cancellation.
4. **Resource Subscriptions & Live Push (`resources/subscribe`)**:
   - Allows client hosts to subscribe to resource URIs (`metrics://live`) to receive real-time `notifications/resources/updated` push events.
5. **Dynamic Parameter Auto-Completions (`completion/complete`)**:
   - Registers auto-completion handlers providing dynamic parameter completion suggestions.

---

## 🏗️ Architecture & Extension Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client as MCP Client Host / UI Frame
    participant Server as MCP Extension Server
    participant Worker as Background Task Worker

    Note over Client,Server: Extension 1: Formal MCP Apps Standard (ui://)
    Client->>Server: 1. tools/call "launch_analytics_app"
    Server-->>Client: 2. Return CallToolResult (mime_type: "text/html;profile=mcp-app", app_uri: "ui://analytics_app")
    Note over Client: Host renders embedded HTML/JS iframe widget

    Note over Client,Server: Extension 2: Human-in-the-Loop Elicitation
    Client->>Server: 3. tools/call "transfer_funds_with_approval" ($15,000)
    Server-->>Client: 4. Elicitation Request: "Do you authorize transfer of $15,000?"
    Client-->>Server: 5. Elicitation Response: Human Operator Approves
    Server-->>Client: 6. Execution Result (Transaction Confirmed)

    Note over Client,Server: Extension 3: Background Tasks
    Client->>Server: 7. tools/call "start_background_export_task"
    Server->>Worker: 8. Spawn background worker process
    Server-->>Client: 9. Immediate Response: { task_id: "task_c2d34a4d", status: "RUNNING" }
    Worker-->>Client: 10. Stream Progress Notifications (1666/5000 -> 5000/5000)
    Client->>Server: 11. tools/call "get_task_status"("task_c2d34a4d")
    Server-->>Client: 12. Response: { status: "COMPLETED" }
```

---

## 🛠️ API Reference

| Handler Name | Type | Description |
| :--- | :--- | :--- |
| `ui://analytics_app` | Resource (`ui://`, MIME: `text/html;profile=mcp-app`) | Serves formal MCP App HTML/JS dashboard widget. |
| `launch_analytics_app` | Tool | Returns formal MCP App widget payload for inline host UI rendering. |
| `transfer_funds_with_approval` | Tool | Triggers mid-tool human-in-the-loop elicitation prompt. |
| `start_background_export_task` | Tool | Spawns non-blocking background task tracking task_id status. |
| `get_task_status` | Tool | Polls status of a background task (`RUNNING` $\rightarrow$ `COMPLETED`). |
| `metrics://live` | Resource | Live metrics resource supporting client subscriptions (`resources/subscribe`). |

---

## 💻 Raw JSON-RPC 2.0 Payload Examples

### Formal MCP App Response Payload (`tools/call`)

```json
📥 [RAW JSON-RPC 2.0 RESPONSE PAYLOAD]:
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"status\": \"Launched\",\n  \"app_uri\": \"ui://analytics_app\",\n  \"spec_status\": \"Formal Standard (out of experimental)\",\n  \"mime_type\": \"text/html;profile=mcp-app\",\n  \"component_type\": \"html-iframe\",\n  \"dimensions\": {\"width\": \"100%\", \"height\": \"320px\"},\n  \"html_content\": \"<!DOCTYPE html><html>...<div class=\\\"card\\\">📊 Real-Time MCP App Component</div>...</html>\"\n}"
      }
    ],
    "isError": false
  }
}
```

---

## 🚀 Running the Interactive Technical Walkthrough

```bash
# Interactive Presentation Mode (Press ENTER to advance each step):
python3 ~/temp/mcp-architecture-and-extensions-demo/04_mcp_extensions_and_apps/test_client.py

# Fast Auto Mode (Runs without pausing):
python3 ~/temp/mcp-architecture-and-extensions-demo/04_mcp_extensions_and_apps/test_client.py --auto
```
