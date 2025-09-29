#!/usr/bin/env python3
"""
Spotify OAuth Token Example

This script shows how to get a Spotify access token using OAuth 2.0.
The token can then be used with the Spotify MCP server.

Note: You'll need to register a Spotify app at https://developer.spotify.com/dashboard
and get your client ID and client secret.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


def get_spotify_token():
    """Get Spotify access token using OAuth 2.0."""
    
    # Replace these with your Spotify app credentials
    client_id = "3a88df0f33e6456b8aa2930c9a7df3f9"
    client_secret = "58ea186b5479411885836080637cc834"
    redirect_uri = "https://strongly-touched-mollusk.ngrok-free.app/callback"  # Must match your app settings
    
    # Required scopes for full MCP server functionality
    scopes = [
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
    
    # Create OAuth manager
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=" ".join(scopes),
        cache_path=".spotify_token_cache"
    )
    
    # Get token
    token_info = sp_oauth.get_access_token()
    
    if token_info:
        print("✅ Successfully obtained Spotify access token!")
        print(f"🎵 Access Token: {token_info['access_token']}")
        print(f"⏰ Expires at: {token_info['expires_at']}")
        print(f"🔄 Refresh Token: {token_info['refresh_token']}")
        print()
        print("📋 Token Info:")
        print(json.dumps(token_info, indent=2))
        print()
        print("🔧 Use this token with your MCP client:")
        print(f"Authorization: Bearer {token_info['access_token']}")
        
        return token_info['access_token']
    else:
        print("❌ Failed to obtain access token")
        return None


if __name__ == "__main__":
    print("🎵 Spotify OAuth Token Generator")
    print("=" * 35)
    print()
    print("📝 Setup Instructions:")
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Create a new app")
    print("3. Add http://localhost:8080/callback to Redirect URIs")
    print("4. Copy your Client ID and Client Secret")
    print("5. Update this script with your credentials")
    print()
    
    token = get_spotify_token()
    
    if token:
        print()
        print("🚀 Ready to use with Spotify MCP Server!")
        print("Start the server with: python start_server.py")
    else:
        print()
        print("❌ Please check your credentials and try again")