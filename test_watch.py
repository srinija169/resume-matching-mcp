
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = Path(__file__).with_name(
        "filesystem_mcp_server.py"
    )

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server)]
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            print("MCP connected successfully!")
            print("Watching resumes folder for 30 seconds...")

            result = await session.call_tool(
                "watch_directory",
                {
                    "wait_seconds": 30,
                    "poll_interval": 1
                }
            )

            for item in result.content:
                if hasattr(item, "text"):
                    print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
