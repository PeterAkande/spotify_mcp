"""Data models for Spotify MCP service."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import StrEnum


class CaseInsensitiveStrEnum(StrEnum):
    """String enum that supports case-insensitive value lookup."""
    
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class DataFormat(CaseInsensitiveStrEnum):
    """Data format options for API responses."""
    MINIMAL = "minimal"      # IDs and basic metadata only
    COMPACT = "compact"      # Essential data for most operations  
    FULL = "full"           # Complete data including detailed info
    RAW = "raw"             # Original Spotify API format


class SpotifyObjectType(CaseInsensitiveStrEnum):
    """Types of Spotify objects."""
    TRACK = "track"
    ARTIST = "artist"
    ALBUM = "album"
    PLAYLIST = "playlist"
    SHOW = "show"
    EPISODE = "episode"
    USER = "user"


class TimeRange(CaseInsensitiveStrEnum):
    """Time ranges for user statistics."""
    SHORT_TERM = "short_term"      # ~4 weeks
    MEDIUM_TERM = "medium_term"    # ~6 months
    LONG_TERM = "long_term"        # ~years


class RepeatState(CaseInsensitiveStrEnum):
    """Playback repeat states."""
    TRACK = "track"
    CONTEXT = "context"
    OFF = "off"


# Core Spotify Models
class SpotifyImage(BaseModel):
    """Spotify image object."""
    height: Optional[int] = Field(None, description="Image height in pixels")
    width: Optional[int] = Field(None, description="Image width in pixels")
    url: str = Field(..., description="Image URL")


class ExternalUrls(BaseModel):
    """External URLs object."""
    spotify: Optional[str] = Field(None, description="Spotify URL")


class ExternalIds(BaseModel):
    """External IDs object."""
    isrc: Optional[str] = Field(None, description="International Standard Recording Code")
    ean: Optional[str] = Field(None, description="International Article Number")
    upc: Optional[str] = Field(None, description="Universal Product Code")


class Followers(BaseModel):
    """Followers information."""
    href: Optional[str] = Field(None, description="Link to full followers data")
    total: int = Field(..., description="Total number of followers")


class Artist(BaseModel):
    """Spotify artist object."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="Spotify artist ID")
    name: str = Field(..., description="Artist name")
    type: str = Field(default="artist", description="Object type")
    uri: str = Field(..., description="Spotify URI")
    href: str = Field(..., description="API endpoint for artist")
    external_urls: Optional[ExternalUrls] = Field(None, description="External URLs")
    images: Optional[List[SpotifyImage]] = Field(None, description="Artist images")
    genres: Optional[List[str]] = Field(None, description="Artist genres")
    popularity: Optional[int] = Field(None, description="Popularity (0-100)")
    followers: Optional[Followers] = Field(None, description="Follower information")


class Album(BaseModel):
    """Spotify album object."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="Spotify album ID")
    name: str = Field(..., description="Album name")
    type: str = Field(default="album", description="Object type")
    uri: str = Field(..., description="Spotify URI")
    href: str = Field(..., description="API endpoint for album")
    external_urls: Optional[ExternalUrls] = Field(None, description="External URLs")
    images: Optional[List[SpotifyImage]] = Field(None, description="Album cover images")
    artists: List[Artist] = Field(..., description="Album artists")
    album_type: Optional[str] = Field(None, description="Album type")
    total_tracks: Optional[int] = Field(None, description="Number of tracks")
    release_date: Optional[str] = Field(None, description="Release date")
    release_date_precision: Optional[str] = Field(None, description="Release date precision")
    genres: Optional[List[str]] = Field(None, description="Album genres")
    popularity: Optional[int] = Field(None, description="Popularity (0-100)")
    external_ids: Optional[ExternalIds] = Field(None, description="External IDs")


class Track(BaseModel):
    """Spotify track object."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="Spotify track ID")
    name: str = Field(..., description="Track name")
    type: str = Field(default="track", description="Object type")
    uri: str = Field(..., description="Spotify URI")
    href: str = Field(..., description="API endpoint for track")
    external_urls: Optional[ExternalUrls] = Field(None, description="External URLs")
    artists: List[Artist] = Field(..., description="Track artists")
    album: Optional[Album] = Field(None, description="Track album")
    duration_ms: Optional[int] = Field(None, description="Track duration in milliseconds")
    explicit: Optional[bool] = Field(None, description="Whether track is explicit")
    popularity: Optional[int] = Field(None, description="Popularity (0-100)")
    preview_url: Optional[str] = Field(None, description="Preview URL")
    track_number: Optional[int] = Field(None, description="Track number on album")
    disc_number: Optional[int] = Field(None, description="Disc number")
    is_local: Optional[bool] = Field(None, description="Whether track is local file")
    external_ids: Optional[ExternalIds] = Field(None, description="External IDs")


class PlaylistTrack(BaseModel):
    """Playlist track object with metadata."""
    added_at: Optional[datetime] = Field(None, description="When track was added")
    added_by: Optional[Dict[str, Any]] = Field(None, description="User who added track")
    is_local: Optional[bool] = Field(None, description="Whether track is local file")
    track: Track = Field(..., description="Track object")


