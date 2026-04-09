import asyncio
import logging
from typing import TypedDict

import chess
from langgraph.graph import END, START, StateGraph

from app.services import milvus_service
from app.services.lichess import get_theoretical_moves
from app.services.stockfish_service import evaluate_position
from app.services.youtube_service import search_videos

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    fen: str
    moves: list[dict]
    evaluation: dict | None
    rag_context: list[dict]
    videos: list[dict]
    opening_name: str | None
    is_theoretical: bool


async def _fetch_moves(state: AgentState) -> dict:
    try:
        data = await get_theoretical_moves(state["fen"])
    except Exception as e:
        logger.warning("Lichess error: %s", e)
        return {"moves": [], "is_theoretical": False, "opening_name": None}

    moves = data.get("moves", [])
    opening = data.get("opening") or {}
    return {
        "moves": moves,
        "is_theoretical": len(moves) > 0,
        "opening_name": opening.get("name"),
    }


async def _fetch_context(state: AgentState) -> dict:
    opening_name = state.get("opening_name")
    fen = state["fen"]

    coros = [evaluate_position(fen)]
    if opening_name:
        coros.append(milvus_service.search(opening_name))
        coros.append(search_videos(opening_name))

    results = await asyncio.gather(*coros, return_exceptions=True)

    eval_raw = results[0]
    rag_raw = results[1] if len(results) > 1 else []
    video_raw = results[2] if len(results) > 2 else []

    return {
        "evaluation": eval_raw if not isinstance(eval_raw, BaseException) else None,
        "rag_context": rag_raw if not isinstance(rag_raw, BaseException) else [],
        "videos": video_raw if not isinstance(video_raw, BaseException) else [],
    }


def _build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("fetch_moves", _fetch_moves)
    workflow.add_node("fetch_context", _fetch_context)
    workflow.add_edge(START, "fetch_moves")
    workflow.add_edge("fetch_moves", "fetch_context")
    workflow.add_edge("fetch_context", END)
    return workflow.compile()


_graph = _build_graph()


async def run_agent(fen: str) -> AgentState:
    chess.Board(fen)  # lève ValueError si FEN invalide
    initial: AgentState = {
        "fen": fen,
        "moves": [],
        "evaluation": None,
        "rag_context": [],
        "videos": [],
        "opening_name": None,
        "is_theoretical": False,
    }
    return await _graph.ainvoke(initial)  # type: ignore[return-value]
