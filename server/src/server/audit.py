import time

from fastmcp.server.dependencies import get_access_token
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from fastmcp.utilities.logging import get_logger
from mcp.types import CallToolRequestParams

logger = get_logger("audit")


def _agent() -> str:
    token = get_access_token()
    if token is None:
        return "anonymous"
    return token.client_id or "unknown"


class AuditMiddleware(Middleware):
    """Logs who called which tool, with what arguments, and how long it took.

    Records the query parameters but never the result content or size, so the
    audit trail stays free of returned data.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[CallToolRequestParams],
        call_next: CallNext[CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        agent = _agent()
        tool = context.message.name
        args = context.message.arguments
        start = time.perf_counter()
        try:
            result = await call_next(context)
            logger.info(
                "tool_call agent=%s tool=%s args=%s duration_ms=%s",
                agent,
                tool,
                args,
                round((time.perf_counter() - start) * 1000, 2),
            )
            return result
        except Exception as exc:
            logger.error(
                "tool_error agent=%s tool=%s args=%s duration_ms=%s error=%s",
                agent,
                tool,
                args,
                round((time.perf_counter() - start) * 1000, 2),
                exc,
            )
            raise
