"""Configuration settings for the OpenAlex MCP Server"""

import sys
import logging 
from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings for the OpenAlex MCP Server"""
    APP_NAME: str = "openalex-mcp-server"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_prefix = "OPENALEX_"
        case_sensitive = True
