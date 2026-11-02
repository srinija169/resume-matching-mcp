# Resume Matching Agent using MCP and LangGraph

A Python-based Resume Matching Agent that uses the **Model Context Protocol (MCP)** and **LangGraph** to discover, process, and rank resumes against a given job description.

This project demonstrates how an MCP filesystem server can expose tools and resources to an AI agent through the MCP client-server architecture.

## 1. Project Features

- Python MCP filesystem server using the official MCP SDK.
- MCP communication using JSON-RPC 2.0 over stdio.
- MCP resource discovery and reading.
- Resume file discovery and extraction.
- Batch processing of multiple resumes.
- Directory watching for newly added resumes.
- LangGraph workflow for resume matching and ranking.
- Supports PDF, DOCX, and TXT resume formats.
- Basic keyword-based candidate scoring.

## 2. Project Structure

```text
resume-matching-mcp/
│
├── filesystem_mcp_server.py
├── matching_agent.py
├── job_description.txt
├── requirements.txt
├── README.md
├── test_mcp_resources.py
├── test_watch.py
│
├── resumes/
│   ├── sample_python_candidate.txt
│   ├── sample_java_candidate.txt
│   └── new_candidate.txt
│
├── utils/
│   ├── resume_parser.py
│   └── matching.py
│
├── tests/
│   ├── test_matching.py
│   └── test_parser.py
│
└── diagrams/
    └── mcp_workflow.mmd
```

## 3. Technologies Used

- Python
- Model Context Protocol (MCP)
- FastMCP
- LangGraph
- JSON-RPC 2.0
- PyPDF
- Python-docx

## 4. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- VS Code or another Python IDE

### Step 1: Clone the repository

```bash
git clone https://github.com/srinija169/resume-matching-mcp.git
cd resume-matching-mcp
```

### Step 2: Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 5. Running the MCP Server

Run the following command:

```bash
python filesystem_mcp_server.py
```

The server uses stdio transport. It may appear to wait silently because it communicates through standard input and output.

The matching agent can also start the MCP server automatically as a subprocess.

**Note:** When running the matching agent, you do not need to manually start another server instance.

## 6. MCP Resources

The MCP server exposes the following resources:

| Resource URI | Description |
|---|---|
| `resumes://list` | Lists available resume files |
| `resume://{filename}` | Reads and extracts an individual resume |

## 7. MCP Tools

The server exposes these tools:

| Tool | Description |
|---|---|
| `list_files` | Lists supported resume files |
| `read_file` | Reads and extracts an individual resume |
| `batch_process` | Processes multiple resumes |
| `watch_directory` | Detects newly added files during a bounded watch period |
| `get_server_config` | Returns server configuration information |

The directory watcher uses polling and a configurable time window. It detects newly added files; it is not a continuous file-content modification monitor.

The official MCP SDK handles protocol initialization, JSON-RPC communication, tool discovery, resource discovery, and stdio transport.

## 8. Running the Resume Matching Agent

Run the agent using the provided job description:

```bash
python matching_agent.py --job-file job_description.txt
```

Alternatively, provide a job description directly:

```bash
python matching_agent.py --job "Python developer with SQL, APIs, Git and Docker experience"
```

### Agent Workflow

1. Connects to the MCP filesystem server.
2. Initializes the MCP client session.
3. Discovers available MCP tools.
4. Retrieves resumes using MCP tools.
5. Extracts resume text.
6. Processes resumes through the LangGraph workflow.
7. Calculates keyword matching scores.
8. Ranks candidates based on their matching scores.

## 9. Testing

Run the unit tests:

```bash
python -m unittest discover -s tests -v
```

The project includes tests for:

- Keyword matching score calculation.
- Candidate ranking order.
- TXT resume extraction.

Additional MCP functionality can be tested using:

```bash
python test_mcp_resources.py
```

```bash
python test_watch.py
```

## 10. Workflow Diagram

The project workflow is available in:

`diagrams/mcp_workflow.mmd`

The diagram illustrates communication between the LangGraph agent, MCP client, MCP server, and filesystem.

GitHub can preview the Mermaid diagram.

## 11. GitHub Repository

**Repository:** https://github.com/srinija169/resume-matching-mcp

## 12. Limitations and Future Improvements

- The current matching algorithm uses basic keyword overlap.
- The scoring mechanism is an educational baseline, not a validated hiring assessment.
- The directory watcher detects new files, not edits to existing files.
- Production deployment would require stronger security, access control, privacy protections, audit logging, and bias testing.
- Future improvements could include semantic matching using embeddings and more advanced resume analysis.

## 13. Conclusion

This project demonstrates how the Model Context Protocol can connect filesystem capabilities to a LangGraph-based agent.

It provides a practical example of MCP server development, tool discovery, resource discovery, batch processing, directory watching, and automated resume matching.