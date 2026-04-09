from fastapi import APIRouter, HTTPException, Path

from app.models.chess import VideoResult, VideosResponse
from app.services.youtube_service import search_videos

router = APIRouter()


@router.get("/videos/{opening}", response_model=VideosResponse)
async def get_videos(
    opening: str = Path(
        ...,
        example="Sicilian Defense",
        description="Nom de l'ouverture d'échecs",
    ),
) -> VideosResponse:
    """Recherche des vidéos YouTube explicatives pour une ouverture d'échecs."""
    try:
        videos = await search_videos(opening)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="YouTube API timeout")
    except RuntimeError as e:
        msg = str(e)
        if "quota" in msg.lower():
            raise HTTPException(status_code=503, detail=msg)
        raise HTTPException(status_code=502, detail=msg)

    return VideosResponse(
        opening=opening,
        videos=[VideoResult(**v) for v in videos],
    )
