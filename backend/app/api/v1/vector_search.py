from fastapi import APIRouter, HTTPException, Query

from app.models.chess import VectorSearchResponse, VectorSearchResult
from app.services import milvus_service

router = APIRouter()


@router.get("/vector-search", response_model=VectorSearchResponse)
async def vector_search(
    q: str | None = Query(None, description="Recherche texte libre", example="Sicilian defense najdorf variation"),
    fen: str | None = Query(None, description="Position FEN", example="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"),
    k: int = Query(3, ge=1, le=10, description="Nombre de résultats"),
) -> VectorSearchResponse:
    """Recherche sémantique dans la base de connaissances des ouvertures d'échecs."""
    if q is None and fen is None:
        raise HTTPException(status_code=400, detail="Paramètre 'q' ou 'fen' requis")

    query_text = q if q is not None else f"chess position {fen}"

    try:
        raw_results = await milvus_service.search(query_text, top_k=k)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Milvus indisponible: {e}")

    return VectorSearchResponse(
        query=query_text,
        results=[VectorSearchResult(**r) for r in raw_results],
    )
