import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from flask_cors import CORS


# Importa funções do script.py
from script import (
    extract_id,
    spotify_auth,
    get_spotify_name,
    get_spotify_items,
    search_youtube,
)

app = Flask(__name__)
CORS(app, origins=["https://spotyload-frontend-flask.vercel.app"])

@app.route("/api/playlist", methods=["POST"])
def get_playlist():
    t0 = time.time()
    data = request.get_json()
    link = data.get("link")

    if not link:
        return jsonify({"error": "Nenhum link fornecido"}), 400

    print(f"[INÍCIO] Processando link: {link}")

    # --- Autenticação Spotify ---
    t_auth = time.time()
    spotify = spotify_auth()
    print(f"[SPOTIFY AUTH] {time.time() - t_auth:.2f}s")

    # --- Coleta de faixas ---
    t_sp = time.time()
    type_id, item_id = extract_id(link)
    if type_id != "playlist":
        return jsonify({"error": "Link inválido ou não é playlist"}), 400

    tracks = get_spotify_items(spotify, type_id, item_id)
    playlist_name = get_spotify_name(spotify, type_id, item_id)
    print(f"[SPOTIFY DATA] {time.time() - t_sp:.2f}s  ({len(tracks)} faixas)")

    # --- Busca no YouTube ---
    t_yt = time.time()
    resultados = [None] * len(tracks)

    def process_track(idx: int, track: str):
        t = time.time()
        url = search_youtube(track)
        print("\n\nURL DO VIDEO: ", url, "\n\n")
        print(f"[YOUTUBE] ({idx+1}/{len(tracks)}) {track} → {url} ({time.time() - t:.2f}s)")
        print(f"[DEBUG] YouTube URL para '{track}': {url}")
        return idx, {"title": track, "youtubeUrl": url}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_track, i, trk) for i, trk in enumerate(tracks)]
        for f in as_completed(futures):
            idx, data_item = f.result()
            resultados[idx] = data_item

    print(f"[YOUTUBE] paralelismo: {time.time() - t_yt:.2f}s")
    print(f"[TOTAL] {time.time() - t0:.2f}s")

    return jsonify({
        "name": playlist_name,
        "tracks": resultados,
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    app.run(debug=True, host="0.0.0.0", port=port)
