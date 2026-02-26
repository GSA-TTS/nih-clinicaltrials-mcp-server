from fastmcp import FastMCP
from .tools import register_tools
from clinicaltrials.prompts import register_prompts
from clinicaltrials.routes import register_routes

# Initialize FastMCP server
mcp = FastMCP("clinicaltrials")

# Register custom routes
register_routes(mcp)

# Register custom tools
register_tools(mcp)

# Register custom prompts
register_prompts(mcp)

# ASGI app for remote deployment (gunicorn/uvicorn imports this)
# Example: gunicorn reporter.app:app
app = mcp.http_app(stateless_http=True)


if __name__ == "__main__":
    # Running directly: use stdio for local MCP client (Claude Desktop, etc.)
    # Remote deployments use the ASGI app above via gunicorn/uvicorn
    mcp.run(transport="stdio")