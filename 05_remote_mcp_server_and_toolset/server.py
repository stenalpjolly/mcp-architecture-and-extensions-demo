#!/usr/bin/env python3
"""Remote MCP Server Connection Endpoint (Demo 5).

Acts as a remote HTTP/SSE transport bridge for external Streamable HTTP connections.
"""

import sys
import os
import site

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Initialize Remote Connection Server
mcp = FastMCP("Remote MCP Streamable Connection Server", log_level="WARNING")
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "0.0.0.0"
    mcp.run(transport=transport)
