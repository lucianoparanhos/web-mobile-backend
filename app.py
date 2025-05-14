from flask import Flask, request, jsonify  # Importa o Flask para criar a aplicação e os módulos para tratar requisições
from flask_cors import CORS  # Importa CORS para permitir requisições de diferentes origens
from script import extract_id, spotify_auth, get_spotify_name, get_spotify_items, search_youtube  # Importa as funções do script.py
import time  # Importa o módulo de tempo para medir o tempo de execução
from concurrent.futures import ThreadPoolExecutor, as_completed  # Importa o executor de threads para executar tarefas em paralelo

app = Flask(__name__)  # Cria uma instância da aplicação Flask
CORS(app)  # Habilita CORS para permitir que o frontend faça requisições para o backend

@app.route('/api/playlist', methods=['POST'])  # Define uma rota para o endpoint /api/playlist com método POST
def get_playlist():
    inicio_total = time.time()  # Marca o tempo de início da requisição
    data = request.get_json()  # Obtém os dados em formato JSON da requisição
    link = data.get('link')  # Obtém o link da playlist

    if not link:  # Se o link não for fornecido
        return jsonify({"error": "Nenhum link fornecido"}), 400  # Retorna um erro

    print(f"[INÍCIO] Processando link da playlist: {link}")

    # Autenticação no Spotify
    inicio_auth = time.time()
    spotify = spotify_auth()  # Realiza a autenticação no Spotify
    print(f"[SPOTIFY AUTH] Tempo de autenticação: {time.time() - inicio_auth:.2f} segundos")

    # Busca as músicas e nome da playlist
    inicio_spotify = time.time()
    type_id, item_id = extract_id(link)  # Extrai o tipo e ID do link
    if not type_id or type_id != 'playlist':  # Se o tipo não for válido ou não for uma playlist
        return jsonify({"error": "Link inválido ou não é uma playlist"}), 400  # Retorna um erro

    tracks = get_spotify_items(spotify, type_id, item_id)  # Obtém as faixas da playlist
    playlist_name = get_spotify_name(spotify, type_id, item_id)  # Obtém o nome da playlist
    print(f"[SPOTIFY DATA] Tempo para buscar nome e músicas: {time.time() - inicio_spotify:.2f} segundos")

    # Busca os links no YouTube com paralelismo
    inicio_youtube = time.time()
    result = [None] * len(tracks)  # Lista para armazenar os resultados das músicas

    def process_track(index, track):  # Função para processar cada música e buscar seu link no YouTube
        yt_start = time.time()  # Marca o tempo de início da busca do YouTube
        youtube_url = search_youtube(track)  # Busca o link no YouTube
        duration = time.time() - yt_start  # Calcula a duração da busca
        print(f"[YOUTUBE] ({index + 1}/{len(tracks)}) '{track}' → {duration:.2f} segundos")
        return index, {"title": track, "youtubeUrl": youtube_url}  # Retorna o índice da música e o link do YouTube

    # Executa as buscas do YouTube em paralelo para cada música
    with ThreadPoolExecutor(max_workers=min(50, len(tracks))) as executor:
        futures = [executor.submit(process_track, i, track) for i, track in enumerate(tracks)]  # Cria as tarefas para as threads
        for future in as_completed(futures):  # Quando uma tarefa for completada
            index, data = future.result()  # Obtém o resultado da tarefa
            result[index] = data  # Preserva a ordem das músicas original

    print(f"[YOUTUBE] Tempo total paralelo: {time.time() - inicio_youtube:.2f} segundos")
    print(f"[TOTAL] Tempo total da requisição: {time.time() - inicio_total:.2f} segundos")

    return jsonify({"name": playlist_name, "tracks": result})  # Retorna o nome da playlist e os links do YouTube das músicas

if __name__ == "__main__":  # Se o script for executado diretamente
    app.run(debug=True, port=3001)  # Inicia o servidor Flask na porta 3001
