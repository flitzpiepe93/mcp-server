import os
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import uvicorn
from fastmcp import Context, FastMCP
from fastmcp.server.auth import AuthProvider, require_scopes
from fastmcp.server.auth.providers.keycloak import KeycloakAuthProvider
from starlette.requests import Request
from starlette.responses import JSONResponse

from server.audit import AuditMiddleware
from server.auth import AuthSettings
from server.repository import (
    SqlTitanicRepository,
    SurvivalGroupBy,
    SurvivalRate,
    TitanicRepository,
)


def build_server(
    build_repository: Callable[[], TitanicRepository],
    auth: AuthProvider | None = None,
) -> FastMCP:
    """Build the MCP server around a repository factory.

    Takes a factory (not a built repository) so the repository — and its
    connection pool — is created inside the lifespan at startup and disposed
    at shutdown, keeping setup and teardown symmetric. Injecting the factory
    also lets tests substitute an in-memory repository.

    The auth provider is injected (not built here) so tests can run without
    Keycloak; when omitted the server runs unauthenticated.
    """

    @asynccontextmanager
    async def lifespan(_: FastMCP) -> AsyncIterator[TitanicRepository]:
        repository = build_repository()
        try:
            yield repository
        finally:
            repository.dispose()

    mcp = FastMCP(
        "mcp-db-server",
        lifespan=lifespan,
        auth=auth,
        middleware=[AuditMiddleware()],
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        """Unauthenticated health endpoint for load balancers and container probes."""
        return JSONResponse({"status": "healthy", "service": "mcp-db-server"})

    @mcp.tool(auth=require_scopes("titanic:survival:read"))
    def get_survival_rate(group_by: SurvivalGroupBy, ctx: Context) -> list[SurvivalRate]:
        """Return Titanic survival figures aggregated by a dimension.

        Groups all passenger observations by ``group_by`` and returns one entry
        per group, each with the number of passengers in that group and their
        survival rate (a fraction between 0.0 and 1.0).

        Args:
            group_by: Dimension to group passengers by before computing survival figures.
        """
        repository: TitanicRepository = ctx.lifespan_context
        return repository.get_survival_rate(group_by)

    return mcp


def main() -> None:
    settings = AuthSettings.from_env()
    # Base scope every agent must carry, so a tool that forgets its own
    # require_scopes is not silently open. Per-tool scopes are enforced on top.
    # audience ties tokens to this specific MCP server: a token minted for a
    # different service in the same realm is rejected.
    auth = KeycloakAuthProvider(
        realm_url=settings.realm_url,
        base_url=settings.base_url,
        required_scopes=["titanic:access"],
        audience="titanic-mcp",
    )
    mcp = build_server(SqlTitanicRepository.from_env, auth=auth)
    host = os.getenv("MCP_HOST", "127.0.0.1")
    uvicorn.run(mcp.http_app(transport="http"), host=host, port=8000)


if __name__ == "__main__":
    main()
