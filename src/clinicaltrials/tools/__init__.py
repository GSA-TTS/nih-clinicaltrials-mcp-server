"""Tool registration aggregator.

Import each dataset module's register_*_tools function here and call it
from register_tools(). This keeps server.py clean and makes it easy to
add or remove entire dataset integrations in one place.
"""

from fastmcp import FastMCP

from .tools import register_tools


def register_tools(mcp: FastMCP) -> None:
    """Register all tools with the MCP server instance."""
    register_tools(mcp)

    # Add more datasets here as you build them:
    # from .census import register_census_tools
    # register_census_tools(mcp)
