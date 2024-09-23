from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy import SpotifyOAuth
import lxml
from dotenv import load_dotenv
load_dotenv()

# spotify id details
SPOTIFY_ID = os.environ["CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["CLIENT_SECRET"]
scope = "playlist-modify-private"

# making url according to the user input
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
URL = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(URL)
billboard_web_page = response.text

soup = BeautifulSoup(billboard_web_page, "lxml")

# making list of the songs
song_titles_span = soup.select(selector="li ul li h3")
song_titles = [song.getText().strip() for song in song_titles_span]

# authenticating spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri="https://open.spotify.com/",
        cache_path="token.txt",
    )
)

user_id = sp.current_user()["id"]

# create playlist
playlist_name = f"Billboard Hot 100 {date}"
playlist_description = f"Top 100 songs from Billboard on {date}"
playlist = sp.user_playlist_create(
    user=user_id,
    name=playlist_name,
    public=False,
    description=playlist_description
)
playlist_id = playlist["id"]

# search for songs
track_ids = []
for song in song_titles:
    try:
        results = sp.search(q=f"track:{song}", type="track", limit=1)
        tracks = results["tracks"]["items"]
        if tracks:
            track_ids.append(tracks[0]["id"])
        else:
            print(f"{song} not found on Spotify.")
    except Exception as e:
        print(f"An error occurred while searching for {song}: {e}")

# add the tracks to the playlist
if track_ids:
    sp.playlist_add_items(playlist_id=playlist_id, items=track_ids)
    print(f"Playlist {playlist_name} created with {len(track_ids)} songs.")
else:
    print("No tracks found to add in the playlist.")
