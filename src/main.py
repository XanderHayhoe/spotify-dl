import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
from dotenv import load_dotenv
import os
import yt_dlp
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
YOUTUBE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

# Initialize the Spotify client with the necessary scopes
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Build the YouTube service
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

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

def search_youtube(song_name):
    # Perform a search
    request = youtube.search().list(
        part="snippet",
        q=song_name,
        type="video",
        maxResults=1
    )
    response = request.execute()

    # Extract the top search result
    if response['items']:
        top_result = response['items'][0]
        video_id = top_result['id']['videoId']
        video_title = top_result['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_title, video_url
    else:
        return None, None

def download_mp3(youtube_urls, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(youtube_urls, start=1):
            current_opts = ydl_opts.copy()
            current_opts['outtmpl'] = f'{i:03d}. %(title)s.%(ext)s'
            ydl.download([url])

    print("Download complete!")

if __name__ == "__main__":
    username = input("Enter your username: ")
    playlist_url = input("Enter the Spotify playlist URL: ")
    playlist_id = extract_playlist_id(playlist_url)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,  # Less verbose output
    }
    
    try:
        song_names = fetch_playlist(username, playlist_id)
        print(f"Found {len(song_names)} songs in the playlist.")
        
        youtube_urls = []
        for song in song_names:
            title, url = search_youtube(song)
            if title and url:
                print(f"Found: {title}")
                youtube_urls.append(url)
            else:
                print(f"No results found for: {song}")
        
        print(f"\nDownloading {len(youtube_urls)} songs...")
        download_mp3(youtube_urls, ydl_opts)
        
    except ValueError as e:
        print(e)

