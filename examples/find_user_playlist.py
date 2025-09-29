#!/usr/bin/env python3
"""
Script to find a user's own playlist for testing purposes.
"""

import asyncio
import os
import sys

# Add parent directory to path to import spotify_mcp modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spotify_mcp.services.spotify_service import SpotifyService


async def find_user_playlist():
    """Find a user's own playlist that can be used for testing."""
    
    # Get access token from environment
    access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    if not access_token:
        print("❌ No SPOTIFY_ACCESS_TOKEN found in environment")
        print("Please run: export SPOTIFY_ACCESS_TOKEN='your_token_here'")
        return None
    
    try:
        # Initialize Spotify service
        service = SpotifyService(access_token)
        
        print("🔍 Searching for user's playlists...")
        
        # Get user's playlists
        playlists = await service.get_user_playlists(limit=20)
        
        if not playlists.items:
            print("❌ No playlists found")
            return None
        
        print(f"\n📋 Found {len(playlists.items)} playlists:")
        print("=" * 80)
        
        user_owned_playlist = None
        
        for i, playlist in enumerate(playlists.items, 1):
            # Debug: print the type and structure
            print(f"DEBUG: playlist type: {type(playlist)}")
            print(f"DEBUG: playlist keys: {list(playlist.keys()) if isinstance(playlist, dict) else 'Not a dict'}")
            
            # Handle both dict and object formats
            if isinstance(playlist, dict):
                owner = playlist.get('owner', {}).get('display_name', 'Unknown')
                name = playlist.get('name', 'Unnamed')
                track_count = playlist.get('tracks', {}).get('total', 0)
                playlist_id = playlist.get('id', '')
                is_public = playlist.get('public', False)
            else:
                # Pydantic model or similar object
                owner = getattr(playlist.owner, 'display_name', 'Unknown') if hasattr(playlist, 'owner') and playlist.owner else 'Unknown'
                name = playlist.name if hasattr(playlist, 'name') else 'Unnamed'
                track_count = playlist.tracks.total if hasattr(playlist, 'tracks') and hasattr(playlist.tracks, 'total') else 0
                playlist_id = playlist.id if hasattr(playlist, 'id') else ''
                is_public = playlist.public if hasattr(playlist, 'public') else False
            
            print(f"{i:2d}. {name}")
            print(f"    ID: {playlist_id}")
            print(f"    Owner: {owner}")
            print(f"    Tracks: {track_count}")
            print(f"    Public: {is_public}")
            print()
            
            # Try to find a user-owned playlist with some tracks
            if not user_owned_playlist and track_count > 0:
                # Check if this is likely user-owned (not a Spotify-generated playlist)
                if not playlist_id.startswith('37i9dQZF1DX'):  # Spotify generated playlists start with this
                    user_owned_playlist = playlist_id
                    print(f"✅ Selected '{name}' (ID: {playlist_id}) for testing")
        
        if user_owned_playlist:
            print(f"\n🎯 Recommended playlist ID for testing: {user_owned_playlist}")
            return user_owned_playlist
        else:
            print("\n⚠️  No suitable user-owned playlists found.")
            print("Consider creating a test playlist with a few tracks.")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    result = asyncio.run(find_user_playlist())
    if result:
        print(f"\nUse this playlist ID in your tests: {result}")