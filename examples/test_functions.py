#!/usr/bin/env python3
"""
Spotify MCP Service Test Script

Comprehensive interactive test script for all 36 Spotify MCP tools.
Tests all functions across 5 categories: Search, Library, Playlists, Playback, and Analysis.
Requires a valid Spotify access token with appropriate scopes.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from spotify_mcp.services import SpotifyService
    from spotify_mcp.models import (
        SearchRequest,

        PlaylistCreateRequest,
        DataFormat,
        SpotifyObjectType,
        TimeRange,
    )
    from spotify_mcp.auth import SpotifyTokenInfo
    
    # Import MCP tools for direct testing
    from spotify_mcp.tools.search import register_search_tools
    from spotify_mcp.tools.library import register_library_tools
    from spotify_mcp.tools.playlists import register_playlist_tools
    from spotify_mcp.tools.playback import register_playback_tools
    from spotify_mcp.tools.analysis import register_analysis_tools
    
    # For creating mock Context
    from mcp.server.fastmcp.server import Context
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure the project is properly installed: pip install -e .")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpotifyTester:
    """Comprehensive tester for all Spotify MCP tools."""

    def __init__(self, access_token: str):
        """Initialize tester with access token."""
        self.access_token = access_token
        
        # Create SpotifyService instance for testing
        self.service = SpotifyService(access_token)
        
        # Create a mock context for MCP tools
        self.mock_context = self._create_mock_context(access_token)
        
        # Test categories and their functions (all implemented MCP tools)
        self.test_categories = {
            "🔍 Search & Discovery": [
                ("search_music", "Search across Spotify's catalog"),

                ("get_categories", "Browse music categories"),


                ("get_new_releases", "Get new album releases")
            ],
            "📚 Library Management": [
                ("get_saved_tracks", "Get user's saved tracks"),
                ("get_saved_albums", "Get user's saved albums"),
                ("get_followed_artists", "Get followed artists"),
                ("get_recently_played", "Get recently played tracks"),
                ("get_top_items", "Get user's top tracks/artists"),
                ("save_tracks", "Save tracks to library"),
                ("remove_saved_tracks", "Remove tracks from library"),
                ("follow_artists", "Follow artists")
            ],
            "🎼 Playlist Management (8 tools)": [
                ("get_user_playlists", "Get user's playlists"),
                ("create_playlist", "Create new playlist"),
                ("get_playlist", "Get playlist details"),
                ("get_playlist_tracks", "Get playlist tracks"),
                ("add_tracks_to_playlist", "Add tracks to playlist"),
                ("remove_tracks_from_playlist", "Remove tracks from playlist"),
                ("update_playlist_details", "Update playlist details"),
                ("unfollow_playlist", "Unfollow playlist")
            ],
            "🎮 Playback Control (12 tools)": [
                ("get_current_playback", "Get current playback state"),
                ("get_devices", "Get available devices"),
                ("start_playback", "Start/resume playback"),
                ("pause_playback", "Pause playback"),
                ("next_track", "Skip to next track"),
                ("previous_track", "Skip to previous track"),
                ("seek_track", "Seek to position"),
                ("set_volume", "Set playback volume"),
                ("set_repeat", "Set repeat mode"),
                ("set_shuffle", "Set shuffle mode"),
                ("transfer_playback", "Transfer playback to device"),
                ("add_to_queue", "Add track to queue")
            ],
            "🔍 Music Analysis (6 tools)": [
                ("get_track_audio_features", "Get track audio features"),
                ("get_audio_analysis", "Get detailed track analysis"),
                ("get_artists", "Get artist information"),
                ("get_artist_top_tracks", "Get artist's top tracks"),
                ("get_artist_albums", "Get artist's albums"),
                ("get_album_tracks", "Get album tracks"),

            ]
        }

    def _create_mock_context(self, access_token: str):
        """Create a mock MCP context with the access token."""
        class MockContext:
            def __init__(self, token):
                self.token = token
                
        return MockContext(access_token)

    async def run_function_test(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Run a specific SpotifyService method test (testing the same functionality that MCP tools use)."""
        try:
            # Since MCP tools call SpotifyService methods, we test SpotifyService directly
            # This effectively tests the same functionality the MCP tools expose
            
            if hasattr(self.service, function_name):
                func = getattr(self.service, function_name)
                
                # Functions that expect Pydantic model objects
                if function_name == "search_music":
                    # Convert kwargs to SearchRequest
                    types = kwargs.get("types", ["track"])
                    if isinstance(types[0], str):
                        types = [SpotifyObjectType(t) for t in types]
                    request = SearchRequest(
                        query=kwargs["query"],
                        types=types,
                        limit=kwargs.get("limit", 20),
                        offset=kwargs.get("offset", 0),
                        market=kwargs.get("market", "US"),
                        format=DataFormat(kwargs.get("format", "compact"))
                    )
                    result = await func(request)
                
                elif function_name == "create_playlist":
                    # Convert kwargs to PlaylistCreateRequest
                    request = PlaylistCreateRequest(
                        name=kwargs["name"],
                        description=kwargs.get("description"),
                        public=kwargs.get("public", False),
                        collaborative=kwargs.get("collaborative", False)
                    )
                    result = await func(request)
                else:
                    # Functions that expect individual parameters
                    result = await func(**kwargs)
            else:
                raise ValueError(f"SpotifyService does not have method: {function_name}")
            
            return {
                "success": True,
                "result": result,
                "function": function_name,
                "parameters": kwargs
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "function": function_name,
                "parameters": kwargs
            }


