.PHONY: up down logs health dev help

help: ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Démarrer tous les services (build inclus)
	docker compose up --build

down: ## Arrêter et supprimer les conteneurs
	docker compose down

logs: ## Suivre les logs de l'API
	docker compose logs -f api

health: ## Vérifier le healthcheck de l'API
	curl -s http://localhost:$${API_PORT:-8000}/api/v1/healthcheck | python3 -m json.tool

dev: ## Lancer l'API en mode développement local (hot reload)
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
