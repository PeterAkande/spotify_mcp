"""MCP tools for playback control operations."""

from typing import Optional, List, Dict, Any
import json
import logging

from mcp.server import FastMCP
from fastapi import HTTPException
from mcp.server.fastmcp.server import Context

from ..services import SpotifyService
from ..models import RepeatState
from ..dependencies import get_access_token, get_spotify_service


logger = logging.getLogger(__name__)


def register_playback_tools(mcp: FastMCP):
    """Register playback control tools with MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def spotify_get_current_playback(
        ctx: Context,
        market: str = "US",
        additional_types: Optional[List[str]] = None
    ) -> str:
        """Get information about current playback state.

        Args:
            ctx: MCP context
            market: Market/country code for track availability
            additional_types: Additional content types to include (episode, track)

        Returns:
            JSON string with current playback information
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            result = await service.get_current_playback()
            
            if result is None:
                return json.dumps({
                    "is_playing": False,
                    "message": "No active playback session found"
                }, indent=2)
            
            return json.dumps(result.model_dump(), indent=2, default=str)

        except Exception as e:
            logger.error(f"Error getting current playback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get current playback: {str(e)}")

    @mcp.tool()
    async def spotify_get_available_devices(
        ctx: Context
    ) -> str:
        """Get list of user's available Spotify devices.

        Args:
            ctx: MCP context

        Returns:
            JSON string with available devices
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            results = await service.get_devices()
            
            return json.dumps(results, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error getting available devices: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get available devices: {str(e)}")

    @mcp.tool()
    async def spotify_start_playback(
        ctx: Context,
        device_id: Optional[str] = None,
        context_uri: Optional[str] = None,
        uris: Optional[List[str]] = None,
        offset_position: Optional[int] = None,
        offset_uri: Optional[str] = None,
        position_ms: Optional[int] = None
    ) -> str:
        """Start or resume playback on user's active device.

        Args:
            ctx: MCP context
            device_id: Device ID to start playback on (uses active device if None)
            context_uri: Spotify URI of context (album, artist, playlist)
            uris: List of Spotify track URIs to play
            offset_position: Position in context to start playback (0-indexed)
            offset_uri: URI of track to start playback from
            position_ms: Position in milliseconds to start playback

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Build playback parameters
            kwargs = {}
            if device_id:
                kwargs["device_id"] = device_id
            if context_uri:
                kwargs["context_uri"] = context_uri
            if uris:
                kwargs["uris"] = uris
            if position_ms:
                kwargs["position_ms"] = position_ms
            
            # Handle offset parameter
            if offset_position is not None:
                kwargs["offset"] = {"position": offset_position}
            elif offset_uri:
                kwargs["offset"] = {"uri": offset_uri}
            
            # Use Spotipy directly
            await service.start_playback(**kwargs)
            
            response = {
                "success": True,
                "message": "Playback started successfully",
                "parameters": kwargs
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error starting playback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start playback: {str(e)}")

    @mcp.tool()
    async def spotify_pause_playback(
        ctx: Context,
        device_id: Optional[str] = None
    ) -> str:
        """Pause playback on user's active device.

        Args:
            ctx: MCP context
            device_id: Device ID to pause playback on (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            await service.pause_playback(device_id=device_id)
            
            response = {
                "success": True,
                "message": "Playback paused successfully"
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error pausing playback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to pause playback: {str(e)}")

    @mcp.tool()
    async def spotify_skip_to_next(
        ctx: Context,
        device_id: Optional[str] = None
    ) -> str:
        """Skip to next track in playback queue.

        Args:
            ctx: MCP context
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            await service.next_track(device_id=device_id)
            
            response = {
                "success": True,
                "message": "Skipped to next track"
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error skipping to next track: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to skip to next track: {str(e)}")

    @mcp.tool()
    async def spotify_skip_to_previous(
        ctx: Context,
        device_id: Optional[str] = None
    ) -> str:
        """Skip to previous track in playback queue.

        Args:
            ctx: MCP context
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            await service.previous_track(device_id=device_id)
            
            response = {
                "success": True,
                "message": "Skipped to previous track"
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error skipping to previous track: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to skip to previous track: {str(e)}")

    @mcp.tool()
    async def spotify_seek_to_position(
        ctx: Context,
        position_ms: int,
        device_id: Optional[str] = None
    ) -> str:
        """Seek to specific position in currently playing track.

        Args:
            ctx: MCP context
            position_ms: Position in milliseconds to seek to
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            if position_ms < 0:
                raise ValueError("Position must be non-negative")
            
            # Use Spotipy directly
            await service.seek_track(position_ms, device_id=device_id)
            
            response = {
                "success": True,
                "message": f"Seeked to position {position_ms}ms",
                "position_ms": position_ms
            }
            
            return json.dumps(response, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error seeking to position: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to seek to position: {str(e)}")

    @mcp.tool()
    async def spotify_set_volume(
        ctx: Context,
        volume_percent: int,
        device_id: Optional[str] = None
    ) -> str:
        """Set playback volume.

        Args:
            ctx: MCP context
            volume_percent: Volume percentage (0-100)
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            if not 0 <= volume_percent <= 100:
                raise ValueError("Volume must be between 0 and 100")
            
            # Use Spotipy directly
            await service.set_volume(volume_percent, device_id=device_id)
            
            response = {
                "success": True,
                "message": f"Volume set to {volume_percent}%",
                "volume_percent": volume_percent
            }
            
            return json.dumps(response, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to set volume: {str(e)}")

    @mcp.tool()
    async def spotify_set_repeat_mode(
        ctx: Context,
        state: str,
        device_id: Optional[str] = None
    ) -> str:
        """Set repeat mode for playback.

        Args:
            ctx: MCP context
            state: Repeat state - "track", "context", or "off"
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Validate repeat state
            repeat_state = RepeatState(state.lower())
            
            # Use Spotipy directly
            await service.set_repeat(repeat_state.value, device_id=device_id)
            
            response = {
                "success": True,
                "message": f"Repeat mode set to {repeat_state.value}",
                "repeat_state": repeat_state.value
            }
            
            return json.dumps(response, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error setting repeat mode: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to set repeat mode: {str(e)}")

    @mcp.tool()
    async def spotify_set_shuffle(
        ctx: Context,
        state: bool,
        device_id: Optional[str] = None
    ) -> str:
        """Toggle shuffle mode for playback.

        Args:
            ctx: MCP context
            state: Shuffle state - True to enable, False to disable
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            await service.set_shuffle(state, device_id=device_id)
            
            response = {
                "success": True,
                "message": f"Shuffle {'enabled' if state else 'disabled'}",
                "shuffle_state": state
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error setting shuffle mode: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to set shuffle mode: {str(e)}")

    @mcp.tool()
    async def spotify_transfer_playback(
        ctx: Context,
        device_ids: List[str],
        play: bool = False
    ) -> str:
        """Transfer playback to different device(s).

        Args:
            ctx: MCP context
            device_ids: List of device IDs to transfer playback to
            play: Whether to start playing after transfer (default: False)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            if not device_ids:
                raise ValueError("At least one device ID must be provided")
            
            # Use Spotipy directly
            await service.transfer_playback(device_ids, force_play=play)
            
            response = {
                "success": True,
                "message": f"Playback transferred to {len(device_ids)} device(s)",
                "device_ids": device_ids,
                "force_play": play
            }
            
            return json.dumps(response, indent=2)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error transferring playback: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to transfer playback: {str(e)}")

    @mcp.tool()
    async def spotify_add_to_queue(
        ctx: Context,
        uri: str,
        device_id: Optional[str] = None
    ) -> str:
        """Add track to playback queue.

        Args:
            ctx: MCP context
            uri: Spotify URI of track to add to queue
            device_id: Device ID to control (uses active device if None)

        Returns:
            JSON string with operation result
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            await service.add_to_queue(uri, device_id=device_id)
            
            response = {
                "success": True,
                "message": "Track added to queue successfully",
                "uri": uri
            }
            
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add to queue: {str(e)}")