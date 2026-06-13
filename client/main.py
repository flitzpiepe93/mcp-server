import asyncio
import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"{name} is not set")
    return value


KEYCLOAK_TOKEN_URL = _require_env("KEYCLOAK_TOKEN_URL")
CLIENT_ID = _require_env("MCP_CLIENT_ID")
CLIENT_SECRET = _require_env("MCP_AGENT_SECRET")
MCP_URL = _require_env("MCP_URL")

logger = logging.getLogger("mcp-client")


def fetch_token() -> str:
    logger.info("Requesting token from %s (client_id=%s)", KEYCLOAK_TOKEN_URL, CLIENT_ID)
    response = httpx.post(
        KEYCLOAK_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    payload = response.json()
    logger.info("Token received (scope=%r)", payload.get("scope"))
    return payload["access_token"]


async def run() -> None:
    token = fetch_token()
    logger.info("Connecting to MCP server at %s", MCP_URL)
    async with Client(MCP_URL, auth=token) as client:
        tools = await client.list_tools()
        logger.info("Available tools: %s", [tool.name for tool in tools] or "(none yet)")

        logger.info("Calling get_survival_rate(group_by='sex')")
        result = await client.call_tool("get_survival_rate", {"group_by": "sex"})
        for row in result.data:
            logger.info("  %s", row)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(run())


if __name__ == "__main__":
    main()
