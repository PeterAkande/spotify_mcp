"""MCP tools for playlist management operations."""

from typing import Optional, List, Dict, Any
import json
import logging

from mcp.server import FastMCP
from fastapi import HTTPException
from mcp.server.fastmcp.server import Context

from ..services import SpotifyService
from ..models import PlaylistCreateRequest, DataFormat
from ..dependencies import get_access_token, get_spotify_service


logger = logging.getLogger(__name__)


def register_playlist_tools(mcp: FastMCP):
    """Register playlist management tools with MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def spotify_get_user_playlists(
        ctx: Context,
        limit: int = 20,
        offset: int = 0,
        format: str = "compact"
    ) -> str:
        """Get current user's playlists.

        Args:
            ctx: MCP context
            limit: Maximum number of playlists to return (1-50)
            offset: Offset for pagination
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with user's playlists
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            data_format = DataFormat(format.lower())
            
            result = await service.get_user_playlists(
                limit=limit,
                offset=offset,
                format=data_format
            )
            
            return json.dumps(result.model_dump(), indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting user playlists: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get user playlists: {str(e)}")

    @mcp.tool()
    async def spotify_create_playlist(
        ctx: Context,
        name: str,
        description: Optional[str] = None,
        public: bool = False,
        collaborative: bool = False
    ) -> str:
        """Create a new playlist for the current user.

        Args:
            ctx: MCP context
            name: Name of the new playlist
            description: Optional description for the playlist
            public: Whether the playlist should be public (default: False)
            collaborative: Whether the playlist should be collaborative (default: False)

        Returns:
            JSON string with created playlist details
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            request = PlaylistCreateRequest(
                name=name,
                description=description,
                public=public,
                collaborative=collaborative
            )

            result = await service.create_playlist(request)
            return json.dumps(result.model_dump(), indent=2, default=str)

        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create playlist: {str(e)}")

    @mcp.tool()
    async def spotify_get_playlist(
        ctx: Context,
        playlist_id: str,
        market: str = "US",
        format: str = "compact"
    ) -> str:
        """Get details of a specific playlist.

        Args:
            ctx: MCP context
            playlist_id: Spotify playlist ID
            market: Market/country code for track availability
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with playlist details
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            data_format = DataFormat(format.lower())
            
            # Get playlist details
            results = await service.get_playlist(playlist_id, market=market)
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse playlist based on format
            playlist = service._parse_object(results, "playlist", data_format)
            
            return json.dumps(playlist.model_dump() if hasattr(playlist, 'model_dump') else playlist, indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting playlist: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get playlist: {str(e)}")

    @mcp.tool()
    async def spotify_get_playlist_tracks(
        ctx: Context,
        playlist_id: str,
        market: str = "US",
        limit: int = 100,
        offset: int = 0,
        format: str = "compact"
    ) -> str:
        """Get tracks from a specific playlist.

        Args:
            ctx: MCP context
            playlist_id: Spotify playlist ID
            market: Market/country code for track availability
            limit: Maximum number of tracks to return (1-100)
            offset: Offset for pagination
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with playlist tracks
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            data_format = DataFormat(format.lower())
            
            # Get playlist tracks
            results = await service.get_playlist_tracks(
                playlist_id=playlist_id,
                market=market,
                limit=limit,
                offset=offset
            )
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse tracks based on format
            tracks = []
            for item in results["items"]:
                if item["track"]:  # Some tracks might be None (deleted tracks)
                    track = service._parse_object(item["track"], "track", data_format)
                    track_data = track.model_dump() if hasattr(track, 'model_dump') else track
                    # Add playlist-specific metadata
                    track_data["added_at"] = item.get("added_at")
                    track_data["added_by"] = item.get("added_by")
                    tracks.append(track_data)
            
            response = {
                "items": tracks,
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
            logger.error(f"Error getting playlist tracks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get playlist tracks: {str(e)}")

    @mcp.tool()
    async def spotify_add_tracks_to_playlist(
        ctx: Context,
        playlist_id: str,
        track_uris: List[str],
        position: Optional[int] = None
    ) -> str:
        """Add tracks to a playlist.

        Args:
            ctx: MCP context
            playlist_id: Spotify playlist ID
            track_uris: List of Spotify track URIs to add (max 100)
            position: Position to insert tracks (default: end of playlist)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            if len(track_uris) > 100:
                raise ValueError("Maximum 100 track URIs allowed per request")
            
            # Add tracks to playlist
            result = await service.add_tracks_to_playlist(
                playlist_id=playlist_id,
                items=track_uris,
                position=position
            )
            
            response = {
                "success": True,
                "message": f"Successfully added {len(track_uris)} tracks to playlist",
                "snapshot_id": result["snapshot_id"],
                "track_uris": track_uris
            }
            
            return json.dumps(response, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error adding tracks to playlist: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add tracks to playlist: {str(e)}")

    @mcp.tool()
    async def spotify_remove_tracks_from_playlist(
        ctx: Context,
        playlist_id: str,
        track_uris: List[str],
        snapshot_id: Optional[str] = None
    ) -> str:
        """Remove tracks from a playlist.

        Args:
            ctx: MCP context
            playlist_id: Spotify playlist ID
            track_uris: List of Spotify track URIs to remove
            snapshot_id: Playlist snapshot ID for optimistic locking

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Remove tracks from playlist
            result = await service.remove_tracks_from_playlist(
                playlist_id=playlist_id,
                items=track_uris,
                snapshot_id=snapshot_id
            )
            
            response = {
                "success": True,
                "message": f"Successfully removed {len(track_uris)} tracks from playlist",
                "snapshot_id": result["snapshot_id"],
                "track_uris": track_uris
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error removing tracks from playlist: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to remove tracks from playlist: {str(e)}")

    @mcp.tool()
    async def spotify_update_playlist_details(
        ctx: Context,
        playlist_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None,
        collaborative: Optional[bool] = None
    ) -> str:
        """Update playlist name, description, and other details.

        Args:
            ctx: MCP context
            playlist_id: Spotify playlist ID
            name: New playlist name
            description: New playlist description
            public: Whether playlist should be public
            collaborative: Whether playlist should be collaborative

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Build update parameters
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if public is not None:
                update_data["public"] = public
            if collaborative is not None:
                update_data["collaborative"] = collaborative
            
            if not update_data:
                raise ValueError("At least one field must be provided for update")
            
            # Update playlist details
            await service.update_playlist_details(playlist_id, **update_data)
            
            response = {
                "success": True,
                "message": "Playlist details updated successfully",
                "playlist_id": playlist_id,
                "updated_fields": list(update_data.keys())
            }
            
            return json.dumps(response, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating playlist details: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update playlist details: {str(e)}")

    

    @mcp.tool()
    async def spotify_unfollow_playlist(
        ctx: Context,
        playlist_id: str
    ) -> str:
        """Unfollow (remove) a playlist from user's library.

        Args:
            ctx: MCP context
            playlist_id: Spotify playlist ID to unfollow

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Unfollow playlist
            await service.unfollow_playlist(playlist_id)
            
            response = {
                "success": True,
                "message": "Successfully unfollowed playlist",
                "playlist_id": playlist_id
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error unfollowing playlist: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to unfollow playlist: {str(e)}")