from flask import Flask, request, jsonify
from flask_cors import CORS
import concurrent.futures

# Aqui você importa suas funções: spotify_auth, extract_id, etc
from script import process_link

app = Flask(__name__)
CORS(app)  # libera para o Nuxt acessar

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    links = data.get('links', [])
    folder = data.get('folder', None)

    if not links:
        return jsonify({"error": "Nenhum link recebido"}), 400

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(links))) as executor:
        for idx, link in enumerate(links):
            executor.submit(process_link, link, idx, custom_folder=folder)

    return jsonify({"message": "Processamento iniciado!"})

if __name__ == '__main__':
    app.run(port=3001)