async def main():
    """Interactive testing main function."""
    print("🎵 Spotify MCP Service Comprehensive Tester")
    print("=" * 45)
    print("This script tests all 36 MCP tools across 5 categories")
    print("Requires a Spotify access token with appropriate scopes")
    print()
    
    # Get access token
    # access_token = input("Enter your Spotify access token: ").strip()
    access_token = "BQDib8ePSBu4Q_-xxd88bv6iZhwFWsdna9N9z7MPnYqMc6x58QKpb02jak8DLFD311rB5Dz1QT_WECu2ZHKCaq98TOSxaa2Y_ybhrmP_xf47nZLOKWGyygD2yV_4c6DQunjUj6pUkU4JzSM2ytCtUUQsdjy_5RCvt9ZXMGGybdQqHf49O__QHxzhksbqgzJ5XFDPV7Eq0I4xjFLn5xylqos7MR7GHByk2NwYwGIJ__qPSQdKHzPqZcHH_1T8wWQCAY2khH35l3dzzrW3kj01XD49BtBbN4NYTg56ZBnK9HAnNqQpKfzuEqmH05PvocetLB51DwxcqWtQCqMNXCHeYSaCSIS5cTinvqZGS_xNVVnjU50Yy8I"
    if not access_token:
        print("❌ Access token required")
        return

    tester = SpotifyTester(access_token)
    
    while True:
        print("\n📋 Test Categories:")
        print("=" * 20)
        categories = list(tester.test_categories.keys())
        for i, category in enumerate(categories, 1):
            count = len(tester.test_categories[category])
            print(f" {i}. {category} ({count} tools)")
        print(" 6. 🚀 Run All Tests (Quick)")
        print(" 7. 🔧 Run All Tests (Detailed)")
        print(" 8. 🧪 Test Specific Function")
        print(" 9. 🔍 Debug All Functions in Category")
        print(" 0. Exit")

        choice = input(f"\nSelect category or option (0-9): ").strip()

        try:
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice in ["1", "2", "3", "4", "5"]:
                category_idx = int(choice) - 1
                if 0 <= category_idx < len(categories):
                    category = categories[category_idx]
                    await test_category(tester, category)
                else:
                    print("❌ Invalid category!")
            elif choice == "6":
                await run_all_tests(tester, detailed=False)
            elif choice == "7":
                await run_all_tests(tester, detailed=True)
            elif choice == "8":
                await test_specific_function(tester)
            elif choice == "9":
                await debug_category_functions(tester)
            else:
                print("❌ Invalid choice!")

        except Exception as e:
            print(f"❌ Error: {e}")
            logger.exception("Error in main loop")


