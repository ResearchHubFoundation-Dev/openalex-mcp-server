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


# from .config import Settings
# import all tools and prompt

# settings = Settings()
logger = logging.getLogger("openalex-mcp-server")
logger.setLevel(logging.INFO)
#server = Server(settings.APP_NAME)
