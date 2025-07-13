import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
SCOPES = (
    "user-read-private user-read-email "
    "playlist-read-private playlist-read-collaborative "
    "playlist-modify-public playlist-modify-private "
    "user-library-read user-library-modify "
    "user-top-read user-read-recently-played user-read-playback-position "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "streaming"            # only if you’ll embed the Web Playback SDK
    # "app-remote-control"  # add if you’ll ship mobile SDK remotes
)

def authenticate():
    """
    Authenticates with the Spotify API using the Authorization Code Flow.

    Relies on environment variables for credentials:
    - SPOTIPY_CLIENT_ID
    - SPOTIPY_CLIENT_SECRET
    - SPOTIPY_REDIRECT_URI

    On the first run, this will open a browser window for user authorization.
    Subsequent runs will use the cached refresh token stored in '.cache'.
    
    Returns:
        spotipy.Spotify: An authenticated Spotipy client instance.
    """

    load_dotenv()
    CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

    if not all([CLIENT_ID,CLIENT_SECRET,REDIRECT_URI]):
        print("Error: Make sure env vars are set properly")
        return None
    
    try:

        auth_manager = SpotifyOAuth(
            client_id= CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope =SCOPES,
            cache_path=".cache"
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        user_info = sp.current_user()
        print(f"Logged in as: {user_info['display_name']} ({user_info['email']})")
        
        return sp
    except SpotifyOauthError as e:
        Path(".cache").unlink(missing_ok = True)
        log.error("OAuth error: %s", e)
        raise
    except Exception as e:
        print(f"Error during authentication: {e}")
        print("Please double-check your credentials and redirect URI in the Spotify Developer Dashboard.")
        return None





    

