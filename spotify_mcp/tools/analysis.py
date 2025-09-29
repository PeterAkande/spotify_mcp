"""MCP tools for music analysis operations."""

from typing import List
import json
import logging

from mcp.server import FastMCP
from fastapi import HTTPException
from mcp.server.fastmcp.server import Context

from ..services import SpotifyService
from ..models import DataFormat, SpotifyObjectType
from ..dependencies import get_access_token, get_spotify_service


logger = logging.getLogger(__name__)


def register_analysis_tools(mcp: FastMCP):
    """Register music analysis tools with MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def spotify_get_track_audio_features(
        ctx: Context,
        track_ids: List[str]
    ) -> str:
        """Get audio features for one or more tracks.

        Args:
            ctx: MCP context
            track_ids: List of Spotify track IDs (max 100)

        Returns:
            JSON string with audio features
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            if len(track_ids) > 100:
                raise ValueError("Maximum 100 track IDs allowed per request")
            
            result = await service.get_track_audio_features(track_ids)
            
            # Convert to dict format for JSON serialization
            features_data = [features.model_dump() for features in result]
            
            return json.dumps(features_data, indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting audio features: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get audio features: {str(e)}")

    @mcp.tool()
    async def spotify_get_track_audio_analysis(
        ctx: Context,
        track_id: str
    ) -> str:
        """Get detailed audio analysis for a track.

        Args:
            ctx: MCP context
            track_id: Spotify track ID

        Returns:
            JSON string with detailed audio analysis
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Get audio analysis for track
            result = await service.get_audio_analysis(track_id)
            
            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error getting audio analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get audio analysis: {str(e)}")

    @mcp.tool()
    async def spotify_get_artist_info(
        ctx: Context,
        artist_ids: List[str],
        format: str = "compact"
    ) -> str:
        """Get detailed information about one or more artists.

        Args:
            ctx: MCP context
            artist_ids: List of Spotify artist IDs (max 50)
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with artist information
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            if len(artist_ids) > 50:
                raise ValueError("Maximum 50 artist IDs allowed per request")
            
            data_format = DataFormat(format.lower())
            
            # Use Spotipy directly
            results = await service.get_artists(artist_ids)
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse artists based on format
            artists = []
            for artist in results["artists"]:
                parsed_artist = service._parse_object(artist, SpotifyObjectType.ARTIST, data_format)
                artists.append(parsed_artist.model_dump() if hasattr(parsed_artist, 'model_dump') else parsed_artist)
            
            return json.dumps(artists, indent=2, default=str)

        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting artist info: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get artist info: {str(e)}")

    @mcp.tool()
    async def spotify_get_artist_top_tracks(
        ctx: Context,
        artist_id: str,
        market: str = "US"
    ) -> str:
        """Get an artist's most popular tracks.

        Args:
            ctx: MCP context
            artist_id: Spotify artist ID
            market: Market/country code for results

        Returns:
            JSON string with top tracks
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            
            # Use Spotipy directly
            results = await service.get_artist_top_tracks(artist_id, country=market)
            
            # Parse tracks
            tracks = []
            for track in results["tracks"]:
                parsed_track = service._parse_object(track, SpotifyObjectType.TRACK, DataFormat.COMPACT)
                tracks.append(parsed_track.model_dump() if hasattr(parsed_track, 'model_dump') else parsed_track)
            
            return json.dumps(tracks, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error getting artist top tracks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get artist top tracks: {str(e)}")



    @mcp.tool()
    async def spotify_get_artist_albums(
        ctx: Context,
        artist_id: str,
        include_groups: List[str] = None,
        market: str = "US",
        limit: int = 20,
        offset: int = 0,
        format: str = "compact"
    ) -> str:
        """Get an artist's albums.

        Args:
            ctx: MCP context
            artist_id: Spotify artist ID
            include_groups: List of album types to include (album, single, appears_on, compilation)
            market: Market/country code for results
            limit: Maximum number of albums to return (1-50)
            offset: Offset for pagination
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with artist albums
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            data_format = DataFormat(format.lower())
            
            # Default include groups
            if include_groups is None:
                include_groups = ["album", "single"]
            
            # Get artist albums
            results = await service.get_artist_albums(
                artist_id,
                album_type=None,
                country=market,
                limit=limit,
                offset=offset,
                include_groups=",".join(include_groups)
            )
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse albums based on format
            albums = []
            for album in results["items"]:
                parsed_album = service._parse_object(album, SpotifyObjectType.ALBUM, data_format)
                albums.append(parsed_album.model_dump() if hasattr(parsed_album, 'model_dump') else parsed_album)
            
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
            logger.error(f"Error getting artist albums: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get artist albums: {str(e)}")

    @mcp.tool()
    async def spotify_get_album_tracks(
        ctx: Context,
        album_id: str,
        market: str = "US",
        limit: int = 50,
        offset: int = 0,
        format: str = "compact"
    ) -> str:
        """Get tracks from an album.

        Args:
            ctx: MCP context
            album_id: Spotify album ID
            market: Market/country code for track availability
            limit: Maximum number of tracks to return (1-50)
            offset: Offset for pagination
            format: Response format (minimal, compact, full, raw)

        Returns:
            JSON string with album tracks
        """
        try:
            service = get_spotify_service(get_access_token(ctx))
            data_format = DataFormat(format.lower())
            
            # Get album tracks
            results = await service.get_album_tracks(
                album_id,
                limit=limit,
                offset=offset,
                market=market
            )
            
            if data_format == DataFormat.RAW:
                return json.dumps(results, indent=2, default=str)
            
            # Parse tracks based on format
            tracks = []
            for track in results["items"]:
                parsed_track = service._parse_object(track, SpotifyObjectType.TRACK, data_format)
                tracks.append(parsed_track.model_dump() if hasattr(parsed_track, 'model_dump') else parsed_track)
            
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
            logger.error(f"Error getting album tracks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get album tracks: {str(e)}")

