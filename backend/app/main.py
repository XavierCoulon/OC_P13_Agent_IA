from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup : initialisation des connexions (Milvus, MongoDB...)
    yield
    # Shutdown : libération des ressources


app = FastAPI(
    title="Chess Agent API",
    version="0.1.0",
    description="POC Agent IA Ouvertures Échecs - FFE",
    lifespan=lifespan,
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
