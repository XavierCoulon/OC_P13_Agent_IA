import asyncio
import logging
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

MAX_RESULTS = 5

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    key = os.getenv("YOUTUBE_API_KEY", "")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY non configurée")
    return key


def _search_sync(opening: str) -> list[dict]:
    api_key = _get_api_key()
    query = f"{opening} chess opening tutorial explanation"

    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        response = (
            youtube.search()
            .list(
                q=query,
                part="snippet",
                type="video",
                maxResults=MAX_RESULTS,
                videoEmbeddable="true",
                videoDuration="medium",
                relevanceLanguage="en",
            )
            .execute()
        )
    except HttpError as e:
        status = e.status_code
        if status in (403, 429):
            logger.warning(
                "YouTube API quota dépassé ou accès refusé (HTTP %s) pour: %r",
                status,
                opening,
            )
            raise RuntimeError(f"YouTube quota dépassé (HTTP {status})") from e
        raise RuntimeError(f"YouTube erreur HTTP {status}") from e

    results = []
    for item in response.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        snippet = item.get("snippet", {})
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
            or ""
        )
        results.append({
            "videoId": video_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channelTitle": snippet.get("channelTitle", ""),
            "publishedAt": snippet.get("publishedAt", ""),
            "thumbnailUrl": thumbnail_url,
            "watchUrl": f"https://youtube.com/watch?v={video_id}",
            "embedUrl": f"https://www.youtube.com/embed/{video_id}",
        })
    return results


async def search_videos(opening: str) -> list[dict]:
    """Recherche des vidéos YouTube pour une ouverture d'échecs.

    Raises:
        RuntimeError: clé API manquante, quota dépassé ou erreur HTTP.
    """
    return await asyncio.to_thread(_search_sync, opening)
