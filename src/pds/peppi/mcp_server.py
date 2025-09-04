"""Model Context Protocol (MCP) server."""
import pds.peppi as pep
from fastmcp import FastMCP


def main():
    """Main entry point, to launch the service.

    Should stay as mininal as possible and just connect documentated entries from the peppi library, as tools or resrouces
    """
    mcp = FastMCP("PDS MCP server")

    context = pep.Context()
    mcp.tool(context.INSTRUMENT_HOSTS.search)
    mcp.tool(context.TARGETS.search)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
