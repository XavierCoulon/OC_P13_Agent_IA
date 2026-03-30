# Agent IA Ouvertures Échecs — FFE

POC d'un agent IA pour l'apprentissage des ouvertures aux échecs, développé pour la Fédération Française des Échecs (FFE).

## Stack

| Composant | Technologie |
|---|---|
| Backend / Agent | FastAPI + LangGraph |
| Frontend | Angular + ngx-chessboard |
| Vector DB | Milvus |
| Document DB | MongoDB |
| Moteur d'analyse | Stockfish |
| Déploiement | Docker Compose |

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/) (pour le développement local)

## Démarrage rapide

```bash
# 1. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env pour renseigner les clés API

# 2. Démarrer tous les services
make up

# 3. Vérifier que l'API répond
make health
```

## Commandes disponibles

```
make up       Démarrer tous les services (build inclus)
make down     Arrêter et supprimer les conteneurs
make logs     Suivre les logs de l'API
make health   Vérifier le healthcheck de l'API
make dev      Lancer l'API en mode développement local (hot reload)
```

## Endpoints

| Route | Description |
|---|---|
| `GET /api/v1/healthcheck` | Santé de l'API |
| `GET /docs` | Swagger UI |

## Structure

```
.
├── backend/        # FastAPI + LangGraph
├── frontend/       # Angular
├── docker-compose.yml
├── Makefile
└── .env.example
```
