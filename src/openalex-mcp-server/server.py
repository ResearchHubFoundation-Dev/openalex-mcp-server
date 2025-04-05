""" 
OpenAlex MCP Server by ResearchHub Foundation 
=============================================

This module implements an MCP server for interacting with OpenAlex

"""

import logging
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from urllib.parse import quote
from mcp.server import Server
from mcp.server.models import InitializationOptions, ResourceTemplate
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ContentItem, ResourceContents

from .config import Settings

# Initialize settings and logging
settings = Settings()
logger = logging.getLogger("openalex-mcp-server")
logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Create server instance
server = Server(settings.APP_NAME)

# Helper function to format paper details
def format_paper_details(paper: Dict[str, Any]) -> str:
    """Format a paper's details into a readable markdown string"""
    try:
        if not paper:
            raise ValueError("Invalid paper data")

        # Safety checks and default values
        title = paper.get("title", "Untitled Paper")
        year = paper.get("publication_year", "Year unknown")
        citations = paper.get("cited_by_count", 0)
        
        # Format authors list with truncation for very long lists
        authorships_list = paper.get("authorships", [])
        author_limit = 20  # Limit number of authors to display
        
        authors = "No author information available"
        author_truncation_note = ""
        
        if authorships_list and len(authorships_list) > 0:
            displayed_authorships = authorships_list[:author_limit]
            truncated = len(authorships_list) > author_limit
            
            authors_list = []
            for authorship in displayed_authorships:
                if not authorship.get("author"):
                    authors_list.append("Unknown Author")
                    continue
                
                author = authorship["author"].get("display_name", "Unknown Author")
                institutions = authorship.get("institutions", [])
                institution = institutions[0].get("display_name") if institutions else None
                
                if institution:
                    authors_list.append(f"{author} ({institution})")
                else:
                    authors_list.append(author)
            
            authors = ", ".join(authors_list)
            
            if truncated:
                remaining_count = len(authorships_list) - author_limit
                author_truncation_note = f"\n\n*Note: This paper has {len(authorships_list)} authors. Showing first {author_limit} only.*"
        
        # Format access information
        open_access = paper.get("open_access", {})
        is_oa = open_access.get("is_oa", False)
        oa_url = open_access.get("oa_url", "")
        
        if is_oa:
            access_info = f"Open Access: Yes{f' (URL: {oa_url})' if oa_url else ''}"
        else:
            access_info = "Open Access: No"

        # Format journal/venue information
        primary_location = paper.get("primary_location", {})
        source = primary_location.get("source", {})
        venue = source.get("display_name", "Unknown Venue") if source else "Unknown Venue"
        
        # Handle potentially long abstracts
        abstract = paper.get("abstract", "No abstract available")
        max_abstract_length = 5000  # Reasonable limit for abstract length
        truncated_abstract = abstract
        abstract_truncation_note = ""
        
        if len(abstract) > max_abstract_length:
            truncated_abstract = abstract[:max_abstract_length] + "..."
            abstract_truncation_note = "\n\n*Note: Abstract has been truncated due to length.*"
        
        # Build links section
        links = []
        landing_page_url = primary_location.get("landing_page_url")
        doi = paper.get("doi")
        
        if landing_page_url:
            links.append(f"- [Publication Page]({landing_page_url})")
        if doi:
            links.append(f"- [DOI Link](https://doi.org/{doi})")
        
        links_section = "\n".join(links) if links else "No links available"
    
        # Build the formatted paper details
        return f"""# {title}

## Publication Information
- **Year:** {year}
- **Venue:** {venue}
- **DOI:** {paper.get("doi", "Not available")}
- **Citations:** {citations}
- **{access_info}**

## Authors
{authors}{author_truncation_note}

## Abstract
{truncated_abstract}{abstract_truncation_note}

## Links
{links_section}
"""
    except Exception as e:
        logger.error(f"Error formatting paper details: {e}")
        return "Error: Unable to format paper details. This may be due to unexpected data structure from the API."

