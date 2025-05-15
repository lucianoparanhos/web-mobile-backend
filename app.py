import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from script import extract_id, spotify_auth, get_spotify_name, get_spotify_items, search_youtube
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🛠️ Reconstrói o cookies.txt a partir da variável de ambiente
def write_cookies_file():
    cookies = os.environ.get("COOKIES_TXT")
    if cookies:
        with open("cookies.txt", "w", encoding="utf-8") as f:
            f.write(cookies)
        print("[COOKIES] cookies.txt reconstruído com sucesso.")
    else:
        print("[COOKIES] Variável COOKIES_TXT não encontrada. cookies.txt não foi criado.")

# 🔧 Reconstrói o arquivo logo no início da aplicação
write_cookies_file()

app = Flask(__name__)
CORS(app)

@app.route('/api/playlist', methods=['POST'])
def get_playlist():
    inicio_total = time.time()
    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({"error": "Nenhum link fornecido"}), 400

    print(f"[INÍCIO] Processando link da playlist: {link}")

    inicio_auth = time.time()
    spotify = spotify_auth()
    print(f"[SPOTIFY AUTH] Tempo de autenticação: {time.time() - inicio_auth:.2f} segundos")

    inicio_spotify = time.time()
    type_id, item_id = extract_id(link)
    if not type_id or type_id != 'playlist':
        return jsonify({"error": "Link inválido ou não é uma playlist"}), 400

    tracks = get_spotify_items(spotify, type_id, item_id)
    playlist_name = get_spotify_name(spotify, type_id, item_id)
    print(f"[SPOTIFY DATA] Tempo para buscar nome e músicas: {time.time() - inicio_spotify:.2f} segundos")

    inicio_youtube = time.time()
    result = [None] * len(tracks)

    def process_track(index, track):
        yt_start = time.time()
        youtube_url = search_youtube(track)
        duration = time.time() - yt_start
        print(f"[YOUTUBE] ({index + 1}/{len(tracks)}) '{track}' → {duration:.2f} segundos")
        return index, {"title": track, "youtubeUrl": youtube_url}

    with ThreadPoolExecutor(max_workers=min(50, len(tracks))) as executor:
        futures = [executor.submit(process_track, i, track) for i, track in enumerate(tracks)]
        for future in as_completed(futures):
            index, data = future.result()
            result[index] = data

    print(f"[YOUTUBE] Tempo total paralelo: {time.time() - inicio_youtube:.2f} segundos")
    print(f"[TOTAL] Tempo total da requisição: {time.time() - inicio_total:.2f} segundos")

    return jsonify({"name": playlist_name, "tracks": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    app.run(debug=True, host="0.0.0.0", port=port)
