#!/usr/bin/env python3
"""Stateless MCP Server Demo.

This server demonstrates a stateless Model Context Protocol (MCP) server design.
A stateless server handles each request independently without maintaining persistent
or side-effecting state between tool calls or client connections.
"""

import sys
import os
import math
import hashlib
import platform
from datetime import datetime, timezone

# Ensure user site-packages are accessible
sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.13/site-packages'))

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Stateless MCP Server - Utilities & Tools", log_level="WARNING")

# ==============================================================================
# TOOLS (Stateless Functions)
# ==============================================================================

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number.
        b: Second number.
        
    Returns:
        The sum of a and b.
    """
    return a + b


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """Calculate Body Mass Index (BMI) and health category.
    
    Args:
        weight_kg: Weight in kilograms (e.g. 70.0).
        height_m: Height in meters (e.g. 1.75).
        
    Returns:
        Dictionary containing BMI value and category string.
    """
    if height_m <= 0 or weight_kg <= 0:
        return {"error": "Weight and height must be positive values."}
    
    bmi = round(weight_kg / (height_m ** 2), 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obesity"
        
    return {
        "weight_kg": weight_kg,
        "height_m": height_m,
        "bmi": bmi,
        "category": category
    }


@mcp.tool()
def transform_text(text: str, operation: str) -> dict:
    """Perform stateless text transformation.
    
    Args:
        text: Input string to process.
        operation: Transformation to apply ('uppercase', 'lowercase', 'reverse', 'word_count', 'sha256').
        
    Returns:
        Dictionary with input text, requested operation, and result.
    """
    op = operation.lower().strip()
    
    if op == "uppercase":
        result = text.upper()
    elif op == "lowercase":
        result = text.lower()
    elif op == "reverse":
        result = text[::-1]
    elif op == "word_count":
        result = len(text.split())
    elif op == "sha256":
        result = hashlib.sha256(text.encode('utf-8')).hexdigest()
    else:
        return {
            "error": f"Unknown operation '{operation}'. Supported: uppercase, lowercase, reverse, word_count, sha256."
        }
        
    return {
        "input_text": text,
        "operation": op,
        "result": result
    }


@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert a numerical value from one unit to another.
    
    Args:
        value: The numerical value to convert.
        from_unit: Source unit ('celsius', 'fahrenheit', 'meters', 'feet', 'kg', 'lbs').
        to_unit: Target unit ('celsius', 'fahrenheit', 'meters', 'feet', 'kg', 'lbs').
        
    Returns:
        Dictionary with original value/unit and converted result/unit.
    """
    f = from_unit.lower().strip()
    t = to_unit.lower().strip()
    
    if f == t:
        return {"value": value, "from_unit": f, "to_unit": t, "result": value}
    
    # Temperature
    if f == "celsius" and t == "fahrenheit":
        converted = (value * 9 / 5) + 32
    elif f == "fahrenheit" and t == "celsius":
        converted = (value - 32) * 5 / 9
    # Distance
    elif f == "meters" and t == "feet":
        converted = value * 3.28084
    elif f == "feet" and t == "meters":
        converted = value / 3.28084
    # Mass
    elif f == "kg" and t == "lbs":
        converted = value * 2.20462
    elif f == "lbs" and t == "kg":
        converted = value / 2.20462
    else:
        return {
            "error": f"Unsupported conversion from '{from_unit}' to '{to_unit}'."
        }
        
    return {
        "original_value": value,
        "from_unit": f,
        "to_unit": t,
        "converted_value": round(converted, 4)
    }

# ==============================================================================
# RESOURCES (Stateless Read-Only Data)
# ==============================================================================

@mcp.resource("system://info")
def get_system_info() -> str:
    """Provides read-only system runtime metadata."""
    info = {
        "server_type": "Stateless MCP Server",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "timestamp_iso": datetime.now(timezone.utc).isoformat()
    }
    import json
    return json.dumps(info, indent=2)

# ==============================================================================
# PROMPTS (Reusable Prompt Templates)
# ==============================================================================

@mcp.prompt()
def code_review_prompt(code: str, language: str = "python") -> str:
    """Generates a prompt template for code review."""
    return f"""Please review the following {language} code snippet for readability, bugs, and performance improvements:

```{language}
{code}
```

Provide constructive recommendations in a bulleted list."""


if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.port = port
        mcp.settings.host = "127.0.0.1"
    mcp.run(transport=transport)
