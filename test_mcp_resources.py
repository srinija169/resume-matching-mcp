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

            print("\n--- MCP RESOURCES ---")
            resources = await session.list_resources()

            for resource in resources.resources:
                print(resource.uri)

            print("\n--- RESOURCE TEMPLATES ---")
            templates = await session.list_resource_templates()

            for template in templates.resourceTemplates:
                print(template.uriTemplate)

            print("\n--- READ RESUME LIST RESOURCE ---")
            result = await session.read_resource(
                "resumes://list"
            )

            for item in result.contents:
                print(item.text)


if __name__ == "__main__":
    asyncio.run(main())