from spotify_tools import SpotifyTools

t = SpotifyTools()

print("\n-- Playlists --")
for p in t.list_playlists(limit=10):
    print(f"{p['name']}  •  {p['tracks']['total']} tracks")

print("\n-- Liked songs (first 5) --")
for item in t.liked_tracks(limit=5):
    track = item["track"]
    print(f"{track['name']} – {track['artists'][0]['name']}")

print("\n-- Top tracks (short term) --")
for i, tr in enumerate(t.top_tracks(limit=5, time_range="short_term"), 1):
    print(f"{i}. {tr['name']} – {tr['artists'][0]['name']}")