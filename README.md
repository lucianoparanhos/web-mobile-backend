
---

# README - Backend da Aplicação Spotify para YouTube

Este repositório contém o backend da aplicação que recebe links de playlists, álbuns ou músicas do Spotify, busca as faixas associadas e retorna os links correspondentes no YouTube. O backend é construído com Flask e utiliza APIs do Spotify e do YouTube para realizar as buscas.

## Tecnologias Utilizadas

* **Python 3.x**: Linguagem de programação utilizada para o desenvolvimento do backend.
* **Flask**: Framework web para Python utilizado para criar a API RESTful.
* **Spotipy**: Biblioteca Python para interagir com a API do Spotify.
* **yt-dlp**: Biblioteca Python para buscar vídeos no YouTube.
* **dotenv**: Utilizado para carregar variáveis de ambiente de um arquivo `.env`.
* **ThreadPoolExecutor**: Utilizado para processar as requisições ao YouTube em paralelo.

## Pré-Requisitos

Antes de rodar o projeto, você precisa instalar as dependências. Certifique-se de ter o Python 3.x instalado em sua máquina.

1. Clone o repositório para sua máquina:

   ```bash
   https://github.com/wfmunizj/web-mobile-backend.git
   cd web-mobile-backend
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use `venv\Scripts\activate`
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz do projeto com as credenciais da API do Spotify, pode ser obtido pelo link abaixo. Exemplo de conteúdo:

   ```
   https://developer.spotify.com/

   SPOTIFY_CLIENT_ID=seu_spotify_client_id
   SPOTIFY_CLIENT_SECRET=seu_spotify_client_secret
   ```

## Endpoints da API

### 1. `/api/playlist` - Obter links de vídeos do YouTube a partir de uma playlist do Spotify

**Método**: `POST`

**Descrição**: Este endpoint recebe um link do Spotify (pode ser uma playlist, álbum ou música) e retorna as músicas contidas no link, junto com seus respectivos links no YouTube.

**Corpo da Requisição (JSON)**:

```json
{
  "link": "https://open.spotify.com/playlist/{playlist_id}"
}
```

**Resposta (JSON)**:

```json
{
  "name": "Nome da Playlist",
  "tracks": [
    {
      "title": "Nome da Música",
      "youtubeUrl": "https://www.youtube.com/watch?v=XXXXXXXXXXX"
    },
    ...
  ]
}
```

**Exemplo de Requisição**:

```bash
curl -X POST http://localhost:3001/api/playlist -H "Content-Type: application/json" -d '{"link": "https://open.spotify.com/playlist/37i9dQZF1DX0XUsfpRnxkJ"}'
```

**Exemplo de Resposta**:

```json
{
  "name": "Chill Hits",
  "tracks": [
    {
      "title": "Artist - Song",
      "youtubeUrl": "https://www.youtube.com/watch?v=XXXXXXXXXXX"
    },
    {
      "title": "Artist - Song",
      "youtubeUrl": "https://www.youtube.com/watch?v=YYYYYYYYYYY"
    }
  ]
}
```

## Como Funciona

### 1. **Autenticação no Spotify**:

A autenticação é feita usando a API do Spotify, através das credenciais `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET`. O código utiliza a biblioteca **Spotipy** para autenticar e acessar as informações sobre playlists, álbuns e faixas no Spotify.

### 2. **Extração do ID do Spotify**:

A função `extract_id()` recebe um link do Spotify e extrai o tipo do item (playlist, álbum ou música) e o seu respectivo ID. O link é dividido com base nas barras (`/`) e a função retorna o tipo do item e o ID.

### 3. **Busca das Faixas**:

Com o tipo e o ID extraídos, a função `get_spotify_items()` é chamada para buscar as faixas associadas. Dependendo do tipo (playlist, álbum ou música), as faixas são extraídas e armazenadas em uma lista com o formato "Artista - Música".

### 4. **Busca no YouTube**:

Após obter a lista de faixas do Spotify, a função `search_youtube()` é chamada para cada faixa. O código utiliza a biblioteca **yt-dlp** para buscar o link do vídeo correspondente no YouTube. O yt-dlp é configurado para procurar vídeos no YouTube sem fazer o download, apenas extraindo a URL do vídeo.

### 5. **Processamento Paralelo**:

A busca dos links no YouTube é realizada de forma paralela utilizando o `ThreadPoolExecutor`. Isso permite que as buscas para todas as músicas sejam feitas ao mesmo tempo, melhorando a performance da aplicação.

### 6. **Resposta ao Cliente**:

Após processar todas as faixas e obter os links do YouTube, o backend retorna um JSON contendo o nome da playlist e os links para os vídeos do YouTube.

## Estrutura do Projeto

O projeto é composto pelos seguintes arquivos principais:

```
web-mobile-backend/
├── app.py               # Código principal do backend com o Flask
├── script.py            # Lógica de integração com Spotify e YouTube
├── requirements.txt     # Lista de dependências do projeto
├── .env                 # Arquivo para armazenar credenciais do Spotify
└── README.md            # Este arquivo
```

## Como Rodar

1. **Execute o backend**:
   Após instalar as dependências e configurar as variáveis de ambiente, você pode rodar o servidor Flask com o seguinte comando:

   ```bash
   python app.py
   ```

2. O servidor será iniciado na porta `3001`. Agora, você pode fazer requisições para o endpoint `/api/playlist`, lembre-se o front-end deve estar rodando em paralelo, link para o repositório abaixo.

    ```
    https://github.com/wfmunizj/web-mobile-frontend
    ```

3. **Testando a API**:
   Você pode testar o endpoint da API com ferramentas como **Postman** ou **cURL**. Aqui está um exemplo de como fazer uma requisição usando o cURL:

   ```bash
   curl -X POST http://localhost:3001/api/playlist -H "Content-Type: application/json" -d '{"link": "https://open.spotify.com/playlist/37i9dQZF1DX0XUsfpRnxkJ"}'
   ```

## Logs e Monitoramento

O backend possui logs básicos para acompanhar o tempo de execução de cada etapa, incluindo autenticação no Spotify, busca de músicas e links do YouTube, e a execução paralela. Os logs são impressos no console e podem ser úteis para diagnóstico de problemas.

## Possíveis Melhorias

* **Validação dos Links**: Melhorar a validação dos links para garantir que sejam apenas links válidos do Spotify.
* **Cache de Resultados**: Implementar caching para evitar buscas repetidas ao YouTube para as mesmas músicas.
* **Escalabilidade**: Melhorar a escalabilidade do backend para processar grandes playlists de forma mais eficiente.

---
