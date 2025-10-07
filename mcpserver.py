from fastmcp import FastMCP
import inspect
import autocad_tools
mcp = FastMCP("autocad_mcp_server")
for func in autocad_tools.tools:
    if callable(func):
        mcp.tool()(func)
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=9901,
        path="/mcp",
        log_level="info",
    )
