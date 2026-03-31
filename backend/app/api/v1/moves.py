from fastapi import APIRouter, HTTPException, Path

from app.models.chess import MovesResponse, TheoreticalMove
from app.services.lichess import get_theoretical_moves

router = APIRouter()


@router.get("/moves/{fen:path}", response_model=MovesResponse)
async def get_moves(
    fen: str = Path(
        ...,
        example="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ),
) -> MovesResponse:
    """Retourne les coups théoriques issus de la base masters Lichess pour une position FEN."""
    try:
        data = await get_theoretical_moves(fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Lichess explorer timeout")
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    moves = [
        TheoreticalMove(
            uci=m["uci"],
            san=m["san"],
            white=m["white"],
            draws=m["draws"],
            black=m["black"],
        )
        for m in data.get("moves", [])
    ]
    return MovesResponse(fen=fen, moves=moves)
