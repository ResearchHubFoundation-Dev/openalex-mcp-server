# OpenAlex MCP Server

An open source implementation of OpenAlex MCP Server providing structured access to worldwide academic literature for AI Agents.

by ResearchHub Foundation 2025
## Overview

This server implements the Model Configuration Protocol (MCP) to connect AI assistants with the OpenAlex database, allowing them to search, retrieve, and analyze academic papers, researchers, institutions, and related scholarly information.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/openalex-mcp-server.git
cd openalex-mcp-server

# Install dependencies
pip install -e .
```

## Usage

```bash
# Start the MCP server
python -m openalex-mcp-server
```

## Requirements

- Python 3.10+
- Dependencies:
  - httpx
  - mcp

## Features

- Search academic papers across various disciplines
- Retrieve metadata about papers, authors, institutions, etc.
- Access citation networks and bibliographic information
- Structured data for easy consumption by AI agents

## License

See the [LICENSE](LICENSE) file for details.

