from fastapi import APIRouter, HTTPException

from app.models.chess import (
    AgentRequest,
    AgentResponse,
    EvaluationResponse,
    TheoreticalMove,
    VideoResult,
    VectorSearchResult,
)
from app.services.agent_service import run_agent

router = APIRouter()


@router.post("/agent", response_model=AgentResponse)
async def agent_endpoint(body: AgentRequest) -> AgentResponse:
    """Orchestre tous les outils (Lichess, Stockfish, Milvus, YouTube) pour une position FEN."""
    try:
        state = await run_agent(body.fen)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return AgentResponse(
        fen=state["fen"],
        opening_name=state["opening_name"],
        is_theoretical=state["is_theoretical"],
        moves=[
            TheoreticalMove(
                uci=m["uci"],
                san=m["san"],
                white=m["white"],
                draws=m["draws"],
                black=m["black"],
            )
            for m in state["moves"]
        ],
        evaluation=(
            EvaluationResponse(fen=state["fen"], **state["evaluation"])
            if state["evaluation"]
            else None
        ),
        rag_context=[VectorSearchResult(**r) for r in state["rag_context"]],
        videos=[VideoResult(**v) for v in state["videos"]],
    )