class Playlist(BaseModel):
    """Spotify playlist object."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="Spotify playlist ID")
    name: str = Field(..., description="Playlist name")
    type: str = Field(default="playlist", description="Object type")
    uri: str = Field(..., description="Spotify URI")
    href: str = Field(..., description="API endpoint for playlist")
    external_urls: Optional[ExternalUrls] = Field(None, description="External URLs")
    images: Optional[List[SpotifyImage]] = Field(None, description="Playlist cover images")
    description: Optional[str] = Field(None, description="Playlist description")
    owner: Optional[Dict[str, Any]] = Field(None, description="Playlist owner")
    public: Optional[bool] = Field(None, description="Whether playlist is public")
    collaborative: Optional[bool] = Field(None, description="Whether playlist is collaborative")
    followers: Optional[Followers] = Field(None, description="Follower information")
    tracks: Optional[Dict[str, Any]] = Field(None, description="Tracks information")
    snapshot_id: Optional[str] = Field(None, description="Playlist snapshot ID")


class Device(BaseModel):
    """Spotify device object."""
    id: Optional[str] = Field(None, description="Device ID")
    is_active: bool = Field(..., description="Whether device is active")
    is_private_session: bool = Field(..., description="Whether in private session")
    is_restricted: bool = Field(..., description="Whether device is restricted")
    name: str = Field(..., description="Device name")
    type: str = Field(..., description="Device type")
    volume_percent: Optional[int] = Field(None, description="Volume percentage")


class PlaybackState(BaseModel):
    """Current playback state."""
    device: Optional[Device] = Field(None, description="Current device")
    repeat_state: str = Field(..., description="Repeat state")
    shuffle_state: bool = Field(..., description="Shuffle state")
    context: Optional[Dict[str, Any]] = Field(None, description="Playback context")
    timestamp: int = Field(..., description="Unix timestamp")
    progress_ms: Optional[int] = Field(None, description="Progress in milliseconds")
    is_playing: bool = Field(..., description="Whether currently playing")
    item: Optional[Track] = Field(None, description="Currently playing track")
    currently_playing_type: str = Field(..., description="Type of currently playing item")


class AudioFeatures(BaseModel):
    """Audio features for a track."""
    id: str = Field(..., description="Track ID")
    danceability: float = Field(..., description="Danceability (0.0-1.0)")
    energy: float = Field(..., description="Energy (0.0-1.0)")
    key: int = Field(..., description="Key (-1-11)")
    loudness: float = Field(..., description="Loudness in dB")
    mode: int = Field(..., description="Mode (0=minor, 1=major)")
    speechiness: float = Field(..., description="Speechiness (0.0-1.0)")
    acousticness: float = Field(..., description="Acousticness (0.0-1.0)")
    instrumentalness: float = Field(..., description="Instrumentalness (0.0-1.0)")
    liveness: float = Field(..., description="Liveness (0.0-1.0)")
    valence: float = Field(..., description="Valence/positivity (0.0-1.0)")
    tempo: float = Field(..., description="Tempo in BPM")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    time_signature: int = Field(..., description="Time signature")


# Request Models
class SearchRequest(BaseModel):
    """Request model for searching Spotify content."""
    query: str = Field(..., description="Search query")
    types: List[SpotifyObjectType] = Field(default=["track"], description="Object types to search")
    market: str = Field(default="US", description="Market for results")
    limit: int = Field(default=20, ge=1, le=50, description="Maximum results per type")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    format: DataFormat = Field(default=DataFormat.COMPACT, description="Response format")





class PlaylistCreateRequest(BaseModel):
    """Request model for creating playlists."""
    name: str = Field(..., description="Playlist name")
    description: Optional[str] = Field(None, description="Playlist description")
    public: bool = Field(default=False, description="Whether playlist is public")
    collaborative: bool = Field(default=False, description="Whether playlist is collaborative")


# Response Models
class SpotifyResponse(BaseModel):
    """Base Spotify API response model."""
    success: bool = Field(..., description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class SearchResponse(BaseModel):
    """Response model for search results."""
    tracks: Optional[List[Track]] = Field(None, description="Track results")
    artists: Optional[List[Artist]] = Field(None, description="Artist results")
    albums: Optional[List[Album]] = Field(None, description="Album results")
    playlists: Optional[List[Playlist]] = Field(None, description="Playlist results")
    total_results: int = Field(..., description="Total number of results")
    format_used: DataFormat = Field(..., description="Response format used")


class PaginatedResponse(BaseModel):
    """Base paginated response model."""
    items: List[Any] = Field(..., description="Response items")
    total: Optional[int] = Field(None, description="Total number of items")
    limit: int = Field(..., description="Request limit")
    offset: int = Field(..., description="Request offset")
    next: Optional[str] = Field(None, description="URL for next page")
    previous: Optional[str] = Field(None, description="URL for previous page")