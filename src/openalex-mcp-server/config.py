"""Configuration settings for the OpenAlex MCP Server"""

import sys
import logging 
from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings for the OpenAlex MCP Server"""
    APP_NAME: str = "openalex-mcp-server"
    VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    API_EMAIL: str = "dev@researchhub.foundation"  # Email for polite API usage
    
    # API settings
    API_BASE_URL: str = "https://api.openalex.org"
    API_TIMEOUT: float = 10.0  # Timeout in seconds
    
    class Config:
        env_prefix = "OPENALEX_"
        case_sensitive = True