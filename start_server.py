#!/usr/bin/env python3
"""Startup script for Spotify MCP Service."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from main import settings, logger
    import uvicorn

    def main():
        """Start Spotify MCP Service."""
        logger.info("🎵 Starting Spotify MCP Service...")
        logger.info(f"📍 Server: {settings.server_host}:{settings.server_port}")
        logger.info(f"🔧 Debug Mode: {settings.debug}")
        logger.info(f"🚀 Transport: {settings.transport_type}")
        logger.info(f"🔐 OAuth: Spotify Web API Token Validation")

        uvicorn.run(
            "main:app",
            host=settings.server_host,
            port=settings.server_port,
            reload=True,
            log_level=settings.log_level.lower(),
        )

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed: pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"❌ Startup error: {e}")
    sys.exit(1)