async def debug_category_functions(tester: SpotifyTester):
    """Debug all functions in a selected category to collect all errors."""
    print("\n🔍 Debug Category Functions")
    print("=" * 30)
    
    categories = list(tester.test_categories.keys())
    for i, category in enumerate(categories, 1):
        count = len(tester.test_categories[category])
        print(f" {i}. {category} ({count} tools)")
    print(" 0. Back to main menu")
    
    choice = input(f"\nSelect category to debug (0-{len(categories)}): ").strip()
    
    try:
        if choice == "0":
            return
        
        category_idx = int(choice) - 1
        if 0 <= category_idx < len(categories):
            category = categories[category_idx]
            results, errors = await test_all_functions_in_category(tester, category)
            
            if errors:
                print(f"\n🔧 COPY THIS ERROR SUMMARY TO FIX ALL ISSUES:")
                print("=" * 60)
                for i, (func_name, error) in enumerate(errors, 1):
                    print(f"ERROR {i}: {func_name}")
                    print(f"  {error}")
                    print()
            else:
                print(f"\n🎉 All functions in {category} work perfectly!")
                
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")

async def test_category(tester: SpotifyTester, category: str):
    """Test all functions in a specific category."""
    print(f"\n{category}")
    print("=" * len(category))
    
    functions = tester.test_categories[category]
    
    for i, (function_name, description) in enumerate(functions, 1):
        print(f" {i}. {function_name} - {description}")
    print(" 0. Back to main menu")
    
    choice = input(f"\nSelect function to test (0-{len(functions)}): ").strip()
    
    try:
        if choice == "0":
            return
        
        func_idx = int(choice) - 1
        if 0 <= func_idx < len(functions):
            function_name, description = functions[func_idx]
            await test_individual_function(tester, function_name, description)
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")


async def test_all_functions_in_category(tester: SpotifyTester, category: str):
    """Test all functions in a category and collect all errors."""
    print(f"\n🧪 Testing all functions in: {category}")
    print("=" * 50)
    
    functions = tester.test_categories[category]
    results = []
    errors = []
    
    for function_name, description in functions:
        print(f"\n⚡ Testing {function_name}...")
        
        # Get default parameters
        params = get_default_function_parameters(function_name)
        
        # Run the test
        result = await tester.run_function_test(function_name, **params)
        
        if result["success"]:
            print(f"✅ {function_name} - SUCCESS")
            results.append((function_name, "SUCCESS", None))
        else:
            print(f"❌ {function_name} - FAILED: {result['error']}")
            results.append((function_name, "FAILED", result['error']))
            errors.append((function_name, result['error']))
    
    # Summary
    print(f"\n📊 SUMMARY FOR {category}:")
    print("=" * 50)
    success_count = len([r for r in results if r[1] == "SUCCESS"])
    fail_count = len(errors)
    
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    if errors:
        print(f"\n🚨 ERRORS TO FIX:")
        for i, (func_name, error) in enumerate(errors, 1):
            print(f"{i}. {func_name}: {error}")
    
    return results, errors

