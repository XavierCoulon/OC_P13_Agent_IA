import os

import chess
import httpx

EXPLORER_URL = "https://explorer.lichess.ovh/masters"
TIMEOUT_SECONDS = 5.0


def _get_headers() -> dict:
    token = os.getenv("LICHESS_API_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def get_theoretical_moves(fen: str) -> dict:
    """Retourne les coups théoriques depuis la base masters Lichess pour une position FEN.

    Raises:
        ValueError: si le FEN est invalide.
        TimeoutError: si l'API Lichess ne répond pas dans le délai imparti.
        RuntimeError: si l'API Lichess retourne une erreur HTTP.
    """
    chess.Board(fen)  # lève ValueError si FEN invalide

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, headers=_get_headers()) as client:
        try:
            response = await client.get(EXPLORER_URL, params={"fen": fen})
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise TimeoutError("Lichess explorer timeout") from e
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 429:
                raise RuntimeError(
                    "Rate limit Lichess atteint, réessaie dans quelques secondes"
                ) from e
            raise RuntimeError(f"Lichess erreur HTTP {status}") from e

    return response.json()
