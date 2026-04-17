# Backend — Chess Agent FFE

API FastAPI de l'agent IA d'apprentissage des ouvertures aux échecs.

## Stack

| Composant | Technologie |
|---|---|
| Framework | FastAPI |
| Orchestration | LangGraph |
| Vector DB | Milvus (IVF_FLAT, cosine) |
| Embeddings | all-MiniLM-L6-v2 (384 dims) |
| Moteur d'analyse | Stockfish |
| Ouvertures théoriques | Lichess Masters Explorer |
| Vidéos | YouTube Data API v3 |
| Gestionnaire de paquets | uv |

## Démarrage local (hot reload)

```bash
# Depuis la racine
make dev

# Ou directement
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Milvus doit être actif (`make up`) pour les endpoints RAG et agent.

## Endpoints

| Route | Description |
|---|---|
| `GET /api/v1/healthcheck` | Santé de l'API |
| `GET /api/v1/moves/{fen}` | Coups théoriques (base masters Lichess) |
| `GET /api/v1/evaluate/{fen}` | Évaluation Stockfish (centipawns + meilleur coup) |
| `GET /api/v1/vector-search?q=&fen=&k=` | Recherche sémantique WikiChess |
| `GET /api/v1/videos/{opening}` | Vidéos YouTube pour une ouverture |
| `POST /api/v1/agent` | Orchestration complète (body: `{"fen": "..."}`) |
| `GET /docs` | Swagger UI |

> `{fen}` accepte les slashes (`{fen:path}`) — encodage URL non obligatoire.

## Variables d'environnement

Copier `.env.example` → `.env` et renseigner :

| Variable | Description |
|---|---|
| `LICHESS_API_TOKEN` | Token Lichess (lichess.org/account/oauth/token, aucun scope requis) |
| `YOUTUBE_API_KEY` | Clé API YouTube Data v3 (100 recherches/jour en quota gratuit) |
| `MILVUS_HOST` | Hôte Milvus (`milvus` en Docker, `localhost` en local) |
| `MILVUS_PORT` | Port Milvus (défaut : 19530) |

## Base de connaissances (RAG)

Données issues de **WikiChess** (Fandom, CC-BY-SA). 8 ouvertures indexées, ~85 chunks.

```bash
# Ingérer (première fois)
make ingest

# Réingérer depuis zéro
make ingest ARGS=--reset
```

**Pipeline :** `scripts/fetch_data.py` → articles MediaWiki → `data/*.json`
→ `scripts/ingest.py` → embeddings MiniLM → Milvus (`chess_openings`)

## Structure

```
app/
├── api/v1/          # Routers FastAPI (moves, evaluate, vector_search, videos, agent)
├── models/          # Modèles Pydantic
└── services/        # lichess, stockfish_service, milvus_service, youtube_service, agent_service
data/                # Articles WikiChess (JSON)
scripts/             # fetch_data.py, ingest.py
```
