from pydantic import BaseModel


class TheoreticalMove(BaseModel):
    uci: str    # ex: "e2e4"
    san: str    # ex: "e4"
    white: int  # nb victoires blancs dans la base masters
    draws: int
    black: int


class MovesResponse(BaseModel):
    fen: str
    moves: list[TheoreticalMove]


class EvaluationResponse(BaseModel):
    fen: str
    score_cp: int | None   # centipawns (None si mat détecté)
    mate_in: int | None    # None si pas de mat
    best_move_uci: str     # ex: "e2e4"
    best_move_san: str     # ex: "e4"


class VectorSearchResult(BaseModel):
    opening_name: str
    chunk_text: str
    chunk_index: int
    score: float  # similarité cosine [0.0, 1.0]


class VectorSearchResponse(BaseModel):
    query: str
    results: list[VectorSearchResult]
