import uvicorn
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("mcp-db-server")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Unauthenticated health endpoint for load balancers and container probes."""
    return JSONResponse({"status": "healthy", "service": "mcp-db-server"})


def main() -> None:
    app = mcp.http_app(transport="http")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
