"""LangGraph resume-matching workflow that accesses files only through MCP.

Run:
    python matching_agent.py --job-file job_description.txt
    python matching_agent.py --job "Looking for a Python developer with SQL..."

The agent starts filesystem_mcp_server.py as an MCP stdio subprocess.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from utils.matching import rank_candidates


class MatchingState(TypedDict, total=False):
    job_description: str
    discovered_tools: list[str]
    resume_files: list[str]
    resume_results: list[dict[str, Any]]
    ranked_candidates: list[dict[str, Any]]
    error: str


def _decode_tool_result(result: Any) -> dict:
    """Decode the JSON text returned by FastMCP tools."""
    if getattr(result, "isError", False):
        raise RuntimeError("MCP tool returned an error")
    for item in getattr(result, "content", []):
        text = getattr(item, "text", None)
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured
    return {}


async def run_matching(job_description: str) -> dict:
    server_path = Path(__file__).with_name("filesystem_mcp_server.py")
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env={**os.environ, "RESUME_DIR": os.getenv(
            "RESUME_DIR", str(Path(__file__).with_name("resumes"))
        )},
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            async def discover_node(state: MatchingState) -> MatchingState:
                tools = await session.list_tools()
                return {"discovered_tools": [tool.name for tool in tools.tools]}

            async def retrieve_node(state: MatchingState) -> MatchingState:
                available = set(state.get("discovered_tools", []))
                if "list_files" not in available or "batch_process" not in available:
                    raise RuntimeError("MCP server is missing required tools.")
                listed = _decode_tool_result(await session.call_tool("list_files", {}))
                filenames = listed.get("files", [])
                processed = _decode_tool_result(
                    await session.call_tool("batch_process", {"filenames": filenames})
                )
                return {
                    "resume_files": filenames,
                    "resume_results": processed.get("results", []),
                }

            async def score_node(state: MatchingState) -> MatchingState:
                ranked = rank_candidates(
                    state["job_description"], state.get("resume_results", [])
                )
                return {"ranked_candidates": ranked}

            graph = StateGraph(MatchingState)
            graph.add_node("discover_mcp_tools", discover_node)
            graph.add_node("retrieve_resumes_via_mcp", retrieve_node)
            graph.add_node("score_and_rank", score_node)
            graph.add_edge(START, "discover_mcp_tools")
            graph.add_edge("discover_mcp_tools", "retrieve_resumes_via_mcp")
            graph.add_edge("retrieve_resumes_via_mcp", "score_and_rank")
            graph.add_edge("score_and_rank", END)

            app = graph.compile()
            return await app.ainvoke({"job_description": job_description})


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP-powered resume matching agent")
    parser.add_argument("--job", help="Job description text")
    parser.add_argument("--job-file", help="Path to a text file containing the job description")
    args = parser.parse_args()

    if args.job_file:
        job_description = Path(args.job_file).read_text(encoding="utf-8")
    elif args.job:
        job_description = args.job
    else:
        job_description = input("Paste the job description and press Enter:\n")

    result = asyncio.run(run_matching(job_description))
    print("\n=== MCP DISCOVERED TOOLS ===")
    print(", ".join(result.get("discovered_tools", [])))
    print("\n=== RANKED CANDIDATES ===")
    print(json.dumps(result.get("ranked_candidates", []), indent=2))


if __name__ == "__main__":
    main()
