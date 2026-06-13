import asyncio

from fastmcp import Client


async def run() -> None:
    async with Client("http://127.0.0.1:8000/mcp/") as client:
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools] or '(none yet)'}")

        result = await client.call_tool("get_survival_rate", {"group_by": "sex"})
        print("get_survival_rate(group_by='sex'):")
        for row in result.data:
            print(f"  {row}")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