def get_default_function_parameters(function_name: str) -> Dict[str, Any]:
    """Get default parameters for testing functions."""
    defaults = {
        # Search & Discovery
        "search_music": {"query": "test", "types": ["track"], "limit": 5},
        "get_categories": {"limit": 5},
        "get_new_releases": {"limit": 5},
        
        # Library Management
        "get_saved_tracks": {"limit": 5},
        "get_saved_albums": {"limit": 5},
        "get_followed_artists": {"limit": 5},
        "get_recently_played": {"limit": 5},
        "get_top_items": {"item_type": "tracks", "time_range": TimeRange.SHORT_TERM, "limit": 5},
        "save_tracks": {"track_ids": ["4iV5W9uYEdYUVa79Axb7Rh"]},  # Sample track ID
        "remove_saved_tracks": {"track_ids": ["4iV5W9uYEdYUVa79Axb7Rh"]},
        "follow_artists": {"artist_ids": ["4NHQUGzhtTLFvgF5SZesLK"]},  # Sample artist ID
        
        # Playlist Management
        "get_user_playlists": {"limit": 5},
        "get_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "additional_types": None},  # User's test playlist ID
        "get_playlist_tracks": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "limit": 5, "additional_types": None},
        "create_playlist": {"name": "Test Playlist", "description": "Test", "public": False},
        "add_tracks_to_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "items": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"]},
        "remove_tracks_from_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "items": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"]},
        "follow_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "follow": True},

        "update_playlist_details": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "name": "Updated Test Playlist", "description": "Updated via MCP", "public": False},
        "unfollow_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW"},
        
        # Playback Control
        "get_current_playback": {},
        "get_available_devices": {},
        "get_devices": {},
        "start_playback": {},
        "pause_playback": {},
        "next_track": {},
        "previous_track": {},
        "seek_track": {"position_ms": 30000},
        "set_volume": {"volume_percent": 50},
        "set_repeat": {"repeat_state": "off"},
        "set_shuffle": {"state": False},
        "transfer_playback": {"device_ids": ["bd2ce475e695acbf03e9c5f0ac7a50f1a8379c53"]},  # Real device ID
        "add_to_queue": {"uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh"},
        
        # Music Analysis
        "get_track_audio_features": {"track_ids": ["0VjIjW4GlULA4LGEGLUplC"]},  # The Weeknd - Blinding Lights
        "get_audio_analysis": {"track_id": "0VjIjW4GlULA4LGEGLUplC"},
        "get_artists": {"artist_ids": ["4NHQUGzhtTLFvgF5SZesLK"]},
        "get_artist_top_tracks": {"artist_id": "4NHQUGzhtTLFvgF5SZesLK"},
        "get_artist_albums": {"artist_id": "4NHQUGzhtTLFvgF5SZesLK", "limit": 5},
        "get_album_tracks": {"album_id": "4aawyAB9vmqN3uQ7FjRGTy", "limit": 5},
    }
    
    return defaults.get(function_name, {})

async def test_individual_function(tester: SpotifyTester, function_name: str, description: str):
    """Test an individual function with appropriate parameters."""
    print(f"\n🧪 Testing: {function_name}")
    print(f"Description: {description}")
    print("-" * 50)
    
    # Get parameters based on function type
    params = await get_function_parameters(function_name)
    
    if params is None:
        print("❌ Test cancelled")
        return
    
    # Run the test
    print(f"\n⚡ Running {function_name}...")
    result = await tester.run_function_test(function_name, **params)
    
    # Display results
    if result["success"]:
        print("✅ Test completed successfully!")
        print(f"� Result preview:")
        display_result_preview(result["result"], function_name)
    else:
        print("❌ Test failed!")
        print(f"Error: {result['error']}")
    
    input("\nPress Enter to continue...")


async def get_function_parameters(function_name: str) -> Optional[Dict[str, Any]]:
    """Get parameters for a specific function."""
    params = {}
    
    try:
        # Search & Discovery functions
        if function_name == "search_music":
            query = input("Search query: ").strip()
            if not query:
                return None
            params["query"] = query
            types_input = input("Types (track,artist,album,playlist) [default: track]: ").strip()
            if types_input:
                params["types"] = [t.strip() for t in types_input.split(",")]
            else:
                params["types"] = ["track"]
            limit = input("Limit [default: 20]: ").strip()
            if limit:
                params["limit"] = int(limit)
            format_input = input("Format (minimal/compact/full/raw) [default: compact]: ").strip()
            if format_input:
                params["format"] = format_input
            
        
        
        # Library Management functions
        elif function_name == "get_saved_tracks":
            limit = input("Limit [default: 20]: ").strip()
            if limit:
                params["limit"] = int(limit)
            format_input = input("Format (minimal/compact/full/raw) [default: compact]: ").strip()
            if format_input:
                params["format"] = DataFormat(format_input)
                
        elif function_name == "get_top_items":
            item_type = input("Type (tracks/artists) [default: tracks]: ").strip() or "tracks"
            params["item_type"] = item_type  # Fixed parameter name
            time_range = input("Time range (short_term/medium_term/long_term) [default: medium_term]: ").strip()
            if time_range:
                params["time_range"] = TimeRange(time_range.upper())
            limit = input("Limit [default: 20]: ").strip()
            if limit:
                params["limit"] = int(limit)
        
        # Playlist Management functions
        elif function_name == "get_user_playlists":
            limit = input("Limit [default: 20]: ").strip()
            if limit:
                params["limit"] = int(limit)
            format_input = input("Format (minimal/compact/full/raw) [default: compact]: ").strip()
            if format_input:
                params["format"] = DataFormat(format_input)
                
        elif function_name == "create_playlist":
            name = input("Playlist name: ").strip()
            if not name:
                return None
            params["name"] = name
            description = input("Description [optional]: ").strip()
            if description:
                params["description"] = description
            public = input("Public? (y/n) [default: n]: ").strip().lower() == 'y'
            params["public"] = public
        
        # Playback Control functions  
        elif function_name == "get_current_playback":
            # No parameters needed
            pass
        
        # Music Analysis functions

        
        elif function_name == "get_track_audio_features":
            track_ids = input("Track IDs (comma-separated): ").strip()
            if not track_ids:
                print("ℹ️ Using sample track ID")
                params["track_ids"] = ["4iV5W9uYEdYUVa79Axb7Rh"]
            else:
                params["track_ids"] = [t.strip() for t in track_ids.split(",")]
        
        return params
        
    except ValueError as e:
        print(f"❌ Invalid parameter: {e}")
        return None


