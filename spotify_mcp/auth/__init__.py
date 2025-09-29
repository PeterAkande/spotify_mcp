"""Authentication module for Spotify MCP service."""

from .spotify_auth import (
    SpotifyTokenInfo,
    SpotifyTokenValidator,
    SpotifyTokenVerifier,
    extract_bearer_token,
    spotify_token_validator,
    spotify_token_verifier,
    SPOTIFY_SCOPES,
    SPOTIFY_READ_ONLY_SCOPES,
    SPOTIFY_PLAYBACK_SCOPES,
)

__all__ = [
    "SpotifyTokenInfo",
    "SpotifyTokenValidator",
    "SpotifyTokenVerifier",
    "extract_bearer_token",
    "spotify_token_validator",
    "spotify_token_verifier",
    "SPOTIFY_SCOPES",
    "SPOTIFY_READ_ONLY_SCOPES",
    "SPOTIFY_PLAYBACK_SCOPES",
]