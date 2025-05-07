import os
import re
import hashlib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Search
import yt_dlp as youtube_dl
from dotenv import load_dotenv
import concurrent.futures
from tqdm import tqdm
import threading

load_dotenv()

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

BASE_DOWNLOAD_PATH = "E:\\"  # Pen drive (ajuste se quiser)

tqdm_lock = threading.Lock()
print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def extract_id(url):
    match_playlist = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    match_album = re.search(r'album/([a-zA-Z0-9]+)', url)
    match_track = re.search(r'track/([a-zA-Z0-9]+)', url)

    if match_playlist:
        return "playlist", match_playlist.group(1)
    elif match_album:
        return "album", match_album.group(1)
    elif match_track:
        return "track", match_track.group(1)
    else:
        return None, None

def spotify_auth():
    auth = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=auth)

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
        safe_print(f"Erro ao obter músicas do Spotify: {e}")
        return []

def get_spotify_name(spotify, type_id, item_id):
    try:
        if type_id == "playlist":
            return spotify.playlist(item_id).get('name', 'playlist_downloads')
        elif type_id == "album":
            return spotify.album(item_id).get('name', 'album_downloads')
        elif type_id == "track":
            track = spotify.track(item_id)
            return f"{track['artists'][0]['name']} - {track['name']}"
        else:
            return 'downloads'
    except Exception as e:
        safe_print(f"Erro ao obter nome do Spotify: {e}")
        return 'downloads'

def search_youtube(query):
    try:
        search = Search(query)
        results = search.results
        if results:
            return results[0].watch_url
    except Exception as e:
        safe_print(f"Erro na busca do YouTube para '{query}': {e}")
    return None

def gerar_nome_arquivo(track):
    hash_id = hashlib.md5(track.encode()).hexdigest()[:8]
    nome_base = re.sub(r'[\\/*?:"<>|]', "", track)
    return f"{nome_base} [{hash_id}].mp3"

def download_audio(url, download_path, filename_base):
    output_template = os.path.join(download_path, filename_base.replace(".mp3", "") + ".%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        safe_print(f"Erro ao baixar: {e}")
        return False

def process_track(track, download_path, pbar):
    filename = gerar_nome_arquivo(track)
    filepath = os.path.join(download_path, filename)

    if os.path.exists(filepath):
        with tqdm_lock:
            pbar.update(1)
        safe_print(f"✅ Já existe: {filename}")
        return

    video_url = search_youtube(track)
    if video_url:
        safe_print(f"⬇️ Baixando: {track}")
        success = download_audio(video_url, download_path, filename)
        safe_print("✅ Sucesso!" if success else "❌ Falha!")
    else:
        safe_print(f"⚠️ Não encontrado: {track}")

    with tqdm_lock:
        pbar.update(1)

def process_link(link, position=0, custom_folder=None):
    type_id, item_id = extract_id(link)
    if not type_id:
        safe_print(f"❌ Link inválido: {link}")
        return

    spotify = spotify_auth()
    name = get_spotify_name(spotify, type_id, item_id)
    folder_name = re.sub(r'[\\/*?:"<>|]', "", name)

    if custom_folder:
        final_download_path = os.path.join(BASE_DOWNLOAD_PATH, custom_folder)
    elif type_id == "track":
        final_download_path = BASE_DOWNLOAD_PATH  # Sem escolha de pasta
    else:
        final_download_path = os.path.join(BASE_DOWNLOAD_PATH, folder_name)

    os.makedirs(final_download_path, exist_ok=True)

    safe_print(f"\n📁 {folder_name}")
    safe_print(f"As músicas serão salvas em: {final_download_path}")

    safe_print("🔍 Obtendo músicas...")
    tracks = get_spotify_items(spotify, type_id, item_id)
    if not tracks:
        safe_print("❌ Nenhuma música encontrada!")
        return

    safe_print(f"🎵 Total de músicas: {len(tracks)}")
    safe_print("🧾 Iniciando downloads...")

    with tqdm(total=len(tracks), desc=f"🎵 {folder_name[:25]}", position=position, leave=True, ncols=100) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
            futures = [executor.submit(process_track, track, final_download_path, pbar) for track in tracks]
            concurrent.futures.wait(futures)

    safe_print(f"\n✅ Finalizado: {folder_name}")


def main():
    links = input("Cole os links de playlists, álbuns ou músicas do Spotify separados por vírgula:\n").split(',')
    links = [url.strip() for url in links if url.strip()]
    if not links:
        safe_print("❌ Nenhum link válido!")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(links))) as executor:
        futures = []
        for idx, link in enumerate(links):
            futures.append(executor.submit(process_link, link, idx))
        concurrent.futures.wait(futures)

    safe_print("\n🎉 Todos os downloads foram processados!")

if __name__ == "__main__":
    main()
