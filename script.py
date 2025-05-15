import os  # Importa o módulo para interagir com o sistema operacional
import re  # Importa o módulo para trabalhar com expressões regulares (não utilizado neste código)
import spotipy  # Importa a biblioteca Spotipy para interagir com a API do Spotify
from spotipy.oauth2 import SpotifyClientCredentials  # Importa a classe para autenticação via credenciais do cliente no Spotify
import yt_dlp  # Importa a biblioteca yt-dlp para buscar vídeos no YouTube

# from youtubesearchpython import VideosSearch  # Linha comentada, não está sendo usada no código

from dotenv import load_dotenv  # Importa a função para carregar variáveis de ambiente de um arquivo .env

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

# Credenciais do Spotify
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")  # Obtém o ID do cliente do Spotify da variável de ambiente
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")  # Obtém o segredo do cliente do Spotify da variável de ambiente

def spotify_auth():
    """
    Autentica e retorna o cliente Spotify.
    """
    auth = SpotifyClientCredentials(  # Cria um objeto para gerenciar as credenciais do cliente Spotify
        client_id=SPOTIFY_CLIENT_ID,  # Usando o ID do cliente do Spotify
        client_secret=SPOTIFY_CLIENT_SECRET  # Usando o segredo do cliente do Spotify
    )
    return spotipy.Spotify(client_credentials_manager=auth)  # Retorna um objeto Spotify autenticado

def extract_id(link):
    """
    Extrai o tipo e o ID de um link do Spotify (playlist, álbum ou música).
    """
    try:
        parts = link.split("/")  # Divide o link do Spotify em partes com base nas barras "/"
        type_id = parts[-2]  # O tipo do item (playlist, álbum ou faixa) está na penúltima parte
        item_id = parts[-1].split("?")[0]  # O ID do item está na última parte, antes do "?" (caso haja parâmetros)
        return type_id, item_id  # Retorna o tipo e o ID do item extraídos
    except:
        return None, None  # Se algo der errado, retorna None para ambos

def get_spotify_name(sp, type_id, item_id):
    """
    Obtém o nome da playlist, álbum ou música com base no tipo e ID.
    """
    if type_id == "playlist":  # Se for uma playlist
        playlist = sp.playlist(item_id)  # Obtém os dados da playlist do Spotify
        return playlist['name']  # Retorna o nome da playlist
    return f"{type_id.capitalize()} {item_id}"  # Para outros tipos de itens, retorna uma string formatada com o tipo e ID

def get_spotify_items(spotify, type_id, item_id):
    """
    Retorna a lista de faixas de uma playlist, álbum ou faixa no Spotify.
    """
    tracks = []  # Lista para armazenar as faixas
    try:
        if type_id == "playlist":  # Se for uma playlist
            results = spotify.playlist_tracks(item_id)  # Obtém as faixas da playlist
            while results:  # Enquanto houver resultados
                for item in results['items']:  # Para cada item nas faixas
                    track = item['track']  # Obtém os dados da faixa
                    if track:  # Se a faixa existir
                        artist = track['artists'][0]['name']  # Obtém o nome do primeiro artista da faixa
                        tracks.append(f"{artist} - {track['name']}")  # Adiciona o nome do artista e da música à lista de faixas
                # Vai para a próxima página de resultados, se houver
                results = spotify.next(results) if results['next'] else None
        elif type_id == "album":  # Se for um álbum
            results = spotify.album_tracks(item_id)  # Obtém as faixas do álbum
            for item in results['items']:  # Para cada faixa no álbum
                artist = item['artists'][0]['name']  # Obtém o nome do primeiro artista
                tracks.append(f"{artist} - {item['name']}")  # Adiciona à lista de faixas
        elif type_id == "track":  # Se for uma música específica
            track = spotify.track(item_id)  # Obtém os dados da faixa
            artist = track['artists'][0]['name']  # Obtém o nome do artista
            tracks.append(f"{artist} - {track['name']}")  # Adiciona à lista de faixas
        return tracks  # Retorna a lista de faixas
    except Exception as e:
        print(f"Erro ao obter músicas do Spotify: {e}")  # Se ocorrer algum erro, imprime o erro
        return []  # Retorna uma lista vazia

def search_youtube(query):
    """
    Realiza a busca do vídeo no YouTube com base na consulta.
    """
    try:
        ydl_opts = {  # Configurações para a busca no YouTube via yt-dlp
            'quiet': True,  # Impede mensagens extras durante o processo
            'skip_download': True,  # Não baixa o vídeo, apenas busca informações
            'default_search': 'ytsearch1',  # Realiza a pesquisa diretamente no YouTube
            'noplaylist': True,  # Impede a busca de playlists
            'cookiefile': 'cookies.txt',  # Usa o arquivo de cookies para autenticação e evitar problemas com o bot do youtube
        }

        # Usa yt-dlp para buscar o vídeo
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)  # Extrai informações do YouTube sem baixar o vídeo
            if 'entries' in result and result['entries']:  # Se houver resultados
                return result['entries'][0]['webpage_url']  # Retorna a URL do primeiro vídeo encontrado
            else:
                return None  # Se não houver resultados, retorna None
    except Exception as e:
        print(f"Erro na busca do YouTube para '{query}': {e}")  # Se ocorrer erro, imprime a mensagem
        return None  # Retorna None em caso de erro

def main():
    """
    Função principal que recebe os links do Spotify e busca os vídeos do YouTube correspondentes.
    """
    links = input("Cole os links de playlists, álbuns ou músicas do Spotify separados por vírgula:\n").split(',')  # Solicita os links e os divide em uma lista
    links = [url.strip() for url in links if url.strip()]  # Remove espaços extras e filtra links vazios
    if not links:  # Se a lista de links estiver vazia
        print("❌ Nenhum link válido!")  # Exibe mensagem de erro
        return

    # Autentica no Spotify
    spotify = spotify_auth()

    for link in links:  # Para cada link na lista de links
        type_id, item_id = extract_id(link)  # Extrai o tipo e o ID do link do Spotify

        if type_id:  # Se o tipo for válido
            print(f"Buscando músicas na {type_id} com ID {item_id}...")  # Exibe mensagem de busca
            tracks = get_spotify_items(spotify, type_id, item_id)  # Obtém as faixas do Spotify
            for track in tracks:  # Para cada faixa
                print(f" - {track}")  # Exibe a faixa
            youtube_link = search_youtube(tracks[0])  # Busca o link do YouTube para a primeira música
            print(f"Link do YouTube: {youtube_link}")  # Exibe o link do YouTube
        else:
            print(f"❌ Link inválido: {link}")  # Se o tipo for inválido, exibe erro

if __name__ == "__main__":  # Se o script for executado diretamente
    main()  # Chama a função principal