def display_result_preview(result: Any, function_name: str):
    """Display a preview of the function result."""
    if result is None:
        print("   No data returned")
        return
    
    try:
        if hasattr(result, 'model_dump'):
            data = result.model_dump()
        elif isinstance(result, dict):
            data = result
        elif isinstance(result, list):
            data = {"items": result, "count": len(result)}
        else:
            data = {"result": str(result)}
        
        # Limit output size for readability
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
            if isinstance(items, list) and len(items) > 20:
                print(f"   Found {len(items)} items, showing first 20:")
                for i, item in enumerate(items[:20]):
                    if hasattr(item, 'name'):
                        print(f"   {i+1}. {item.name}")
                    elif isinstance(item, dict) and 'name' in item:
                        print(f"   {i+1}. {item['name']}")
                    else:
                        print(f"   {i+1}. {str(item)}...")
                print(f"   ... and {len(items) - 3} more")
            else:
                print(f"   {json.dumps(data, indent=4, default=str)}...")
        else:
            result_str = json.dumps(data, indent=4, default=str)
            print(f"   {result_str}")
                
    except Exception as e:
        print(f"   Result: {str(result)[:100]}... (Preview error: {e})")


async def run_all_tests(tester: SpotifyTester, detailed: bool = False):
    """Run all tests across all categories."""
    print("\n🚀 Running All Tests")
    print("=" * 20)
    
    total_tests = sum(len(funcs) for funcs in tester.test_categories.values())
    print(f"Testing {total_tests} functions across {len(tester.test_categories)} categories")
    
    if not detailed:
        print("Running in quick mode (minimal output)...")
    else:
        print("Running in detailed mode (full output)...")
    
    success_count = 0
    failure_count = 0
    results = {}
    
    for category, functions in tester.test_categories.items():
        print(f"\n{category}")
        print("-" * len(category))
        category_results = []
        
        for function_name, description in functions:
            print(f"Testing {function_name}...", end=" ")
            
            # Get default parameters for testing
            params = get_default_test_params(function_name)
            result = await tester.run_function_test(function_name, **params)
            
            if result["success"]:
                print("✅")
                success_count += 1
                if detailed:
                    display_result_preview(result["result"], function_name)
            else:
                print("❌")
                failure_count += 1
                if detailed:
                    print(f"   Error: {result['error']}")
            
            category_results.append(result)
        
        results[category] = category_results
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 15)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📈 Success Rate: {success_count / total_tests * 100:.1f}%")
    
    if failure_count > 0:
        print("\n❌ Failed Tests:")
        for category, category_results in results.items():
            failed_tests = [r for r in category_results if not r["success"]]
            if failed_tests:
                print(f"\n{category}:")
                for test in failed_tests:
                    print(f"  - {test['function']}: {test['error']}")


