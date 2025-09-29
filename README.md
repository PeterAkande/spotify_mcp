# Spotify MCP Server

A comprehensive Model Context Protocol (MCP) server for Spotify operations with **36 production-ready tools** and FastMCP transport.

## 🚀 Quick Start

### Prerequisites
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation
```bash
# Clone and install dependencies
git clone <repository>
cd spotify_mcp
uv sync
```

### Development Setup
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your configuration (see Configuration section)

# Start development server (auto-reload)
uv run python start_server.py
# OR manually with custom port
uvicorn main:app --reload --port 8001
```

## Features

### Complete Spotify Integration
- **36 MCP Tools** covering all Spotify operations
- **OAuth 2.0 Authentication** with Spotify token validation
- **Type Safety** with comprehensive Pydantic models

## Tools available (36 Total)

### 🔍 **Search & Discovery** (3 tools)
- `search_music` - Universal music search with filters and pagination
- `get_categories` - Browse available music categories
- `get_new_releases` - Get new album releases

### 📚 **Library Management** (8 tools)
- `get_saved_tracks` - Get user's liked tracks with pagination
- `get_saved_albums` - Get user's saved albums
- `get_followed_artists` - Get followed artists
- `get_recently_played` - Get recently played tracks
- `get_top_items` - Get user's top tracks or artists
- `save_tracks` - Add tracks to user's library
- `remove_saved_tracks` - Remove tracks from library
- `follow_artists` - Follow or unfollow artists

### 🎼 **Playlist Management** (8 tools)
- `get_user_playlists` - List user's playlists with pagination
- `create_playlist` - Create new playlists
- `get_playlist` - Get playlist details and metadata
- `get_playlist_tracks` - Get tracks from a playlist
- `add_tracks_to_playlist` - Add tracks to playlists
- `remove_tracks_from_playlist` - Remove tracks from playlists
- `update_playlist_details` - Update playlist name, description, etc.
- `unfollow_playlist` - Unfollow/delete playlists

### 🎮 **Playback Control** (12 tools)
- `get_current_playback` - Get current playback state
- `get_devices` - List available Spotify devices
- `start_playback` - Start/resume playback with options
- `pause_playback` - Pause current playback
- `next_track` - Skip to next track
- `previous_track` - Skip to previous track
- `seek_track` - Seek to specific position
- `set_volume` - Control playback volume
- `set_repeat` - Set repeat mode (track, context, off)
- `set_shuffle` - Toggle shuffle mode
- `transfer_playback` - Transfer playback between devices
- `add_to_queue` - Add tracks to playback queue

### 🔍 **Music Analysis** (6 tools)
- `get_track_audio_features` - Get audio features for tracks
- `get_audio_analysis` - Get detailed audio analysis
- `get_artists` - Get artist information
- `get_artist_top_tracks` - Get artist's most popular tracks
- `get_artist_albums` - Get artist's albums
- `get_album_tracks` - Get tracks from an album

## Configuration

### Environment Variables (.env)
```bash
# Server Configuration
SERVER_HOST=0.0.0.0                    # Server bind address
SERVER_PORT=8001                       # Server port
DEBUG=false                            # Enable debug mode

# Spotify OAuth Configuration
SPOTIFY_CLIENT_ID=your_client_id       # From Spotify Developer Dashboard
SPOTIFY_CLIENT_SECRET=your_secret      # From Spotify Developer Dashboard
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback

# Logging
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
```

### Spotify OAuth Scopes
The server requires these Spotify scopes:
- `user-read-private` - Read user profile
- `user-read-email` - Read user email
- `user-library-read` - Read user's library
- `user-library-modify` - Modify user's library
- `playlist-read-private` - Read private playlists
- `playlist-modify-public` - Modify public playlists
- `playlist-modify-private` - Modify private playlists
- `user-read-playback-state` - Read playback state
- `user-modify-playback-state` - Control playback
- `user-read-recently-played` - Read recently played
- `user-top-read` - Read top tracks/artists
- `user-follow-read` - Read followed artists
- `user-follow-modify` - Follow/unfollow artists

## Response Formats

The server supports multiple response formats for optimal performance:

### **COMPACT (Default)**
- **Best for**: General music browsing and AI processing
- **Contains**: Essential metadata + track/artist info
- **Use case**: Most common operations

### **MINIMAL**
- **Best for**: Listing and enumeration
- **Contains**: ID, name, basic info only
- **Use case**: High-volume operations

### **FULL**
- **Best for**: Complete music data
- **Contains**: All available metadata and details
- **Use case**: Detailed music analysis

### **RAW**
- **Best for**: Direct Spotify API response
- **Contains**: Unprocessed Spotify API data
- **Use case**: Advanced integrations

## Pagination Support

Most tools support flexible pagination:

### **Standard Pagination**
```python
# Get first 20 tracks
get_saved_tracks(limit=20, offset=0)

# Get next 20 tracks  
get_saved_tracks(limit=20, offset=20)
```

### **Examples**
```python
# Get user's top tracks from last 6 months
get_top_items(type="tracks", time_range="medium_term", limit=50)

# Search for Drake songs with pagination
search_music(query="Drake", type="track", limit=10, offset=0)
```

## Architecture

### **MCP Server Design**
- **Transport**: FastMCP with HTTP transport
- **Authentication**: Spotify OAuth 2.0 with token validation
- **Format**: JSON-based MCP protocol
- **Streaming**: Real-time response handling

### **OAuth Flow**
```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   MCP Client        │    │   Spotify OAuth      │    │  Spotify MCP    │
│                     │    │   (accounts.spotify) │    │  Server         │
│ 1. Request with     │────│ 2. Validates token   │────│ 3. Spotify API  │
│    Bearer token     │    │    Returns user info │    │    operations   │
│                     │    │                      │    │                 │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
```

## API Reference

### **Authentication**
All endpoints require a valid Spotify OAuth token:
```http
Authorization: Bearer <spotify_oauth_token>
```

## Development

### **Project Setup**
```bash
# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env file with your configuration

# Run tests
uv run python examples/test_functions.py

# Start development server with auto-reload
uv run python start_server.py
```

### **Development Commands**
```bash
# Development server (auto-reload)
uv run python start_server.py

# Manual development with custom port
uvicorn main:app --reload --port 8001

# Production server
uvicorn main:app --host 0.0.0.0 --port 8001

# Run interactive tests
uv run python examples/test_functions.py
```

### **Testing Tools**
The project includes `examples/test_functions.py` - an interactive test suite:
- Tests all 36 Spotify MCP functions
- Comprehensive debugging with error reporting
- Category-based testing (Search, Library, Playlists, Playback, Analysis)

### **Spotify OAuth Scopes**
The server automatically configures these required scopes:
```python
REQUIRED_SCOPES = [
    "user-read-private",
    "user-read-email", 
    "user-library-read",
    "user-library-modify",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-recently-played",
    "user-top-read",
    "user-follow-read",
    "user-follow-modify"
]
```

## 🔐 Spotify OAuth Setup

1. **Spotify Developer Dashboard**
   - Create project at [developer.spotify.com](https://developer.spotify.com/dashboard)
   - Create a new app
   - Add redirect URI: `http://localhost:8080/callback`

2. **OAuth Configuration**
   - Copy Client ID and Client Secret to `.env` file
   - Configure redirect URIs as needed for your OAuth flow
   - Download credentials (not stored in this server)

3. **Token Validation**
   - This server validates tokens with Spotify's `/v1/me` endpoint
   - No credential storage - tokens validated per request
   - For getting an access token for quick test, check `examples/get_access_token.py`

## 📝 License

MIT License - see LICENSE file for details.
