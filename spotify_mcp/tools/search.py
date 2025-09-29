"""MCP tools for search and discovery operations."""

from typing import Optional, List
import json
import logging

from mcp.server import FastMCP
from fastapi import HTTPException
from mcp.server.fastmcp.server import Context

from ..models import (
    SearchRequest,

    DataFormat,
    SpotifyObjectType,
)
from ..dependencies import get_access_token, get_spotify_service


logger = logging.getLogger(__name__)


def register_search_tools(mcp: FastMCP):
    """Register search and discovery tools with MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def spotify_search_music(
        ctx: Context,
        query: str,
        types: Optional[List[str]] = None,
        market: str = "US",
        limit: int = 20,
        offset: int = 0,
        format: str = "compact",
    ) -> str:
        """Search for music across Spotify's catalog.

        Args:
            ctx: MCP context
            query: Search query string
            types: List of object types to search (track, artist, album, playlist, show, episode)
            market: Market/country code for results (e.g., "US", "GB", "DE")
            limit: Maximum number of results per type (1-50)
            offset: Offset for pagination
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with search results
        """
        try:
            service = get_spotify_service(get_access_token(ctx))

            # Validate and convert parameters
            data_format = DataFormat(format.lower())
            search_types = (
                [SpotifyObjectType(t.lower()) for t in types]
                if types
                else [SpotifyObjectType.TRACK]
            )

            request = SearchRequest(
                query=query,
                types=search_types,
                market=market,
                limit=limit,
                offset=offset,
                format=data_format,
            )

            result = await service.search_music(request)
            return json.dumps(result.model_dump(), indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error searching music: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to search music: {str(e)}"
            )

    

    @mcp.tool()
    async def spotify_browse_categories(
        ctx: Context, country: str = "US", limit: int = 20, offset: int = 0
    ) -> str:
        """Browse Spotify's music categories.

        Args:
            ctx: MCP context
            country: Country code for localized categories
            limit: Maximum number of categories to return (1-50)
            offset: Offset for pagination

        Returns:
            JSON string with category list
        """
        try:
            service = get_spotify_service(get_access_token(ctx))

            results = await service.get_categories(
                country=country, limit=limit, offset=offset
            )

            return json.dumps(results, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error browsing categories: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to browse categories: {str(e)}"
            )

    @mcp.tool()
    async def spotify_get_new_releases(
        ctx: Context, country: str = "US", limit: int = 20, offset: int = 0
    ) -> str:
        """Get new album releases on Spotify.

        Args:
            ctx: MCP context
            country: Country code for localized results
            limit: Maximum number of albums to return (1-50)
            offset: Offset for pagination

        Returns:
            JSON string with new releases
        """
        try:
            service = get_spotify_service(get_access_token(ctx))

            # Get new releases
            results = await service.get_new_releases(
                country=country, limit=limit, offset=offset
            )

            return json.dumps(results, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error getting new releases: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to get new releases: {str(e)}"
            )
