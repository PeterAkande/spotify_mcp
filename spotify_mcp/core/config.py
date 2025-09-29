"""Core configuration and settings for Spotify MCP service."""

from enum import StrEnum
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class TransportType(StrEnum):
    """Transport types for MCP server."""
    SSE = "sse"
    STREAMABLE_HTTP = "streamble_http"


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=8001, description="Server port")
    server_url: str = Field(
        default="http://localhost:8001", 
        description="This server's URL for resource validation"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # MCP Configuration
    mcp_server_name: str = Field(default="spotify_mcp", description="MCP server name")
    transport_type: TransportType = Field(
        default=TransportType.STREAMABLE_HTTP, 
        description="Transport type for MCP server"
    )

    # Spotify Configuration
    spotify_api_base_url: str = Field(
        default="https://api.spotify.com/v1", 
        description="Spotify API base URL"
    )
    spotify_token_validation_endpoint: str = Field(
        default="https://api.spotify.com/v1/me",
        description="Spotify token validation endpoint"
    )
    
    required_scopes: List[str] = Field(
        default=[
            "user-read-private",
            "user-read-email",
            "user-library-read",
            "user-library-modify",
            "playlist-read-private",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-read-playback-state",
            "user-modify-playback-state",
            "user-read-recently-played",
            "user-top-read"
        ],
        description="Required Spotify OAuth scopes",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        description="Log format"
    )


# Global settings instance
settings = Settings()