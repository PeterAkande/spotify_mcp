"""Dependency injection functions for MCP tools."""

from fastapi import HTTPException, Depends
from mcp.server.fastmcp.server import Context
from starlette.requests import Request

from .auth import SpotifyTokenInfo, extract_bearer_token, spotify_token_validator
from .services import SpotifyService


def get_access_token(ctx: Context) -> str:
    """Extract access token from MCP context.

    Args:
        ctx: MCP context containing request information

    Returns:
        Access token string

    Raises:
        HTTPException: If no valid token is found
    """
    if not ctx or not ctx.request_context:
        raise HTTPException(status_code=401, detail="No request context available")

    request: Request = ctx.request_context.request
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    return auth_header.replace("Bearer ", "")


async def get_validated_token(access_token: str = Depends(get_access_token)) -> SpotifyTokenInfo:
    """Validate access token with Spotify API.

    Args:
        access_token: Access token from request

    Returns:
        SpotifyTokenInfo if valid

    Raises:
        HTTPException: If token validation fails
    """
    try:
        token_info = await spotify_token_validator.validate_token(access_token)
        if not token_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return token_info
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


def get_spotify_service(access_token: str = Depends(get_access_token)) -> SpotifyService:
    """Create SpotifyService instance with validated token.

    Args:
        access_token: Validated access token

    Returns:
        SpotifyService instance

    Raises:
        HTTPException: If service creation fails
    """
    try:
        return SpotifyService(access_token)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Spotify service: {str(e)}")