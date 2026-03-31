import chess
import chess.engine

STOCKFISH_PATH = "/usr/games/stockfish"
ANALYSIS_TIME = 0.1  # secondes — suffisant pour un POC


async def evaluate_position(fen: str) -> dict:
    """Évalue une position FEN avec Stockfish.

    Retourne le score en centipawns (ou mat en N coups) et le meilleur coup.

    Raises:
        ValueError: si le FEN est invalide.
        RuntimeError: si le binaire Stockfish n'est pas disponible.
    """
    board = chess.Board(fen)  # lève ValueError si FEN invalide

    try:
        transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)
    except FileNotFoundError as e:
        raise RuntimeError("Stockfish non disponible — binaire introuvable") from e

    try:
        info = await engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME))
    finally:
        await engine.quit()

    pov_score = info.get("score")
    if pov_score is None:
        raise RuntimeError("Stockfish n'a retourné aucun score")
    score = pov_score.white()  # PovScore depuis la perspective des blancs
    best_move = info.get("pv", [None])[0]

    return {
        "score_cp": None if score.is_mate() else score.score(),
        "mate_in": score.mate() if score.is_mate() else None,
        "best_move_uci": best_move.uci() if best_move else "",
        "best_move_san": board.san(best_move) if best_move else "",
    }
