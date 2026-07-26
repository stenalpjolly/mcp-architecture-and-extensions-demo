#!/usr/bin/env bgsh
# Shell Script to Launch Official Model Context Protocol Inspector UI (@modelcontextprotocol/inspector)

echo "========================================================================="
echo "🔍 OFFICIAL MODEL CONTEXT PROTOCOL INSPECTOR UI LAUNCHER"
echo "========================================================================="
echo ""

# Mode 1: STDIO Transport Mode
echo "Option 1: Launch Inspector in STDIO mode (spawns server.py automatically)"
echo "  Command: npx -y @modelcontextprotocol/inspector python3 server.py"
echo ""

# Mode 2: SSE Transport Mode
echo "Option 2: Launch Inspector in SSE mode (connects to running SSE server on Port 8006)"
echo "  Command: CLIENT_PORT=5173 SERVER_PORT=3000 npx -y @modelcontextprotocol/inspector"
echo ""

if [ "$1" == "--no-auth" ]; then
    echo "🚀 Launching Official MCP Inspector with DANGEROUSLY_OMIT_AUTH=true..."
    DANGEROUSLY_OMIT_AUTH=true npx -y @modelcontextprotocol/inspector python3 server.py
else
    echo "🚀 Launching Official MCP Inspector in Stdio mode..."
    npx -y @modelcontextprotocol/inspector python3 server.py
fi