# Helper function to search papers via OpenAlex API
async def search_papers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for papers in OpenAlex API
    
    Args:
        query: Search query for finding papers
        limit: Maximum number of results to return
        
    Returns:
        List of paper objects from OpenAlex API
    """
    try:
        # Validate inputs
        if not query or query.strip() == "":
            raise ValueError("Search query cannot be empty")
        
        # Cap the limit to avoid excessive data
        safe_limit = min(max(1, limit), 50)
        
        # Email for polite API usage (optional)
        email = "researcher@example.com"
        
        # Build and encode the query URL
        encoded_query = quote(query)
        url = f"https://api.openalex.org/works?search={encoded_query}&per_page={safe_limit}&sort=cited_by_count:desc&mailto={email}"
        
        logger.info(f'Searching OpenAlex for: "{query}" (limit: {safe_limit})')
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, 
                headers={'User-Agent': 'OpenAlexMCPServer/1.0'},
                timeout=15.0  # 15 second timeout
            ) as response:
                if response.status == 404:
                    logger.warning(f"No results found for query: {query}")
                    return []
                
                if not response.ok:
                    raise ValueError(f"OpenAlex API error: {response.status} {response.reason}")
                
                data = await response.json()
                
                # Handle empty results case
                if not data.get("results") or len(data["results"]) == 0:
                    logger.info(f'No results found for query: "{query}"')
                    return []
                
                return data["results"]
    except asyncio.TimeoutError:
        logger.error("Request timeout: The OpenAlex API took too long to respond")
        return []
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        return []

# Function to generate a summary of search results
def generate_search_summary(query: str, papers: List[Dict[str, Any]]) -> str:
    """Generate a markdown summary of search results"""
    if not papers or len(papers) == 0:
        return f'No results found for query: "{query}"'
    
    summaries = []
    for i, paper in enumerate(papers):
        # Get authors
        authors = []
        for authorship in paper.get("authorships", [])[:3]:  # Limit to first 3 authors
            if authorship.get("author", {}).get("display_name"):
                authors.append(authorship["author"]["display_name"])
        
        author_text = ", ".join(authors)
        if len(paper.get("authorships", [])) > 3:
            author_text += " et al."
        
        # Format the summary
        summary = f"{i + 1}. **{paper.get('title', 'Untitled')}** ({paper.get('publication_year', 'N/A')})\n"
        summary += f"   Authors: {author_text}\n"
        summary += f"   Citations: {paper.get('cited_by_count', 0)}\n"
        summary += f"   Resource URI: paper://{paper.get('id', '')}"
        
        summaries.append(summary)
    
    return f'# Search Results for: "{query}"\n\n' + "\n\n".join(summaries)

@server.tool("search_papers")
async def search_papers_tool(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for papers matching the given query.
    
    Args:
        query: Search terms for finding relevant papers
        limit: Maximum number of results to return
        
    Returns:
        List of papers with basic metadata
    """
    logger.info(f"Searching papers with query: {query}, limit: {limit}")
    
    try:
        papers = await search_papers(query, limit)
        summary = generate_search_summary(query, papers)
        
        return {
            "content": [{"type": "text", "text": summary}]
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in search_papers_tool: {error_message}")
        return {
            "content": [{"type": "text", "text": f"Error searching papers: {error_message}"}],
            "isError": True
        }

@server.tool("search_papers_by_author")
async def search_papers_by_author(author: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for papers by a specific author.
    
    Args:
        author: Author name to search for
        limit: Maximum number of results to return
        
    Returns:
        List of papers by the specified author
    """
    logger.info(f"Searching papers by author: {author}, limit: {limit}")
    
    try:
        # Use the author: filter in OpenAlex API
        query = f'author.display_name:"{author}"'
        papers = await search_papers(query, limit)
        summary = generate_search_summary(f"Papers by {author}", papers)
        
        return {
            "content": [{"type": "text", "text": summary}]
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in search_papers_by_author: {error_message}")
        return {
            "content": [{"type": "text", "text": f"Error searching papers by author: {error_message}"}],
            "isError": True
        }

@server.tool("get_paper")
async def get_paper(paper_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific paper.
    
    Args:
        paper_id: The OpenAlex ID of the paper
        
    Returns:
        Detailed paper information
    """
    logger.info(f"Getting paper with ID: {paper_id}")
    
    try:
        # Clean the paper_id - typically they start with "W" followed by numbers
        clean_paper_id = paper_id.replace("https://", "").replace("http://", "")
        if "/" in clean_paper_id:
            clean_paper_id = clean_paper_id.split("/", 1)[1]
        
        logger.info(f"Fetching paper details for ID: {clean_paper_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.openalex.org/works/{clean_paper_id}",
                headers={'User-Agent': 'OpenAlexMCPServer/1.0'},
                timeout=15.0  # 15 second timeout
            ) as response:
                if response.status == 404:
                    return {
                        "content": [{"type": "text", "text": f"Paper not found: No paper exists with ID {clean_paper_id}"}],
                        "isError": True
                    }
                
                if not response.ok:
                    raise ValueError(f"OpenAlex API error: {response.status} {response.reason}")
                
                paper = await response.json()
                
                # Check if we got a valid paper object
                if not paper or not paper.get("id") or not paper.get("title"):
                    raise ValueError("Invalid or incomplete paper data received")
                
                paper_details = format_paper_details(paper)
                
                return {
                    "content": [{"type": "text", "text": paper_details}]
                }
    except asyncio.TimeoutError:
        error_message = "Request timeout: The OpenAlex API took too long to respond"
        logger.error(error_message)
        return {
            "content": [{"type": "text", "text": error_message}],
            "isError": True
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in get_paper: {error_message}")
        return {
            "content": [{"type": "text", "text": f"Error fetching paper: {error_message}"}],
            "isError": True
        }

# Define paper resource template for accessing individual papers
@server.resource("paper", ResourceTemplate("paper://{paper_id}"))
async def paper_resource(uri: str, params: Dict[str, str]) -> ResourceContents:
    """Retrieve a paper as a resource by its ID"""
    paper_id = params.get("paper_id")
    
    # Validate the paper_id format
    if not paper_id or not isinstance(paper_id, str):
        return ResourceContents(
            contents=[{
                "uri": uri,
                "text": "Error: Invalid paper ID format",
                "mime_type": "text/plain"
            }]
        )
    
    # Clean the paper_id - typically they start with "W" followed by numbers
    clean_paper_id = paper_id.replace("https://", "").replace("http://", "")
    if "/" in clean_paper_id:
        clean_paper_id = clean_paper_id.split("/", 1)[1]
    
    try:
        logger.info(f"Fetching paper resource for ID: {clean_paper_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.openalex.org/works/{clean_paper_id}",
                headers={'User-Agent': 'OpenAlexMCPServer/1.0'},
                timeout=15.0  # 15 second timeout
            ) as response:
                if response.status == 404:
                    return ResourceContents(
                        contents=[{
                            "uri": uri,
                            "text": f"Paper not found: No paper exists with ID {clean_paper_id}",
                            "mime_type": "text/plain"
                        }]
                    )
                
                if not response.ok:
                    raise ValueError(f"OpenAlex API error: {response.status} {response.reason}")
                
                paper = await response.json()
                
                # Check if we got a valid paper object
                if not paper or not paper.get("id") or not paper.get("title"):
                    raise ValueError("Invalid or incomplete paper data received")
                
                paper_details = format_paper_details(paper)
                
                return ResourceContents(
                    contents=[{
                        "uri": uri,
                        "text": paper_details,
                        "mime_type": "text/markdown"
                    }]
                )
    except asyncio.TimeoutError:
        error_message = "Request timeout: The OpenAlex API took too long to respond"
        logger.error(error_message)
        return ResourceContents(
            contents=[{
                "uri": uri,
                "text": error_message,
                "mime_type": "text/plain"
            }]
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error retrieving paper resource {clean_paper_id}: {error_message}")
        return ResourceContents(
            contents=[{
                "uri": uri,
                "text": f"Error fetching paper: {error_message}",
                "mime_type": "text/plain"
            }]
        )

@server.prompt("find_papers_by_author")
def find_papers_by_author_prompt(author_name: str, limit: Optional[int] = 10) -> Dict[str, Any]:
    """Generate a prompt to find papers by a specific author"""
    limit_val = min(max(1, limit or 10), 50)  # Ensure limit is between 1 and 50
    
    return {
        "messages": [{
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Please search for research papers written by {author_name}. List the top {limit_val} papers by citation count and briefly describe their contribution to the field."
            }
        }]
    }

@server.prompt("find_recent_papers")
def find_recent_papers_prompt(
    topic: str, 
    year_from: Optional[int] = None, 
    year_to: Optional[int] = None
) -> Dict[str, Any]:
    """Generate a prompt to find recent papers on a specific topic"""
    prompt_text = f'Please search for recent research papers about "{topic}"'
    
    if year_from and year_to:
        prompt_text += f" published between {year_from} and {year_to}"
    elif year_from:
        prompt_text += f" published since {year_from}"
    elif year_to:
        prompt_text += f" published up to {year_to}"
    
    prompt_text += ". Summarize the key findings and trends in this research area."
    
    return {
        "messages": [{
            "role": "user",
            "content": {
                "type": "text",
                "text": prompt_text
            }
        }]
    }

# Server initialization and startup
def start_server():
    """Start the MCP server"""
    server_options = InitializationOptions(
        name=f"{settings.APP_NAME}",
        version="1.0.0",
        description="MCP server for accessing OpenAlex academic data",
        notification_options=NotificationOptions(
            show_tool_calls=True,
            show_tool_errors=True
        )
    )
    
    logger.info("Starting OpenAlex MCP Server...")
    stdio_server(server, server_options)
    logger.info("OpenAlex MCP Server connected and running.")

if __name__ == "__main__":
    start_server()