from .spotify_api import authenticate
from typing import Iterable, Sequence, Optional
from spotipy import Spotify, SpotifyException


class SpotifyTools:

    def __init__(self):
        self._sp :Spotify =  authenticate()

    def _call(self, fn, *a, **kw):
        """
        Execute a Spotipy SDK function with one automatic retry if the
        access token is expired or lacks scope (401/403).
        """
        try:
            return fn(*a, **kw)
        except SpotifyException as ex:
            if ex.http_status in (401, 403):
                self._sp = authenticate()      # refresh token → new client
                return fn(*a, **kw)
            raise
    
    def list_playlists(self, limit: int = 50, include_public: bool = True,
                       include_private: bool = True, include_collab: bool = True):
        """
        Return user's playlists as a list of dicts.

        Args:
            limit: Max playlists to return (Spotify page size ≤ 50).
            include_public/private/collab: Toggle visibility types.
        """
        if not any((include_public, include_private, include_collab)):
            raise ValueError("Nothing to include – set at least one flag True.")

        playlists = []
        offset = 0
        while len(playlists) < limit:
            batch = self._call(self._sp.current_user_playlists,
                               limit=min(50, limit - len(playlists)),
                               offset=offset)["items"]
            if not batch:
                break
            for p in batch:
                if ((p["public"] and include_public) or
                    (not p["public"] and include_private) or
                    (p["collaborative"] and include_collab)):
                    playlists.append(p)
            offset += len(batch)
        return playlists
    

    def get_playlist(self, playlist_id: str):
        """Fetch full playlist object (tracks, owner, etc.)."""
        return self._call(self._sp.playlist, playlist_id)
    
    def create_playlist(self, name: str, public: bool = False,
                        description: str = "", collaborative: bool = False):
        """Create a playlist for the current user and return its object."""
        user_id = self._call(self._sp.current_user)["id"]
        return self._call(
            self._sp.user_playlist_create,
            user=user_id, name=name, public=public,
            collaborative=collaborative, description=description
        )
    
    def add_tracks(self, playlist_id: str, track_uris: Sequence[str]) -> None:
        """Append up to 100 tracks to `playlist_id`."""
        if not track_uris:
            raise ValueError("track_uris is empty")
        self._call(self._sp.playlist_add_items, playlist_id, list(track_uris))

    def replace_tracks(self, playlist_id: str, track_uris: Sequence[str]) -> None:
        """
        Replace entire playlist contents.
        Spotify lets you send max 100 uris at once; we chunk automatically.
        """
        self._call(self._sp.playlist_replace_items, playlist_id, list(track_uris))

    def remove_tracks(self, playlist_id: str, track_uris: Sequence[str]) -> None:
        """Remove specific tracks from a playlist."""
        if not track_uris:
            raise ValueError("track_uris is empty")
        self._call(self._sp.playlist_remove_all_occurrences_of_items,
                   playlist_id, list(track_uris))


    # ──────────────── LIBRARY / STATS ─────────────────────────────────
    def liked_tracks(self, limit: int = 50):
        """Return the user's 'Liked Songs' (saved tracks) up to `limit`."""
        tracks, offset = [], 0
        while len(tracks) < limit:
            chunk = self._call(self._sp.current_user_saved_tracks,
                               limit=min(50, limit - len(tracks)),
                               offset=offset)["items"]
            if not chunk:
                break
            tracks.extend(chunk)
            offset += len(chunk)
        return tracks

    def save_tracks(self, track_uris: Iterable[str]) -> None:
        """Save tracks to 'Liked Songs'."""
        self._call(self._sp.current_user_saved_tracks_add, list(track_uris))

    def top_tracks(self, limit: int = 20, time_range: str = "medium_term"):
        """Return top tracks over `short_term` | `medium_term` | `long_term`."""
        return self._call(self._sp.current_user_top_tracks,
                          limit=limit, time_range=time_range)["items"]

    def recently_played(self, limit: int = 50):
        """Return last *limit* tracks the user listened to."""
        return self._call(self._sp.current_user_recently_played,
                          limit=limit)["items"]


    # ──────────────── PLAYBACK CONTROL ───────────────────────────────
    def devices(self):
        """Return available Spotify Connect devices."""
        return self._call(self._sp.devices)["devices"]

    def play(self, uris: Optional[Sequence[str]] = None,
             device_id: Optional[str] = None, position_ms: int | None = None):
        self._call(self._sp.start_playback,
                   device_id=device_id,
                   uris=list(uris) if uris else None,
                   position_ms=position_ms)

    def pause(self, device_id: Optional[str] = None):
        self._call(self._sp.pause_playback, device_id=device_id)

    def next(self, device_id: Optional[str] = None):
        self._call(self._sp.next_track, device_id=device_id)

    def previous(self, device_id: Optional[str] = None):
        self._call(self._sp.previous_track, device_id=device_id)

    def seek(self, position_ms: int, device_id: Optional[str] = None):
        self._call(self._sp.seek_track, position_ms, device_id=device_id)

    def set_volume(self, volume_percent: int, device_id: Optional[str] = None):
        """Volume 0-100."""
        if not 0 <= volume_percent <= 100:
            raise ValueError("volume_percent must be 0-100")
        self._call(self._sp.volume, volume_percent, device_id=device_id)


    # ──────────────── SEARCH / DISCOVERY ─────────────────────────────
    def search_track(self, query: str, limit: int = 10):
        """Simple track search, returns list of track objects."""
        return self._call(self._sp.search,
                          q=query, type="track", limit=limit)["tracks"]["items"]

    def recommendations(self, seed_tracks: Sequence[str] | None = None,
                        seed_artists: Sequence[str] | None = None,
                        limit: int = 20):
        """Spotify recommendations endpoint – pass up to 5 track or artist seeds."""
        return self._call(self._sp.recommendations,
                          seed_tracks=list(seed_tracks or []),
                          seed_artists=list(seed_artists or []),
                          limit=limit)["tracks"]   
    
    