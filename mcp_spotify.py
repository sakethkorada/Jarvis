import os
from typing import List, Optional, Sequence
from mcp.server.fastmcp import FastMCP
from Tools.Spotify.spotify_tools import SpotifyTools

_sp = SpotifyTools()

mcp = FastMCP(
    "Spotify",                          # display-name for the service
    dependencies=[
        
        "spotipy==2.25.1",              # Spotify Web-API client
        "python-dotenv==1.1.1",         # load .env secrets
        "fastapi==0.116.1",             # REST layer
        "uvicorn[standard]==0.35.0",    # ASGI server (production-ready)

       
    ]
)


# ────────────────────────────────────────────────────────────────────
# PLAYLISTS
# ────────────────────────────────────────────────────────────────────
@mcp.tool()
def list_playlists(
    limit: int = 50,
    include_public: bool = True,
    include_private: bool = True,
    include_collab: bool = True,
) -> List[dict]:
    """Return the user’s playlists."""
    return _sp.list_playlists(limit, include_public, include_private, include_collab)


@mcp.tool()
def get_playlist(playlist_id: str) -> dict:
    """Fetch a single playlist (including tracks)."""
    return _sp.get_playlist(playlist_id)


@mcp.tool()
def create_playlist(
    name: str,
    public: bool = False,
    description: str = "",
    collaborative: bool = False,
) -> dict:
    """Create a new playlist for the current user and return it."""
    return _sp.create_playlist(name, public, description, collaborative)


@mcp.tool()
def add_tracks(playlist_id: str, track_uris: Sequence[str]) -> None:
    """Append one or more track URIs to a playlist."""
    _sp.add_tracks(playlist_id, track_uris)


@mcp.tool()
def replace_tracks(playlist_id: str, track_uris: Sequence[str]) -> None:
    """Replace the entire playlist with the given track URIs."""
    _sp.replace_tracks(playlist_id, track_uris)


@mcp.tool()
def remove_tracks(playlist_id: str, track_uris: Sequence[str]) -> None:
    """Remove all occurrences of the given tracks from a playlist."""
    _sp.remove_tracks(playlist_id, track_uris)


# ────────────────────────────────────────────────────────────────────
# LIBRARY / USER COLLECTION
# ────────────────────────────────────────────────────────────────────
@mcp.tool()
def liked_tracks(limit: int = 50) -> List[dict]:
    """Return up to `limit` liked (saved) tracks."""
    return _sp.liked_tracks(limit)


@mcp.tool()
def save_tracks(track_uris: Sequence[str]) -> None:
    """Save the given track URIs to ‘Liked Songs’."""
    _sp.save_tracks(track_uris)


@mcp.tool()
def top_tracks(limit: int = 20, time_range: str = "medium_term") -> List[dict]:
    """
    Return the user’s top tracks.

    `time_range` can be "short_term" (4 weeks), "medium_term" (6 months),
    or "long_term" (several years).
    """
    return _sp.top_tracks(limit, time_range)


@mcp.tool()
def recently_played(limit: int = 50) -> List[dict]:
    """Return the user’s play history (max 50 most recent plays)."""
    return _sp.recently_played(limit)


# ────────────────────────────────────────────────────────────────────
# PLAYBACK CONTROL
# ────────────────────────────────────────────────────────────────────
@mcp.tool()
def devices() -> List[dict]:
    """Return the user’s available Spotify Connect devices."""
    return _sp.devices()


@mcp.tool()
def play(
    uris: Optional[Sequence[str]] = None,
    device_id: Optional[str] = None,
    position_ms: Optional[int] = None,
) -> None:
    """Start playback on the active or specified device."""
    _sp.play(uris, device_id, position_ms)


@mcp.tool()
def pause(device_id: Optional[str] = None) -> None:
    """Pause playback."""
    _sp.pause(device_id)


@mcp.tool(name="next_track")
def next_track(device_id: Optional[str] = None) -> None:
    """Skip to the next track."""
    _sp.next(device_id)


@mcp.tool(name="previous_track")
def previous_track(device_id: Optional[str] = None) -> None:
    """Go back to the previous track."""
    _sp.previous(device_id)


@mcp.tool()
def seek(position_ms: int, device_id: Optional[str] = None) -> None:
    """Seek to `position_ms` within the current track."""
    _sp.seek(position_ms, device_id)


@mcp.tool()
def set_volume(volume_percent: int, device_id: Optional[str] = None) -> None:
    """Set volume on the target device (0–100 %)."""
    _sp.set_volume(volume_percent, device_id)


# ────────────────────────────────────────────────────────────────────
# DISCOVERY / SEARCH
# ────────────────────────────────────────────────────────────────────
@mcp.tool()
def search_track(query: str, limit: int = 10) -> List[dict]:
    """Search for tracks by free-text query."""
    return _sp.search_track(query, limit)


if __name__ == "__main__":
    mcp.run(transport="stdio")
