"""MCP tools for user library management operations."""

from typing import Optional
import json
import logging

from mcp.server import FastMCP
from fastapi import HTTPException
from mcp.server.fastmcp.server import Context

from ..services import SpotifyService
from ..models import DataFormat, TimeRange
from ..dependencies import get_access_token, get_spotify_service, parse_comma_separated_list


logger = logging.getLogger(__name__)


def register_library_tools(mcp: FastMCP):
    """Register library management tools with MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def spotify_get_saved_tracks(
        ctx: Context,
        limit: int = 20,
        offset: int = 0,
        market: str = "US",
        format: str = "compact"
    ) -> str:
        """Get user's saved/liked tracks.

        Args:
            ctx: MCP context
            limit: Maximum number of tracks to return (1-50)
            offset: Offset for pagination
            market: Market/country code for track availability
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with saved tracks
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            data_format = DataFormat(format.lower())
            
            result = await service.get_saved_tracks(
                limit=limit,
                offset=offset,
                market=market,
                format=data_format
            )
            
            return json.dumps(result.model_dump(), indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting saved tracks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get saved tracks: {str(e)}")

    @mcp.tool()
    async def spotify_get_saved_albums(
        ctx: Context,
        limit: int = 20,
        offset: int = 0,
        market: str = "US",
        format: str = "compact"
    ) -> str:
        """Get user's saved albums.

        Args:
            ctx: MCP context
            limit: Maximum number of albums to return (1-50)
            offset: Offset for pagination
            market: Market/country code for album availability
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with saved albums
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            data_format = DataFormat(format.lower())
            
            # Get user's saved albums
            results = await service.get_saved_albums(
                limit=limit,
                offset=offset,
                market=market
            )
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse albums based on format
            albums = []
            for item in results["items"]:
                album = service._parse_object(item["album"], "album", data_format)
                albums.append(album.model_dump() if hasattr(album, 'model_dump') else album)
            
            response = {
                "items": albums,
                "total": results["total"],
                "limit": results["limit"],
                "offset": results["offset"],
                "next": results["next"],
                "previous": results["previous"]
            }
            
            return json.dumps(response, indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting saved albums: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get saved albums: {str(e)}")

    @mcp.tool()
    async def spotify_get_followed_artists(
        ctx: Context,
        limit: int = 20,
        after: Optional[str] = None,
        format: str = "compact"
    ) -> str:
        """Get artists that the user follows.

        Args:
            ctx: MCP context
            limit: Maximum number of artists to return (1-50)
            after: Last artist ID for pagination cursor
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with followed artists
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            data_format = DataFormat(format.lower())
            
            # Get followed artists
            results = await service.get_followed_artists(
                limit=limit,
                after=after
            )
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse artists based on format
            artists = []
            for artist in results["artists"]["items"]:
                parsed_artist = service._parse_object(artist, "artist", data_format)
                artists.append(parsed_artist.model_dump() if hasattr(parsed_artist, 'model_dump') else parsed_artist)
            
            response = {
                "items": artists,
                "total": results["artists"]["total"],
                "limit": results["artists"]["limit"],
                "after": results["artists"]["cursors"]["after"] if results["artists"]["cursors"] else None
            }
            
            return json.dumps(response, indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting followed artists: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get followed artists: {str(e)}")

    @mcp.tool()
    async def spotify_get_recently_played(
        ctx: Context,
        limit: int = 20,
        after: Optional[int] = None,
        before: Optional[int] = None
    ) -> str:
        """Get recently played tracks.

        Args:
            ctx: MCP context
            limit: Maximum number of tracks to return (1-50)
            after: Unix timestamp - return tracks played after this time
            before: Unix timestamp - return tracks played before this time

        Returns:
            JSON string with recently played tracks
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Build parameters
            kwargs = {"limit": limit}
            if after:
                kwargs["after"] = after
            if before:
                kwargs["before"] = before
            
            # Get recently played tracks
            results = await service.get_recently_played(
                limit=limit,
                after=after,
                before=before
            )
            
            return json.dumps(results, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error getting recently played: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get recently played: {str(e)}")

    @mcp.tool()
    async def spotify_get_top_items(
        ctx: Context,
        type: str,
        time_range: str = "medium_term",
        limit: int = 20,
        offset: int = 0
    ) -> str:
        """Get user's top artists or tracks.

        Args:
            ctx: MCP context
            type: Item type - "artists" or "tracks"
            time_range: Time range - "short_term" (~4 weeks), "medium_term" (~6 months), "long_term" (~years)
            limit: Maximum number of items to return (1-50)
            offset: Offset for pagination

        Returns:
            JSON string with top items
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Validate parameters
            if type not in ["artists", "tracks"]:
                raise ValueError("Type must be 'artists' or 'tracks'")
            
            time_range_enum = TimeRange(time_range.lower())
            
            result = await service.get_top_items(
                item_type=type,
                time_range=time_range_enum,
                limit=limit,
                offset=offset
            )
            
            return json.dumps(result.model_dump(), indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting top {type}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get top {type}: {str(e)}")

    @mcp.tool()
    async def spotify_save_tracks(
        ctx: Context,
        track_ids: str
    ) -> str:
        """Save tracks to user's library.

        Args:
            ctx: MCP context
            track_ids: Comma-separated string of Spotify track IDs to save (max 50)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Parse comma-separated track IDs string into list
            track_ids_list = parse_comma_separated_list(track_ids)
            if not track_ids_list:
                raise ValueError("At least one track ID is required")
            
            if len(track_ids_list) > 50:
                raise ValueError("Maximum 50 track IDs allowed per request")
            
            # Save tracks to user's library
            await service.save_tracks(track_ids_list)
            
            result = {
                "success": True,
                "message": f"Successfully saved {len(track_ids_list)} tracks",
                "track_ids": track_ids_list
            }
            
            return json.dumps(result, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error saving tracks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save tracks: {str(e)}")

    @mcp.tool()
    async def spotify_remove_saved_tracks(
        ctx: Context,
        track_ids: str
    ) -> str:
        """Remove tracks from user's saved library.

        Args:
            ctx: MCP context
            track_ids: Comma-separated string of Spotify track IDs to remove (max 50)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Parse comma-separated track IDs string into list
            track_ids_list = parse_comma_separated_list(track_ids)
            if not track_ids_list:
                raise ValueError("At least one track ID is required")
            
            if len(track_ids_list) > 50:
                raise ValueError("Maximum 50 track IDs allowed per request")
            
            # Remove tracks from user's library
            await service.remove_saved_tracks(track_ids_list)
            
            result = {
                "success": True,
                "message": f"Successfully removed {len(track_ids_list)} tracks from library",
                "track_ids": track_ids_list
            }
            
            return json.dumps(result, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error removing saved tracks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to remove saved tracks: {str(e)}")

    @mcp.tool()
    async def spotify_follow_artists(
        ctx: Context,
        artist_ids: str
    ) -> str:
        """Follow artists on Spotify.

        Args:
            ctx: MCP context
            artist_ids: Comma-separated string of Spotify artist IDs to follow (max 50)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Parse comma-separated artist IDs string into list
            artist_ids_list = parse_comma_separated_list(artist_ids)
            if not artist_ids_list:
                raise ValueError("At least one artist ID is required")
            
            if len(artist_ids_list) > 50:
                raise ValueError("Maximum 50 artist IDs allowed per request")
            
            # Follow artists
            await service.follow_artists(artist_ids_list)
            
            result = {
                "success": True,
                "message": f"Successfully followed {len(artist_ids_list)} artists",
                "artist_ids": artist_ids_list
            }
            
            return json.dumps(result, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error following artists: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to follow artists: {str(e)}")