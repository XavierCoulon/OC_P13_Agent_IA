from fastapi import APIRouter, HTTPException, Path

from app.models.chess import EvaluationResponse
from app.services.stockfish_service import evaluate_position

router = APIRouter()


@router.get("/evaluate/{fen:path}", response_model=EvaluationResponse)
async def get_evaluation(
    fen: str = Path(
        ...,
        example="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ),
) -> EvaluationResponse:
    """Évalue une position FEN avec Stockfish et retourne le score et le meilleur coup."""
    try:
        result = await evaluate_position(fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return EvaluationResponse(fen=fen, **result)
