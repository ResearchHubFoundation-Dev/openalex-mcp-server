"""
OpenAlex MCP Server - Main Entry Point
======================================

This is the main entry point for the OpenAlex MCP Server.
"""

import sys
import logging
from .server import start_server
from .config import Settings

# Configure logging
settings = Settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(settings.APP_NAME)

def main():
    """Main entry point for the OpenAlex MCP Server"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()