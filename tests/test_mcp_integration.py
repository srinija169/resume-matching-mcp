import uuid
import asyncio
import json
import sys
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_DIR = Path(__file__).resolve().parents[1]
SERVER = PROJECT_DIR / "filesystem_mcp_server.py"


def get_tool_data(result):
    """Extract structured data from an MCP tool result."""
    if result.structuredContent is not None:
        return result.structuredContent

    for item in result.content:
        if hasattr(item, "text"):
            try:
                return json.loads(item.text)
            except json.JSONDecodeError:
                return item.text

    return None


class MCPIntegrationTests(unittest.IsolatedAsyncioTestCase):

    async def test_mcp_server_workflow(self):
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER)]
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:

                # 1. Initialize MCP connection
                initialized = await session.initialize()
                self.assertIsNotNone(initialized)

                # 2. Discover MCP tools
                tools = await session.list_tools()
                tool_names = {tool.name for tool in tools.tools}

                expected_tools = {
                    "list_files",
                    "read_file",
                    "batch_process",
                    "watch_directory",
                    "get_server_config",
                }
                self.assertTrue(expected_tools.issubset(tool_names))

                # 3. Discover resources
                resources = await session.list_resources()
                resource_uris = {
                    str(resource.uri)
                    for resource in resources.resources
                }
                self.assertIn("resumes://list", resource_uris)

                # 4. Discover resource templates
                templates = await session.list_resource_templates()
                template_uris = {
                    template.uriTemplate
                    for template in templates.resourceTemplates
                }
                self.assertIn("resume://{filename}", template_uris)

                # 5. Read resume list resource
                resource_result = await session.read_resource(
                    "resumes://list"
                )
                resource_data = json.loads(
                    resource_result.contents[0].text
                )
                self.assertIn("files", resource_data)

                # 6. Call list_files tool
                list_result = await session.call_tool("list_files", {})
                self.assertFalse(list_result.isError)

                list_data = get_tool_data(list_result)
                self.assertIsNotNone(list_data)
                self.assertIn("files", list_data)

                # 7. Read an existing resume
                if "sample_python_candidate.txt" in list_data["files"]:
                    read_result = await session.call_tool(
                        "read_file",
                        {"filename": "sample_python_candidate.txt"}
                    )
                    self.assertFalse(read_result.isError)

                    read_data = get_tool_data(read_result)
                    self.assertIn("Python", read_data["text"])

                # 8. Batch processing with one missing file
                batch_result = await session.call_tool(
                    "batch_process",
                    {
                        "filenames": [
                            "sample_python_candidate.txt",
                            "missing_candidate.txt",
                        ]
                    }
                )
                self.assertFalse(batch_result.isError)

                batch_data = get_tool_data(batch_result)
                self.assertEqual(batch_data["processed"], 2)
                self.assertEqual(batch_data["successful"], 1)
                self.assertEqual(batch_data["failed"], 1)

                # 9. Verify missing-file error handling
                missing_result = await session.call_tool(
                    "read_file",
                    {"filename": "missing_candidate.txt"}
                )
                self.assertTrue(missing_result.isError)

                # 10. Verify path traversal protection
                unsafe_result = await session.call_tool(
                    "read_file",
                    {"filename": "../outside.txt"}
                )
                self.assertTrue(unsafe_result.isError)

                # 11. Verify server configuration
                config_result = await session.call_tool(
                    "get_server_config",
                    {}
                )
                self.assertFalse(config_result.isError)

                config_data = get_tool_data(config_result)
                self.assertEqual(
                    config_data["server_name"],
                    "resume-filesystem"
                )
                self.assertEqual(config_data["transport"], "stdio")

    
    async def test_watch_directory_detects_new_file(self):
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER)]
        )

        resumes_dir = PROJECT_DIR / "resumes"
        filename = f"watch_test_{uuid.uuid4().hex}.txt"
        test_file = resumes_dir / filename

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:

                await session.initialize()

                async def create_file_during_watch():
                    await asyncio.sleep(0.75)
                    test_file.write_text(
                        "Test candidate with Python skills",
                        encoding="utf-8"
                    )

                try:
                    creator = asyncio.create_task(
                        create_file_during_watch()
                    )

                    result = await session.call_tool(
                        "watch_directory",
                        {
                            "wait_seconds": 5,
                            "poll_interval": 0.25
                        }
                    )

                    await creator

                    self.assertFalse(result.isError)

                    data = get_tool_data(result)

                    self.assertTrue(data["detected"])
                    self.assertIn(filename, data["new_files"])
                    self.assertEqual(
                        data["watch_duration_seconds"], 5
                    )

                finally:
                    if test_file.exists():
                        test_file.unlink()


if __name__ == "__main__":
    unittest.main()
