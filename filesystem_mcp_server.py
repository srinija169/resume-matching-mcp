"""MCP filesystem server for a resume-matching project.

Run with: python filesystem_mcp_server.py
Transport: stdio (the standard MCP transport for local subprocess clients).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from utils.resume_parser import extract_resume_text

BASE_DIR = Path(os.getenv("RESUME_DIR", Path(__file__).parent / "resumes")).resolve()
BASE_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("resume-filesystem")


def _safe_path(filename: str) -> Path:
    """Resolve a filename inside BASE_DIR and reject path traversal."""
    candidate = (BASE_DIR / filename).resolve()
    if candidate != BASE_DIR and BASE_DIR not in candidate.parents:
        raise ValueError("Access outside the configured resume directory is not allowed.")
    return candidate


@mcp.resource("resumes://list")
def resume_list_resource() -> str:
    """A discoverable resource containing the names of supported resume files."""
    supported = {".pdf", ".docx", ".txt"}
    names = sorted(
        p.name for p in BASE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in supported
    )
    return json.dumps({"directory": str(BASE_DIR), "files": names}, indent=2)


@mcp.resource("resume://{filename}")
def resume_file_resource(filename: str) -> str:
    """Read a single resume as extracted text through an MCP resource URI."""
    path = _safe_path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"Resume not found: {filename}")
    return extract_resume_text(path)


@mcp.tool()
def list_files() -> dict[str, Any]:
    """List supported PDF, DOCX and TXT resumes in the configured directory."""
    supported = {".pdf", ".docx", ".txt"}
    names = sorted(
        p.name for p in BASE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in supported
    )
    return {"directory": str(BASE_DIR), "files": names, "count": len(names)}


@mcp.tool()
def read_file(filename: str) -> dict[str, Any]:
    """Extract text from one resume file."""
    path = _safe_path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"Resume not found: {filename}")
    return {"filename": path.name, "text": extract_resume_text(path)}


@mcp.tool()
def batch_process(filenames: list[str] | None = None) -> dict[str, Any]:
    """Extract multiple resumes; one bad file does not stop the whole batch."""
    if filenames is None:
        filenames = list_files()["files"]

    results = []
    for filename in filenames:
        try:
            path = _safe_path(filename)
            if not path.is_file():
                raise FileNotFoundError(f"Resume not found: {filename}")
            results.append({
                "filename": path.name,
                "status": "success",
                "text": extract_resume_text(path),
            })
        except Exception as exc:
            results.append({
                "filename": str(filename),
                "status": "error",
                "error": str(exc),
            })
    return {
        "processed": len(results),
        "successful": sum(item["status"] == "success" for item in results),
        "failed": sum(item["status"] == "error" for item in results),
        "results": results,
    }


@mcp.tool()
def watch_directory(
    wait_seconds: int = 30,
    poll_interval: float = 2.0,
) -> dict[str, Any]:
    """Watch for newly added resumes for a bounded period, then return the new files.

    This is a finite MCP tool call rather than an indefinitely running process.
    For production deployments, replace polling with OS-native file notifications.
    """
    wait_seconds = max(1, min(int(wait_seconds), 300))
    poll_interval = max(0.25, min(float(poll_interval), 10.0))
    supported = {".pdf", ".docx", ".txt"}

    def current_files() -> set[str]:
        return {
            p.name for p in BASE_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in supported
        }

    before = current_files()
    deadline = time.monotonic() + wait_seconds
    new_files: set[str] = set()

    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        new_files = current_files() - before
        if new_files:
            break

    return {
        "directory": str(BASE_DIR),
        "new_files": sorted(new_files),
        "detected": bool(new_files),
        "watch_duration_seconds": wait_seconds,
    }


@mcp.tool()
def get_server_config() -> dict[str, Any]:
    """Return non-secret runtime configuration for diagnostics."""
    return {
        "server_name": "resume-filesystem",
        "resume_directory": str(BASE_DIR),
        "supported_extensions": [".pdf", ".docx", ".txt"],
        "transport": "stdio",
    }


if __name__ == "__main__":
    # FastMCP serves the MCP JSON-RPC protocol over stdio.
    mcp.run(transport="stdio")
