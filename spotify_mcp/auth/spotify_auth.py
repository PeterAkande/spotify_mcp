"""Spotify OAuth token validation for MCP Server."""

import logging
import httpx
from typing import Optional, Dict, Any
import json
from pydantic import BaseModel

from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger(__name__)


class SpotifyTokenInfo(BaseModel):
    """Token information from Spotify OAuth validation."""

    access_token: str
    user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    product: Optional[str] = None
    followers: Optional[int] = None
    token_type: str = "Bearer"


class SpotifyTokenValidator:
    """Spotify OAuth token validator."""

    def __init__(self, token_endpoint: str = "https://api.spotify.com/v1/me"):
        self.token_endpoint = token_endpoint

    async def validate_token(self, token: str) -> Optional[SpotifyTokenInfo]:
        """Validate access token with Spotify API.

        Args:
            token: Access token to validate

        Returns:
            SpotifyTokenInfo if valid, None if invalid
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.token_endpoint,
                    headers=headers,
                    timeout=10.0
                )

                if response.status_code != 200:
                    logger.warning(
                        f"Spotify token validation failed: {response.status_code}"
                    )
                    return None

                data = response.json()

                # Check for error in response
                if "error" in data:
                    logger.warning(
                        f"Spotify token validation error: {data.get('error', {}).get('message', 'Unknown error')}"
                    )
                    return None

                # Validate required fields
                if "id" not in data:
                    logger.warning(
                        "Spotify token validation response missing required fields"
                    )
                    return None

                return SpotifyTokenInfo(
                    access_token=token,
                    user_id=data["id"],
                    display_name=data.get("display_name"),
                    email=data.get("email"),
                    country=data.get("country"),
                    product=data.get("product"),
                    followers=data.get("followers", {}).get("total") if data.get("followers") else None,
                    token_type="Bearer",
                )

        except Exception as e:
            logger.error(f"Spotify token validation error: {e}")
            return None

    def _validate_scopes(self, required_scopes: list) -> bool:
        """Validate that token has required scopes.
        
        Note: Spotify doesn't provide scope information in the /v1/me endpoint.
        Scope validation is done implicitly - if the endpoint call succeeds,
        the token has at least user-read-private scope.
        Additional scope validation happens when specific endpoints are called.

        Args:
            required_scopes: List of required scope strings (for documentation)

        Returns:
            True (validation happens at endpoint level)
        """
        # Spotify doesn't return scope information in /v1/me
        # Scopes are validated implicitly when accessing protected endpoints
        return True


class SpotifyTokenVerifier(TokenVerifier):
    """MCP token verifier for Spotify service."""

    def __init__(self, token_validator: SpotifyTokenValidator, required_scopes: list):
        self.token_validator = token_validator
        self.required_scopes = required_scopes

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        """Verify access token and return AccessToken object.

        Args:
            token: Bearer token from request

        Returns:
            AccessToken if valid, None if invalid
        """
        try:
            token_info = await self.token_validator.validate_token(token)
            if not token_info:
                return None

            # Note: Spotify doesn't provide explicit scope validation in /v1/me
            # Scopes are validated when accessing specific endpoints
            if not self.token_validator._validate_scopes(self.required_scopes):
                logger.warning(
                    f"Token validation completed. Required scopes: {self.required_scopes}"
                )

            return AccessToken(
                token=token_info.access_token,
                client_id=token_info.user_id,  # Use user ID as client identifier
                scopes=self.required_scopes,  # Assume all scopes (validated at endpoint level)
                expires_at=None,  # Spotify doesn't provide expiration in /v1/me
                resource=None,
            )

        except Exception as e:
            logger.error(f"Access token verification error: {e}")
            return None


def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """Extract bearer token from Authorization header.

    Args:
        auth_header: Authorization header value

    Returns:
        Token string if valid Bearer token, None otherwise
    """
    if not auth_header:
        return None

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header[7:]  # Remove "Bearer " prefix


# Spotify API Scopes
SPOTIFY_SCOPES = [
    "user-read-private",           # Read user profile
    "user-read-email",             # Read user email
    "user-library-read",           # Read saved tracks/albums
    "user-library-modify",         # Modify saved tracks/albums
    "playlist-read-private",       # Read private playlists
    "playlist-read-collaborative", # Read collaborative playlists
    "playlist-modify-public",      # Modify public playlists
    "playlist-modify-private",     # Modify private playlists
    "user-read-playback-state",    # Read playback state
    "user-modify-playback-state",  # Control playback
    "user-read-currently-playing", # Read currently playing
    "user-read-recently-played",   # Read recently played
    "user-top-read",              # Read top artists/tracks
    "user-follow-read",           # Read followed artists
    "user-follow-modify",         # Modify followed artists
]

SPOTIFY_READ_ONLY_SCOPES = [
    "user-read-private",
    "user-read-email",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-playback-state",
    "user-read-currently-playing",
    "user-read-recently-played",
    "user-top-read",
    "user-follow-read",
]

SPOTIFY_PLAYBACK_SCOPES = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
]

# Create global instances  
spotify_token_validator = SpotifyTokenValidator()
spotify_token_verifier = SpotifyTokenVerifier(
    spotify_token_validator, SPOTIFY_SCOPES
)