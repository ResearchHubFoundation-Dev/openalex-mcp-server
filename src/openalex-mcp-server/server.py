""" 
OpenAlex MCP Server by ResearchHub Foundation 
=============================================

This module implements an MCP server for interacting with OpenAlex

"""

import logging
import mcp.types as types
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server

from .config import Settings

# Initialize settings and logging
settings = Settings()
logger = logging.getLogger("openalex-mcp-server")
logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Create server instance
server = Server(settings.APP_NAME)

# Define basic tool functions
@server.tool("openalex.search_papers")
async def search_papers(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for papers matching the given query.
    
    Args:
        query: Search terms for finding relevant papers
        limit: Maximum number of results to return
        
    Returns:
        List of papers with basic metadata
    """
    logger.info(f"Searching papers with query: {query}, limit: {limit}")
    # Basic implementation - would connect to OpenAlex API in production
    return [
        {"id": "W1", "title": "Example paper 1", "year": 2023},
        {"id": "W2", "title": "Example paper 2", "year": 2022},
    ][:limit]

@server.tool("openalex.get_paper")
async def get_paper(paper_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific paper.
    
    Args:
        paper_id: The OpenAlex ID of the paper
        
    Returns:
        Detailed paper information
    """
    logger.info(f"Getting paper with ID: {paper_id}")
    # Basic implementation - would connect to OpenAlex API in production
    return {
        "id": paper_id,
        "title": "Example paper details",
        "abstract": "This is an example abstract for demonstration purposes.",
        "year": 2023,
        "authors": ["Author 1", "Author 2"]
    }

# Server initialization and startup
def start_server():
    """Start the MCP server"""
    server_options = InitializationOptions(
        name=settings.APP_NAME,
        description="MCP server for accessing OpenAlex academic data",
        notification_options=NotificationOptions(
            show_tool_calls=True,
            show_tool_errors=True
        )
    )
    
    stdio_server(server, server_options)

if __name__ == "__main__":
    start_server()
