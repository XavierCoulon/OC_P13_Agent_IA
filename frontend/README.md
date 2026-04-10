# Frontend — Chess Agent FFE

Interface Angular de l'agent IA d'apprentissage des ouvertures aux échecs.

## Stack

| Composant | Technologie |
|---|---|
| Framework | Angular 21 (standalone components) |
| Échiquier | ngx-chess-board 2.2.3 |
| HTTP | Angular HttpClient |
| Style | CSS natif |

## Démarrage

```bash
# Depuis la racine du projet
make front

# Ou directement
cd frontend && ng serve
```

> Le backend doit être actif (`make up`) pour que les appels API fonctionnent.
> L'application tourne sur [http://localhost:4200](http://localhost:4200).

## Proxy

En développement, les requêtes vers `/api` sont redirigées vers `http://localhost:8000` via `proxy.conf.json`.

## Structure

```
src/app/
├── components/
│   ├── chessboard/       # Échiquier interactif (ngx-chess-board)
│   └── agent-panel/      # Panneau de recommandations de l'agent
├── models/
│   └── chess.model.ts    # Types TypeScript (AgentResponse, VideoResult…)
├── services/
│   └── chess-api.ts      # HttpClient → POST /api/v1/agent
├── app.ts                # Composant racine (orchestration)
└── app.config.ts         # provideHttpClient
```

## Build production

```bash
npm run build
# Artifacts dans dist/chess-agent/
```
