import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
from typing import Optional

load_dotenv()

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

def spotify_auth():
    auth = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=auth)

def extract_id(link):
    try:
        parts = link.split("/")
        type_id = parts[-2]
        item_id = parts[-1].split("?")[0]
        return type_id, item_id
    except:
        return None, None

def get_spotify_name(sp, type_id, item_id):
    if type_id == "playlist":
        playlist = sp.playlist(item_id)
        return playlist['name']
    return f"{type_id.capitalize()} {item_id}"

def get_spotify_items(spotify, type_id, item_id):
    tracks = []
    try:
        if type_id == "playlist":
            results = spotify.playlist_tracks(item_id)
            while results:
                for item in results['items']:
                    track = item['track']
                    if track:
                        artist = track['artists'][0]['name']
                        tracks.append(f"{artist} - {track['name']}")
                results = spotify.next(results) if results['next'] else None
        elif type_id == "album":
            results = spotify.album_tracks(item_id)
            for item in results['items']:
                artist = item['artists'][0]['name']
                tracks.append(f"{artist} - {item['name']}")
        elif type_id == "track":
            track = spotify.track(item_id)
            artist = track['artists'][0]['name']
            tracks.append(f"{artist} - {track['name']}")
        return tracks
    except Exception as e:
        print(f"Erro ao obter músicas do Spotify: {e}")
        return []

def search_youtube(track: str) -> str:
    try:
        videos_search = VideosSearch(track, limit=1)
        result = videos_search.result()
        print("[DEBUG] Resultado da busca:", result)

        if result and result.get("result"):
            video = result["result"][0]
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            print(f"[DEBUG] Link encontrado: {video_url}")
            return video_url
        else:
            print(f"[AVISO] Nenhum vídeo encontrado para: {track}")
            return ""
    except Exception as e:
        print(f"[ERRO] Falha ao buscar YouTube para '{track}': {e}")
        return ""


def main():
    links = input("Cole os links do Spotify (playlist, álbum ou música), separados por vírgula:\n").split(',')
    links = [url.strip() for url in links if url.strip()]
    if not links:
        print("❌ Nenhum link válido!")
        return

    spotify = spotify_auth()

    for link in links:
        type_id, item_id = extract_id(link)
        if type_id:
            print(f"Buscando músicas na {type_id} com ID {item_id}...")
            tracks = get_spotify_items(spotify, type_id, item_id)
            for track in tracks:
                print(f" - {track}")
            if tracks:
                youtube_link = search_youtube(tracks[0])
                print(f"Link do YouTube: {youtube_link}")
            else:
                print("Nenhuma música encontrada.")
        else:
            print(f"❌ Link inválido: {link}")

if __name__ == "__main__":
    main()