def get_default_test_params(function_name: str) -> Dict[str, Any]:
    """Get default parameters for testing functions."""
    # Default parameters for implemented function types only
    defaults = {
        # Search & Discovery
        "search_music": {"query": "test", "limit": 5},
        "get_categories": {"limit": 5},
        "get_new_releases": {"limit": 5},
        
        # Library Management
        "get_saved_tracks": {"limit": 5},
        "get_saved_albums": {"limit": 5},
        "get_followed_artists": {"limit": 5},
        "get_recently_played": {"limit": 5},
        "get_top_items": {"item_type": "tracks", "limit": 5},
        "save_tracks": {"track_ids": ["4iV5W9uYEdYUVa79Axb7Rh"]},
        "remove_saved_tracks": {"track_ids": ["4iV5W9uYEdYUVa79Axb7Rh"]},
        "follow_artists": {"artist_ids": ["4Z8W4fKeB5YxbusRsdQVPb"]},
        
        # Playlist Management
        "get_user_playlists": {"limit": 5},
        "create_playlist": {"name": "Test Playlist", "description": "Created by test script", "public": False},
        "get_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW"},
        "get_playlist_tracks": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "limit": 5},
        "add_tracks_to_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "items": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"]},
        "remove_tracks_from_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW", "items": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"]},
        "update_playlist_details": {"playlist_id": "6Zg9Bnh5vKvKGNummahehnW", "name": "Updated Test Playlist"},
        "unfollow_playlist": {"playlist_id": "6Zg9Bnh5vKgGNummahehnW"},
        
        # Playback Control
        "get_current_playback": {},
        "get_devices": {},
        "start_playback": {},
        "pause_playback": {},
        "next_track": {},
        "previous_track": {},
        "seek_track": {"position_ms": 30000},
        "set_volume": {"volume_percent": 50},
        "set_repeat": {"repeat_state": "track"},
        "set_shuffle": {"state": True},
        "transfer_playback": {"device_ids": ["bd2ce475e695acbf03e9c5f0ac7a50f1a8379c53"]},  # Real device ID
        "add_to_queue": {"uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh"},
        
        # Music Analysis
        "get_track_audio_features": {"track_ids": ["0VjIjW4GlULA4LGEGLUplC"]},  # The Weeknd - Blinding Lights
        "get_audio_analysis": {"track_id": "0VjIjW4GlULA4LGEGLUplC"},
        "get_artists": {"artist_ids": ["4Z8W4fKeB5YxbusRsdQVPb"]},
        "get_artist_top_tracks": {"artist_id": "4Z8W4fKeB5YxbusRsdQVPb"},

        "get_artist_albums": {"artist_id": "4Z8W4fKeB5YxbusRsdQVPb", "limit": 5},
        "get_album_tracks": {"album_id": "1DFixLWuPkv3KT3TnV35m3", "limit": 5}
    }
    
    return defaults.get(function_name, {})


async def test_specific_function(tester: SpotifyTester):
    """Test a specific function by name."""
    print("\n🧪 Test Specific Function")
    print("=" * 25)
    
    # Show all available functions
    all_functions = []
    for category, functions in tester.test_categories.items():
        for function_name, description in functions:
            all_functions.append((function_name, description, category))
    
    print("Available functions:")
    for i, (function_name, description, category) in enumerate(all_functions, 1):
        print(f" {i:2d}. {function_name} - {description} ({category})")
    
    choice = input(f"\nSelect function (1-{len(all_functions)}) or enter function name: ").strip()
    
    try:
        if choice.isdigit():
            func_idx = int(choice) - 1
            if 0 <= func_idx < len(all_functions):
                function_name, description, category = all_functions[func_idx]
                await test_individual_function(tester, function_name, description)
            else:
                print("❌ Invalid choice!")
        else:
            # Try to find function by name
            matching_functions = [(f, d, c) for f, d, c in all_functions if choice.lower() in f.lower()]
            if len(matching_functions) == 1:
                function_name, description, category = matching_functions[0]
                await test_individual_function(tester, function_name, description)
            elif len(matching_functions) > 1:
                print("Multiple matches found:")
                for i, (f, d, c) in enumerate(matching_functions, 1):
                    print(f" {i}. {f} - {d}")
            else:
                print("❌ Function not found!")
    except ValueError:
        print("❌ Invalid input!")


if __name__ == "__main__":
    asyncio.run(main())