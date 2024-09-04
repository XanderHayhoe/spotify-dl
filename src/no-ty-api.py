
# less accurate, no rate limit
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
from dotenv import load_dotenv
import os
import yt_dlp

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

def fetch_playlist(username, playlist_id):
    playlist = sp.user_playlist(user=username, playlist_id=playlist_id)
    print(f"Playlist: {playlist['name']} - {playlist['description']}")
    
    tracks = get_playlist_tracks(username, playlist_id)
    print(f"Total tracks: {len(tracks)}\n")
    
    song_names = [item['track']['name'] for item in tracks]
    
    return song_names

def download_first_youtube_result(song_name, ydl_opts, sequence_number):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_result = ydl.extract_info(f"ytsearch1:{song_name}", download=True)
        video_title = search_result['entries'][0]['title'] if 'entries' in search_result else search_result['title']
        print(f"Downloaded: {video_title}")

if __name__ == "__main__":
    username = input("Enter your username: ")
    playlist_url = input("Enter the Spotify playlist URL: ")
    playlist_id = extract_playlist_id(playlist_url)
    
    # Create 'playlist' folder if it doesn't exist
    if not os.path.exists('playlist'):
        os.makedirs('playlist')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': r'C:\Users\xande\ffmpeg\ffmpeg-7.0.2-full_build\bin',  # in prod replace with docker path
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,  # less verbose output
        'outtmpl': 'playlist/%(autonumber)s-%(title)s.%(ext)s',
    }
    
    try:
        song_names = fetch_playlist(username, playlist_id)
        print(f"Found {len(song_names)} songs in the playlist.")
        
        for i, song in enumerate(song_names, start=1):
            ydl_opts['outtmpl'] = f'playlist/{i:03d}-{song}.%(ext)s'
            download_first_youtube_result(song, ydl_opts, i)
        
    except ValueError as e:
        print(e)
