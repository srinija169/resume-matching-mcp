# Resume Matching Agent using MCP and LangGraph

A Python-based Resume Matching Agent that uses the **Model Context Protocol (MCP)** and **LangGraph** to discover, process, and rank resumes against a given job description.

This project demonstrates how an MCP filesystem server exposes tools and resources that can be accessed by an AI agent through an MCP client-server architecture.

## 1. Project Features

- Filesystem MCP server built using the official Python MCP SDK.
- MCP communication using JSON-RPC 2.0 over stdio.
- MCP resource and resource-template discovery.
- Resume file discovery and text extraction.
- Batch processing of multiple resumes.
- Directory watching for newly added resumes.
- LangGraph-based resume matching workflow.
- Support for PDF, DOCX, and TXT resume formats.
- Keyword-based candidate scoring and ranking.
- Automated unit and MCP integration tests.
- File access validation and error handling.

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
│   ├── test_parser.py
│   └── test_mcp_integration.py
│
└── diagrams/
    └── mcp_workflow.mmd
```

## 3. Technologies Used

- Python
- Model Context Protocol (MCP)
- Official Python MCP SDK / FastMCP
- LangGraph
- JSON-RPC 2.0
- PyPDF
- python-docx
- unittest

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

**Windows PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 5. MCP Server Implementation

The project implements an MCP filesystem server using the official Python MCP SDK and FastMCP.

The server uses **stdio transport** for communication with the MCP client.

Run the server independently with:

```bash
python filesystem_mcp_server.py
```

The server may appear to wait silently because it communicates through standard input and output.

The matching agent can also launch the MCP server automatically as a subprocess. Therefore, manually starting another server instance is not required when running the agent.

The MCP SDK handles protocol initialization, JSON-RPC communication, tool discovery, resource discovery, and stdio transport.

## 6. MCP Resources

The server exposes the following resources:

| Resource URI | Description |
|---|---|
| `resumes://list` | Lists available resume files |
| `resume://{filename}` | Resource template for accessing an individual resume |

These resources allow MCP clients to discover available resume data and access individual resume contents.

## 7. MCP Tools

The server provides the following tools:

| Tool | Description |
|---|---|
| `list_files` | Lists supported resume files |
| `read_file` | Reads and extracts an individual resume |
| `batch_process` | Processes multiple resumes and returns individual success or error results |
| `watch_directory` | Detects newly added files during a bounded watch period |
| `get_server_config` | Returns server configuration information |

### Additional Implementation Details

- Batch processing handles individual file errors without stopping the entire batch.
- File access includes path validation to prevent unauthorized path traversal.
- Directory watching uses bounded polling and detects newly added supported files.
- The watcher is a finite operation, not a continuously running background service.

## 8. LangGraph Resume Matching Agent

Run the matching agent:

```bash
python matching_agent.py
```

When prompted, paste a job description and press Enter.

The agent connects to the MCP server automatically through an MCP client session.

### Agent Workflow

1. Starts the MCP server as a subprocess.
2. Initializes the MCP client session.
3. Discovers available MCP tools.
4. Retrieves resume information through MCP tools.
5. Extracts resume text using the resume parser.
6. Processes candidate information through the LangGraph workflow.
7. Calculates keyword matching scores.
8. Ranks candidates based on their matching scores.

### Example Job Description

```text
We are looking for a Python Developer with strong Python
programming skills, experience with Django and Flask,
REST APIs, SQL databases, Git, and problem-solving abilities.
Knowledge of machine learning and data analysis is a plus.
```

### Example Output

The agent displays the discovered MCP tools and ranked candidates, including:

- Candidate filename
- Matching score
- Matched keywords
- Number of matched keywords
- Job-description keyword count

The matching score is based on keyword overlap and is intended as an educational baseline.

## 9. Testing

The project uses Python's built-in `unittest` framework.

Run all tests using:

```bash
python -m unittest discover -s tests -v
```

### Test Coverage

**Matching tests**
- Keyword score calculation.
- Candidate ranking order.

**Resume parser tests**
- TXT resume extraction.
- PDF resume extraction.
- DOCX resume extraction.
- Unsupported file type handling.

**MCP integration tests**
- MCP server initialization.
- Tool discovery.
- Resource discovery.
- Resource template discovery.
- Resume list resource access.
- File listing and reading.
- Batch processing with successful and failed files.
- Missing-file error handling.
- Path traversal protection.
- Server configuration.
- Directory watcher detection of newly added files.

**Latest test result: 8 tests passed successfully.**

## 10. Workflow Diagram

The project workflow diagram is available at:

`diagrams/mcp_workflow.mmd`

It illustrates the interaction between:

- LangGraph Agent
- MCP Client
- MCP Filesystem Server
- Filesystem and Resume Documents

The Mermaid diagram can be previewed in GitHub or a Mermaid-compatible editor.

## 11. GitHub Repository

**Repository:**  
https://github.com/srinija169/resume-matching-mcp

## 12. Limitations and Future Improvements

### Current Limitations

- Resume matching currently uses basic keyword overlap.
- The scoring mechanism is an educational baseline, not a validated hiring assessment.
- Generic keyword matches can affect scoring accuracy.
- Directory watching detects newly added files, not modifications to existing files.
- The project is intended for local educational use rather than production hiring decisions.

### Future Improvements

- Semantic resume matching using embeddings.
- Improved keyword extraction and filtering.
- Better handling of required and optional job skills.
- More detailed candidate matching explanations.
- Expanded test coverage and retrieval evaluation.
- Production-grade security, privacy protections, access controls, audit logging, and bias testing.

## 13. Conclusion

This project demonstrates how the Model Context Protocol can connect filesystem capabilities to a LangGraph-based agent.

It provides a practical implementation of MCP server development, JSON-RPC-based communication, tool and resource discovery, resume processing, batch operations, directory watching, and automated candidate matching.

The project highlights the use of MCP client-server architecture to make filesystem operations accessible to an AI agent through a structured and reusable interface.