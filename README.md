# Resume Matching Agent with MCP + LangGraph

A beginner-friendly reference implementation for the MCP assignment. It includes:
- A Python MCP filesystem server using the official `mcp` Python SDK and stdio transport.
- MCP resources for listing resumes and reading an individual resume.
- MCP tools: `list_files`, `read_file`, `batch_process`, `watch_directory`, and `get_server_config`.
- A LangGraph workflow that discovers MCP tools, retrieves resumes through MCP, then scores and ranks candidates.
- PDF, DOCX, and TXT text extraction.

> This is an educational baseline. The keyword-overlap score is not a validated hiring assessment. Do not use it as the sole basis for employment decisions. Add human review, privacy controls, access control, audit logging, retention policies, and bias testing before production use.

## 1. Requirements

- Python 3.10+
- Install dependencies:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Add resumes

Put `.pdf`, `.docx`, or `.txt` files in `resumes/`. Two sample TXT files are included.

## 3. Run the MCP server

```bash
python filesystem_mcp_server.py
```

The server uses stdio, so it may appear to wait silently. That is expected: it communicates using MCP JSON-RPC messages over stdin/stdout. Stop it with Ctrl+C. The LangGraph agent can also launch the server automatically.

## 4. Run the matching agent

In another terminal:

```bash
python matching_agent.py --job-file job_description.txt
```

Or pass a job description directly:

```bash
python matching_agent.py --job "Python developer with SQL, APIs, Git and Docker experience"
```

The agent starts the MCP server as a subprocess, initializes an MCP client session, discovers tools, calls `list_files` and `batch_process`, then ranks candidates.

## 5. MCP capabilities

### Resources
- `resumes://list` — JSON list of supported resume filenames.
- `resume://{filename}` — extracted text for one resume.

### Tools
- `list_files()` — discover resume files.
- `read_file(filename)` — extract one resume.
- `batch_process(filenames=None)` — process many resumes independently.
- `watch_directory(wait_seconds=30, poll_interval=2.0)` — detect newly added files during a bounded watch window.
- `get_server_config()` — report non-secret server configuration.

The server is implemented with FastMCP, which handles MCP's JSON-RPC protocol, initialization, discovery, and stdio framing. It is not a hand-written imitation of MCP.

## 6. Tests

```bash
python -m unittest discover -s tests -v
```

## 7. Configuration

By default, resumes are read from the local `resumes/` folder. Override it with:

```bash
# macOS/Linux
export RESUME_DIR="/absolute/path/to/resumes"
python matching_agent.py --job-file job_description.txt

# Windows PowerShell
$env:RESUME_DIR="C:\path\to\resumes"
python matching_agent.py --job-file job_description.txt
```

## 8. Workflow diagram

See `diagrams/mcp_workflow.mmd`. You can preview the Mermaid diagram in GitHub or a Mermaid editor.

## 9. Demo video plan (5–6 minutes)

1. Introduce the problem and architecture (0:00–0:40).
2. Show `filesystem_mcp_server.py`, its resources and tools (0:40–1:40).
3. Explain MCP initialization and discovery; run the server (1:40–2:30).
4. Show `matching_agent.py` and its LangGraph nodes (2:30–3:30).
5. Run the agent and explain batch processing and ranking (3:30–4:40).
6. Demonstrate directory watching in a second terminal or small Python MCP client (4:40–5:20).
7. Run tests and show the GitHub repository (5:20–6:00).

## 10. GitHub submission

Create a repository named `resume-matching-mcp`, then:

```bash
git init
git add .
git commit -m "Build MCP resume matching agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-matching-mcp.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Record the demo and add its link to this README before submitting.
