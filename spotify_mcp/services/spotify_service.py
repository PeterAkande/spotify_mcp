"""Main Spotify service implementation."""

import logging
from typing import List, Optional, Dict, Any
import spotipy
from datetime import datetime

from ..models import (
    Track,
    Artist,
    Album,
    Playlist,
    PlaybackState,
    AudioFeatures,
    SearchRequest,

    PlaylistCreateRequest,
    DataFormat,
    SpotifyObjectType,
    TimeRange,
    SearchResponse,
    PaginatedResponse,
)
from ..auth import SpotifyTokenInfo
from ..core.config import settings

logger = logging.getLogger(__name__)


class SpotifyService:
    """Main service class for Spotify MCP operations."""

    def __init__(self, access_token: str):
        """Initialize Spotify service with user access token.
        
        Args:
            access_token: User's Spotify access token
        """
        self.access_token = access_token
        self.spotify = spotipy.Spotify(auth=access_token)  
    async def search_music(
        self, 
        request: SearchRequest
    ) -> SearchResponse:
        """Search for music across different Spotify object types.
        
        Args:
            request: Search request parameters
            
        Returns:
            SearchResponse with search results
        """
        try:
            # Convert enum types to strings for Spotipy
            types_str = ",".join([obj_type.value for obj_type in request.types])
            
            # Perform search
            results = self.spotify.search(
                q=request.query,
                type=types_str,
                market=request.market,
                limit=request.limit,
                offset=request.offset
            )
            
            # Parse results based on requested types
            response_data = {}
            total_results = 0
            
            for obj_type in request.types:
                key = f"{obj_type.value}s"  # tracks, artists, albums, playlists
                if key in results:
                    items = results[key]["items"]
                    total_results += results[key]["total"]
                    
                    # Parse items based on format
                    parsed_items = [
                        self._parse_object(item, obj_type, request.format)
                        for item in items
                    ]
                    response_data[key] = parsed_items
            
            return SearchResponse(
                **response_data,
                total_results=total_results,
                format_used=request.format
            )
            
        except Exception as e:
            logger.error(f"Error searching music: {e}")
            raise Exception(f"Failed to search music: {str(e)}")

    

    async def get_user_playlists(
        self, 
        limit: int = 20,
        offset: int = 0,
        format: DataFormat = DataFormat.COMPACT
    ) -> PaginatedResponse:
        """Get current user's playlists.
        
        Args:
            limit: Maximum number of playlists to return
            offset: Offset for pagination
            format: Response format
            
        Returns:
            PaginatedResponse with playlists
        """
        try:
            results = self.spotify.current_user_playlists(limit=limit, offset=offset)
            
            playlists = [
                self._parse_object(playlist, SpotifyObjectType.PLAYLIST, format)
                for playlist in results["items"]
            ]
            
            return PaginatedResponse(
                items=playlists,
                total=results["total"],
                limit=results["limit"],
                offset=results["offset"],
                next=results["next"],
                previous=results["previous"]
            )
            
        except Exception as e:
            logger.error(f"Error getting user playlists: {e}")
            raise Exception(f"Failed to get user playlists: {str(e)}")

    async def create_playlist(
        self,
        request: PlaylistCreateRequest
    ) -> Playlist:
        """Create a new playlist for the current user.
        
        Args:
            request: Playlist creation parameters
            
        Returns:
            Created Playlist object
        """
        try:
            # Get current user ID
            user = self.spotify.current_user()
            user_id = user["id"]
            
            # Create playlist
            result = self.spotify.user_playlist_create(
                user=user_id,
                name=request.name,
                public=request.public,
                collaborative=request.collaborative,
                description=request.description or ""
            )
            
            return self._parse_object(result, SpotifyObjectType.PLAYLIST, DataFormat.FULL)
            
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            raise Exception(f"Failed to create playlist: {str(e)}")

    async def get_current_playback(self) -> Optional[PlaybackState]:
        """Get current playback state.
        
        Returns:
            PlaybackState if music is playing, None if not
        """
        try:
            result = self.spotify.current_playback()
            
            if not result:
                return None
                
            return self._parse_playback_state(result)
            
        except Exception as e:
            logger.error(f"Error getting current playback: {e}")
            raise Exception(f"Failed to get current playback: {str(e)}")

    async def get_saved_tracks(
        self,
        limit: int = 20,
        offset: int = 0,
        market: str = "US",
        format: DataFormat = DataFormat.COMPACT
    ) -> PaginatedResponse:
        """Get user's saved tracks.
        
        Args:
            limit: Maximum number of tracks to return
            offset: Offset for pagination
            market: Market for track availability
            format: Response format
            
        Returns:
            PaginatedResponse with saved tracks
        """
        try:
            results = self.spotify.current_user_saved_tracks(
                limit=limit, 
                offset=offset, 
                market=market
            )
            
            tracks = [
                self._parse_object(item["track"], SpotifyObjectType.TRACK, format)
                for item in results["items"]
            ]
            
            return PaginatedResponse(
                items=tracks,
                total=results["total"],
                limit=results["limit"],
                offset=results["offset"],
                next=results["next"],
                previous=results["previous"]
            )
            
        except Exception as e:
            logger.error(f"Error getting saved tracks: {e}")
            raise Exception(f"Failed to get saved tracks: {str(e)}")

    async def get_top_items(
        self,
        item_type: str,
        time_range: TimeRange = TimeRange.MEDIUM_TERM,
        limit: int = 20,
        offset: int = 0
    ) -> PaginatedResponse:
        """Get user's top artists or tracks.
        
        Args:
            item_type: 'artists' or 'tracks'
            time_range: Time range for statistics
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            PaginatedResponse with top items
        """
        try:
            # Use the appropriate method based on item type
            if item_type == "tracks":
                results = self.spotify.current_user_top_tracks(
                    time_range=time_range.value,
                    limit=limit,
                    offset=offset
                )
            elif item_type == "artists":
                results = self.spotify.current_user_top_artists(
                    time_range=time_range.value,
                    limit=limit,
                    offset=offset
                )
            else:
                raise ValueError(f"Invalid item_type: {item_type}. Must be 'tracks' or 'artists'")
            
            obj_type = SpotifyObjectType.TRACK if item_type == "tracks" else SpotifyObjectType.ARTIST
            
            items = [
                self._parse_object(item, obj_type, DataFormat.COMPACT)
                for item in results["items"]
            ]
            
            return PaginatedResponse(
                items=items,
                total=results["total"],
                limit=results["limit"],
                offset=results["offset"],
                next=results["next"],
                previous=results["previous"]
            )
            
        except Exception as e:
            logger.error(f"Error getting top {item_type}: {e}")
            raise Exception(f"Failed to get top {item_type}: {str(e)}")

    async def get_track_audio_features(
        self,
        track_ids: List[str]
    ) -> List[AudioFeatures]:
        """Get audio features for tracks.
        
        Args:
            track_ids: List of Spotify track IDs (max 100)
            
        Returns:
            List of AudioFeatures objects
        """
        try:
            # Spotipy handles batching automatically
            results = self.spotify.audio_features(track_ids)
            
            features = []
            for result in results:
                if result:  # Some tracks might not have audio features
                    features.append(AudioFeatures(**result))
                    
            return features
            
        except Exception as e:
            logger.error(f"Error getting audio features: {e}")
            raise Exception(f"Failed to get audio features: {str(e)}")

    def _parse_object(self, obj: Dict[str, Any], obj_type: SpotifyObjectType, format: DataFormat) -> Any:
        """Parse Spotify API object based on type and format."""
        try:
            if format == DataFormat.RAW:
                return obj
                
            # Parse based on object type
            if obj_type == SpotifyObjectType.TRACK:
                return self._parse_track(obj, format)
            elif obj_type == SpotifyObjectType.ARTIST:
                return self._parse_artist(obj, format)
            elif obj_type == SpotifyObjectType.ALBUM:
                return self._parse_album(obj, format)
            elif obj_type == SpotifyObjectType.PLAYLIST:
                return self._parse_playlist(obj, format)
            else:
                return obj
                
        except Exception as e:
            logger.warning(f"Error parsing {obj_type} object: {e}")
            return obj

    def _parse_track(self, track_data: Dict[str, Any], format: DataFormat) -> Track:
        """Parse track data based on format."""
        base_data = {
            "id": track_data["id"],
            "name": track_data["name"],
            "uri": track_data["uri"],
            "href": track_data["href"],
            "external_urls": track_data.get("external_urls"),
            "artists": [self._parse_artist(artist, DataFormat.MINIMAL) for artist in track_data.get("artists", [])],
        }
        
        if format in [DataFormat.COMPACT, DataFormat.FULL]:
            base_data.update({
                "album": self._parse_album(track_data["album"], DataFormat.MINIMAL) if track_data.get("album") else None,
                "duration_ms": track_data.get("duration_ms"),
                "explicit": track_data.get("explicit"),
                "popularity": track_data.get("popularity"),
                "preview_url": track_data.get("preview_url"),
            })
            
        if format == DataFormat.FULL:
            base_data.update({
                "track_number": track_data.get("track_number"),
                "disc_number": track_data.get("disc_number"),
                "is_local": track_data.get("is_local"),
                "external_ids": track_data.get("external_ids"),
            })
            
        return Track(**base_data)

    def _parse_artist(self, artist_data: Dict[str, Any], format: DataFormat) -> Artist:
        """Parse artist data based on format."""
        base_data = {
            "id": artist_data["id"],
            "name": artist_data["name"],
            "uri": artist_data["uri"],
            "href": artist_data["href"],
            "external_urls": artist_data.get("external_urls"),
        }
        
        if format in [DataFormat.COMPACT, DataFormat.FULL]:
            base_data.update({
                "images": artist_data.get("images"),
                "popularity": artist_data.get("popularity"),
            })
            
        if format == DataFormat.FULL:
            base_data.update({
                "genres": artist_data.get("genres"),
                "followers": artist_data.get("followers"),
            })
            
        return Artist(**base_data)

    def _parse_album(self, album_data: Dict[str, Any], format: DataFormat) -> Album:
        """Parse album data based on format."""
        base_data = {
            "id": album_data["id"],
            "name": album_data["name"],
            "uri": album_data["uri"],
            "href": album_data["href"],
            "external_urls": album_data.get("external_urls"),
            "artists": [self._parse_artist(artist, DataFormat.MINIMAL) for artist in album_data.get("artists", [])],
        }
        
        if format in [DataFormat.COMPACT, DataFormat.FULL]:
            base_data.update({
                "images": album_data.get("images"),
                "album_type": album_data.get("album_type"),
                "total_tracks": album_data.get("total_tracks"),
                "release_date": album_data.get("release_date"),
            })
            
        if format == DataFormat.FULL:
            base_data.update({
                "release_date_precision": album_data.get("release_date_precision"),
                "genres": album_data.get("genres"),
                "popularity": album_data.get("popularity"),
                "external_ids": album_data.get("external_ids"),
            })
            
        return Album(**base_data)

    def _parse_playlist(self, playlist_data: Dict[str, Any], format: DataFormat) -> Playlist:
        """Parse playlist data based on format."""
        base_data = {
            "id": playlist_data["id"],
            "name": playlist_data["name"],
            "uri": playlist_data["uri"],
            "href": playlist_data["href"],
            "external_urls": playlist_data.get("external_urls"),
        }
        
        if format in [DataFormat.COMPACT, DataFormat.FULL]:
            base_data.update({
                "images": playlist_data.get("images"),
                "description": playlist_data.get("description"),
                "owner": playlist_data.get("owner"),
                "public": playlist_data.get("public"),
                "collaborative": playlist_data.get("collaborative"),
                "tracks": playlist_data.get("tracks"),
            })
            
        if format == DataFormat.FULL:
            base_data.update({
                "followers": playlist_data.get("followers"),
                "snapshot_id": playlist_data.get("snapshot_id"),
            })
            
        return Playlist(**base_data)

    def _parse_playback_state(self, playback_data: Dict[str, Any]) -> PlaybackState:
        """Parse playback state data."""
        return PlaybackState(
            device=playback_data.get("device"),
            repeat_state=playback_data["repeat_state"],
            shuffle_state=playback_data["shuffle_state"],
            context=playback_data.get("context"),
            timestamp=playback_data["timestamp"],
            progress_ms=playback_data.get("progress_ms"),
            is_playing=playback_data["is_playing"],
            item=self._parse_track(playback_data["item"], DataFormat.COMPACT) if playback_data.get("item") else None,
            currently_playing_type=playback_data["currently_playing_type"]
        )

    # ===== SEARCH & BROWSE METHODS =====
    
    async def get_categories(
        self, 
        country: Optional[str] = None, 
        locale: Optional[str] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get available browse categories."""
        try:
            return self.spotify.categories(
                country=country, 
                locale=locale, 
                limit=limit, 
                offset=offset
            )
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise





    async def get_new_releases(
        self, 
        country: Optional[str] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get new album releases."""
        try:
            return self.spotify.new_releases(
                country=country,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Error getting new releases: {e}")
            raise

    # ===== LIBRARY METHODS =====
    
    async def get_saved_albums(
        self, 
        limit: int = 20, 
        offset: int = 0, 
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's saved albums."""
        try:
            return self.spotify.current_user_saved_albums(
                limit=limit, 
                offset=offset, 
                market=market
            )
        except Exception as e:
            logger.error(f"Error getting saved albums: {e}")
            raise

    async def get_followed_artists(
        self, 
        limit: int = 20, 
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's followed artists."""
        try:
            return self.spotify.current_user_followed_artists(
                limit=limit, 
                after=after
            )
        except Exception as e:
            logger.error(f"Error getting followed artists: {e}")
            raise

    async def get_recently_played(
        self, 
        limit: int = 20, 
        after: Optional[int] = None, 
        before: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get recently played tracks."""
        try:
            kwargs = {"limit": limit}
            if after is not None:
                kwargs["after"] = after
            if before is not None:
                kwargs["before"] = before
            return self.spotify.current_user_recently_played(**kwargs)
        except Exception as e:
            logger.error(f"Error getting recently played: {e}")
            raise

    async def save_tracks(self, track_ids: List[str]) -> bool:
        """Save tracks to user's library."""
        try:
            self.spotify.current_user_saved_tracks_add(track_ids)
            return True
        except Exception as e:
            logger.error(f"Error saving tracks: {e}")
            raise

    async def remove_saved_tracks(self, track_ids: List[str]) -> bool:
        """Remove tracks from user's library."""
        try:
            self.spotify.current_user_saved_tracks_delete(track_ids)
            return True
        except Exception as e:
            logger.error(f"Error removing saved tracks: {e}")
            raise

    async def follow_artists(self, artist_ids: List[str]) -> bool:
        """Follow artists."""
        try:
            self.spotify.user_follow_artists(artist_ids)
            return True
        except Exception as e:
            logger.error(f"Error following artists: {e}")
            raise

    # ===== PLAYLIST METHODS =====
    
    async def get_playlist(
        self, 
        playlist_id: str, 
        market: Optional[str] = None, 
        fields: Optional[str] = None,
        additional_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get a specific playlist."""
        try:
            kwargs = {}
            if market is not None:
                kwargs["market"] = market
            if fields is not None:
                kwargs["fields"] = fields
            if additional_types is not None:
                kwargs["additional_types"] = ",".join(additional_types) if isinstance(additional_types, list) else additional_types
            
            return self.spotify.playlist(playlist_id, **kwargs)
        except Exception as e:
            logger.error(f"Error getting playlist: {e}")
            raise

    async def get_playlist_tracks(
        self, 
        playlist_id: str, 
        fields: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0, 
        market: Optional[str] = None,
        additional_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get tracks from a playlist."""
        try:
            kwargs = {
                "limit": limit,
                "offset": offset
            }
            if fields is not None:
                kwargs["fields"] = fields
            if market is not None:
                kwargs["market"] = market
            if additional_types is not None:
                kwargs["additional_types"] = ",".join(additional_types) if isinstance(additional_types, list) else additional_types
                
            return self.spotify.playlist_tracks(playlist_id, **kwargs)
        except Exception as e:
            logger.error(f"Error getting playlist tracks: {e}")
            raise

    async def add_tracks_to_playlist(
        self, 
        playlist_id: str, 
        items: List[str], 
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add tracks to a playlist."""
        try:
            return self.spotify.playlist_add_items(
                playlist_id=playlist_id, 
                items=items, 
                position=position
            )
        except Exception as e:
            logger.error(f"Error adding tracks to playlist: {e}")
            raise

    async def remove_tracks_from_playlist(
        self, 
        playlist_id: str, 
        items: List[str], 
        snapshot_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Remove tracks from a playlist."""
        try:
            return self.spotify.playlist_remove_all_occurrences_of_items(
                playlist_id=playlist_id, 
                items=items, 
                snapshot_id=snapshot_id
            )
        except Exception as e:
            logger.error(f"Error removing tracks from playlist: {e}")
            raise

    async def update_playlist_details(
        self, 
        playlist_id: str, 
        name: Optional[str] = None,
        public: Optional[bool] = None,
        collaborative: Optional[bool] = None,
        description: Optional[str] = None
    ) -> bool:
        """Update playlist details."""
        try:
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if public is not None:
                update_data["public"] = public
            if collaborative is not None:
                update_data["collaborative"] = collaborative
            if description is not None:
                update_data["description"] = description
                
            self.spotify.playlist_change_details(playlist_id, **update_data)
            return True
        except Exception as e:
            logger.error(f"Error updating playlist details: {e}")
            raise

    async def reorder_playlist_items(
        self, 
        playlist_id: str, 
        range_start: int, 
        range_length: int = 1,
        insert_before: Optional[int] = None, 
        snapshot_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reorder items in a playlist."""
        try:
            return self.spotify.playlist_reorder_items(
                playlist_id=playlist_id,
                range_start=range_start,
                range_length=range_length,
                insert_before=insert_before,
                snapshot_id=snapshot_id
            )
        except Exception as e:
            logger.error(f"Error reordering playlist items: {e}")
            raise

    async def unfollow_playlist(self, playlist_id: str) -> bool:
        """Unfollow a playlist."""
        try:
            self.spotify.current_user_unfollow_playlist(playlist_id)
            return True
        except Exception as e:
            logger.error(f"Error unfollowing playlist: {e}")
            raise

    # ===== PLAYBACK METHODS =====
    
    async def get_devices(self) -> Dict[str, Any]:
        """Get available devices."""
        try:
            return self.spotify.devices()
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            raise

    async def start_playback(
        self, 
        device_id: Optional[str] = None,
        context_uri: Optional[str] = None,
        uris: Optional[List[str]] = None,
        offset: Optional[Dict[str, Any]] = None,
        position_ms: Optional[int] = None
    ) -> bool:
        """Start or resume playback."""
        try:
            kwargs = {}
            if device_id:
                kwargs["device_id"] = device_id
            if context_uri:
                kwargs["context_uri"] = context_uri
            if uris:
                kwargs["uris"] = uris
            if offset:
                kwargs["offset"] = offset
            if position_ms:
                kwargs["position_ms"] = position_ms
                
            self.spotify.start_playback(**kwargs)
            return True
        except Exception as e:
            logger.error(f"Error starting playback: {e}")
            raise

    async def pause_playback(self, device_id: Optional[str] = None) -> bool:
        """Pause playback."""
        try:
            self.spotify.pause_playback(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error pausing playback: {e}")
            raise

    async def next_track(self, device_id: Optional[str] = None) -> bool:
        """Skip to next track."""
        try:
            self.spotify.next_track(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error skipping to next track: {e}")
            raise

    async def previous_track(self, device_id: Optional[str] = None) -> bool:
        """Skip to previous track."""
        try:
            self.spotify.previous_track(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error skipping to previous track: {e}")
            raise

    async def seek_track(
        self, 
        position_ms: int, 
        device_id: Optional[str] = None
    ) -> bool:
        """Seek to position in current track."""
        try:
            self.spotify.seek_track(position_ms, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error seeking track: {e}")
            raise

    async def set_volume(
        self, 
        volume_percent: int, 
        device_id: Optional[str] = None
    ) -> bool:
        """Set playback volume."""
        try:
            self.spotify.volume(volume_percent, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            raise

    async def set_repeat(
        self, 
        repeat_state: str, 
        device_id: Optional[str] = None
    ) -> bool:
        """Set repeat mode."""
        try:
            self.spotify.repeat(repeat_state, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error setting repeat: {e}")
            raise

    async def set_shuffle(
        self, 
        state: bool, 
        device_id: Optional[str] = None
    ) -> bool:
        """Set shuffle mode."""
        try:
            self.spotify.shuffle(state, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error setting shuffle: {e}")
            raise

    async def transfer_playback(
        self, 
        device_ids: List[str], 
        force_play: bool = False
    ) -> bool:
        """Transfer playback to different device."""
        try:
            # Spotipy expects device_id (singular) for the first device, or device_ids parameter
            if len(device_ids) == 1:
                self.spotify.transfer_playback(device_id=device_ids[0], force_play=force_play)
            else:
                self.spotify.transfer_playback(device_ids=device_ids, force_play=force_play)
            return True
        except Exception as e:
            logger.error(f"Error transferring playback: {e}")
            raise

    async def add_to_queue(
        self, 
        uri: str, 
        device_id: Optional[str] = None
    ) -> bool:
        """Add item to playback queue."""
        try:
            self.spotify.add_to_queue(uri, device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            raise

    # ===== ANALYSIS METHODS =====
    
    async def get_audio_analysis(self, track_id: str) -> Dict[str, Any]:
        """Get audio analysis for a track."""
        try:
            return self.spotify.audio_analysis(track_id)
        except Exception as e:
            logger.error(f"Error getting audio analysis: {e}")
            raise

    async def get_artists(self, artist_ids: List[str]) -> Dict[str, Any]:
        """Get information about multiple artists."""
        try:
            return self.spotify.artists(artist_ids)
        except Exception as e:
            logger.error(f"Error getting artists: {e}")
            raise

    async def get_artist_top_tracks(
        self, 
        artist_id: str, 
        country: str = "US"
    ) -> Dict[str, Any]:
        """Get an artist's top tracks."""
        try:
            return self.spotify.artist_top_tracks(artist_id, country=country)
        except Exception as e:
            logger.error(f"Error getting artist top tracks: {e}")
            raise

    async def get_artist_related_artists(self, artist_id: str) -> Dict[str, Any]:
        """Get artists related to an artist."""
        try:
            return self.spotify.artist_related_artists(artist_id)
        except Exception as e:
            logger.error(f"Error getting related artists: {e}")
            raise

    async def get_artist_albums(
        self, 
        artist_id: str,
        album_type: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 20, 
        offset: int = 0, 
        include_groups: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get an artist's albums."""
        try:
            return self.spotify.artist_albums(
                artist_id=artist_id,
                album_type=album_type,
                country=country,
                limit=limit,
                offset=offset,
                include_groups=include_groups
            )
        except Exception as e:
            logger.error(f"Error getting artist albums: {e}")
            raise

    async def get_album_tracks(
        self, 
        album_id: str, 
        limit: int = 50, 
        offset: int = 0, 
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get tracks from an album."""
        try:
            return self.spotify.album_tracks(
                album_id=album_id,
                limit=limit,
                offset=offset,
                market=market
            )
        except Exception as e:
            logger.error(f"Error getting album tracks: {e}")
            raise

