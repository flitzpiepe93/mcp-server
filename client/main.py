import asyncio

from fastmcp import Client


async def run() -> None:
    async with Client("http://127.0.0.1:8000/mcp/") as client:
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools] or '(none yet)'}")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
