import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize the Spotify client with the necessary scopes
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

def extract_playlist_id(playlist_url):
    match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Spotify Playlist URL")

def get_playlist_tracks(username, playlist_id):
    results = sp.user_playlist_tracks(user=username, playlist_id=playlist_id)
    tracks = results['items']
    
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    return tracks

# Fetch the playlist details and create an array with all song names
def fetch_playlist(username, playlist_id):
    playlist = sp.user_playlist(user=username, playlist_id=playlist_id)
    print(f"Playlist: {playlist['name']} - {playlist['description']}")
    
    tracks = get_playlist_tracks(username, playlist_id)
    print(f"Total tracks: {len(tracks)}\n")
    
    song_names = [item['track']['name'] for item in tracks]
    
    return song_names

# Example usage
if __name__ == "__main__":
    username = input("enter your username: ")
    playlist_url = input("Enter the Spotify playlist URL: ")
    
    try:
        song_names = fetch_playlist(username, playlist_url)
        print(f"Song names in the playlist: {song_names}")
    except ValueError as e:
        print(e)
