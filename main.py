"""Spotify MCP Service - Main application with OAuth 2.0 Token Validation."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from mcp.server import FastMCP
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spotify_mcp.core.config import TransportType, settings
from spotify_mcp.auth import spotify_token_verifier, SPOTIFY_SCOPES
from spotify_mcp.tools import (
    register_search_tools,
    register_library_tools,
    register_playlist_tools,
    register_playback_tools,
    register_analysis_tools,
)


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


# Create FastMCP server with OAuth validation
mcp = FastMCP(
    name=settings.mcp_server_name,
    instructions="Production Spotify MCP Service with OAuth 2.0 token validation",
    host=settings.server_host,
    port=settings.server_port,
    debug=settings.debug,
    # OAuth configuration
    token_verifier=spotify_token_verifier,
    auth=AuthSettings(
        issuer_url="https://accounts.spotify.com",  # Spotify OAuth issuer
        service_documentation_url="https://developer.spotify.com/documentation/web-api/",  # Spotify API docs
        required_scopes=settings.required_scopes,
        resource_server_url=settings.server_url,
        client_registration_options=ClientRegistrationOptions(
            enabled=False,  # Spotify doesn't support dynamic client registration
            valid_scopes=SPOTIFY_SCOPES,
            default_scopes=["user-read-private", "user-read-email"]  # Default to basic profile access
        ),
        revocation_options=RevocationOptions(
            enabled=True  # Support token revocation for security
        ),
    ),
)

# Register all tools
register_search_tools(mcp)
register_library_tools(mcp)
register_playlist_tools(mcp)
register_playback_tools(mcp)
register_analysis_tools(mcp)

# Create the MCP app based on transport type
if settings.transport_type == TransportType.SSE:
    mcp_app = mcp.sse_app()
else:
    mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Spotify MCP Service with OAuth 2.0 validation...")
    logger.info("OAuth issuer: https://accounts.spotify.com")
    logger.info("Token validation: Spotify Web API /v1/me endpoint")
    logger.info(f"Required scopes: {settings.required_scopes}")

    # Use the session manager's run() context manager
    async with mcp.session_manager.run():
        yield

    logger.info("Spotify MCP Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Spotify MCP Service",
    description="Production Spotify MCP Service with OAuth 2.0 support",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Spotify MCP Service",
        "description": "Production Spotify MCP Service with OAuth 2.0 token validation",
        "version": "0.1.0",
        "mcp_endpoint": "/mcp",
        "oauth_issuer": "https://accounts.spotify.com",
        "token_validation": "https://api.spotify.com/v1/me",
        "required_scopes": settings.required_scopes,
        "data_formats": {
            "default": "COMPACT",
            "supported": ["MINIMAL", "COMPACT", "FULL", "RAW"],
            "description": "All reading tools support DataFormat parameter. COMPACT gives you essential data for optimal performance."
        },
        "tools": {
            "search_discovery": [
                "search_music",

                "browse_categories",


                "get_new_releases"
            ],
            "library_management": [
                "get_saved_tracks",
                "get_saved_albums",
                "get_followed_artists",
                "get_recently_played",
                "get_top_items",
                "save_tracks",
                "remove_saved_tracks",
                "follow_artists"
            ],
            "playlist_management": [
                "get_user_playlists",
                "create_playlist",
                "get_playlist",
                "get_playlist_tracks",
                "add_tracks_to_playlist",
                "remove_tracks_from_playlist",
                "update_playlist_details",
                "unfollow_playlist"
            ],
            "playback_control": [
                "get_current_playback",
                "get_available_devices",
                "start_playback",
                "pause_playback",
                "skip_to_next",
                "skip_to_previous",
                "seek_to_position",
                "set_volume",
                "set_repeat_mode",
                "set_shuffle",
                "transfer_playback",
                "add_to_queue"
            ],
            "music_analysis": [
                "get_track_audio_features",
                "get_track_audio_analysis",
                "get_artist_info",
                "get_artist_top_tracks",
                "get_artist_albums",
                "get_album_tracks",
                "get_available_genre_seeds"
            ]
        },
        "authentication": {
            "type": "Bearer Token",
            "description": "Requires valid OAuth token from Spotify",
            "oauth_endpoint": "https://accounts.spotify.com/authorize",
            "scopes_required": settings.required_scopes,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": settings.mcp_server_name,
        "oauth_validation": "Spotify Web API /v1/me endpoint",
    }


# Mount MCP app
app.mount("", mcp_app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
