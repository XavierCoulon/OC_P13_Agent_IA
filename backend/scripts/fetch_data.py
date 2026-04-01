#!/usr/bin/env python3
"""
Scrape les articles WikiChess (Fandom/MediaWiki) et génère les fichiers JSON
dans backend/data/ au format attendu par ingest.py.

Usage (depuis backend/) :
    uv run python scripts/fetch_data.py

Source : https://chess.fandom.com — licence CC-BY-SA
"""
import json
import re
import time
from pathlib import Path

import httpx

API_URL = "https://chess.fandom.com/api.php"
DATA_DIR = Path(__file__).parent.parent / "data"
CHUNK_MIN = 150
CHUNK_MAX = 600

OPENINGS = [
    ("sicilian.json",     "Sicilian Defense",      "Sicilian_Defense"),
    ("ruy_lopez.json",    "Ruy Lopez",             "Ruy_Lopez"),
    ("italian.json",      "Italian Game",          "Italian_Game"),
    ("french.json",       "French Defense",        "French_Defense"),
    ("caro_kann.json",    "Caro-Kann Defense",     "Caro-Kann_Defense"),
    ("kings_indian.json", "King's Indian Defense", "King's_Indian_Defense"),
    ("queens_gambit.json","Queen's Gambit",        "Queen's_Gambit"),
    ("english.json",      "English Opening",       "English_Opening"),
    ("nimzo_indian.json", "Nimzo-Indian Defense",  "Nimzo-Indian_Defense"),
    ("dutch.json",        "Dutch Defense",         "Dutch_Defense"),
]


def fetch_wikitext(title: str) -> str:
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    }
    r = httpx.get(API_URL, params=params, timeout=15.0)
    r.raise_for_status()
    data = r.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "revisions" not in page:
        return ""
    slots = page["revisions"][0].get("slots", {})
    if slots:
        return slots.get("main", {}).get("*", "")
    return page["revisions"][0].get("*", "")


def clean_wikitext(text: str) -> str:
    # Supprimer les templates {{...}}
    text = re.sub(r"\{\{[^}]*\}\}", " ", text, flags=re.DOTALL)
    # Supprimer les balises <ref>...</ref> et <ref ... />
    text = re.sub(r"<ref[^>]*>.*?</ref>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^/]*/?>", " ", text)
    # Conserver le texte des liens [[texte|affichage]] → affichage, [[texte]] → texte
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    # Supprimer les liens externes [url texte] → texte
    text = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\]", "", text)
    # Supprimer le markup de formatage '' ''' ''''
    text = re.sub(r"'{2,}", "", text)
    # Supprimer les balises HTML restantes
    text = re.sub(r"<[^>]+>", " ", text)
    # Supprimer les lignes de fichier/image
    text = re.sub(r"^\s*(?:File|Image|Fichier):.*$", "", text, flags=re.MULTILINE)
    # Supprimer les lignes de catégorie
    text = re.sub(r"^\s*\[\[(?:Category|Catégorie):.*$", "", text, flags=re.MULTILINE)
    # Nettoyer les espaces multiples
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text: str) -> list[str]:
    """Découpe le texte en chunks par section (==), puis par paragraphe si trop long."""
    chunks: list[str] = []

    # Découper par sections de niveau 2 ou 3
    sections = re.split(r"\n={2,3}[^=]+={2,3}\n", text)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Découper la section en paragraphes
        paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]

        current = ""
        for para in paragraphs:
            # Ignorer les paragraphes trop courts (titres, listes isolées)
            if len(para) < 30:
                continue

            if len(current) + len(para) + 1 <= CHUNK_MAX:
                current = (current + " " + para).strip() if current else para
            else:
                if len(current) >= CHUNK_MIN:
                    chunks.append(current)
                current = para if len(para) <= CHUNK_MAX else para[:CHUNK_MAX]

        if len(current) >= CHUNK_MIN:
            chunks.append(current)

    return chunks


def process_opening(filename: str, opening_name: str, wiki_title: str) -> int:
    print(f"  Fetching '{wiki_title}'...", end=" ", flush=True)
    raw = fetch_wikitext(wiki_title)
    if not raw:
        print("VIDE — ignoré")
        return 0

    cleaned = clean_wikitext(raw)
    chunks = split_into_chunks(cleaned)

    doc = {
        "opening_name": opening_name,
        "chunks": [{"index": i, "text": chunk} for i, chunk in enumerate(chunks)],
    }

    out_path = DATA_DIR / filename
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(chunks)} chunks → {filename}")
    return len(chunks)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for filename, opening_name, wiki_title in OPENINGS:
        try:
            n = process_opening(filename, opening_name, wiki_title)
            total += n
        except Exception as e:
            print(f"ERREUR pour {wiki_title}: {e}")
        time.sleep(0.5)  # politesse envers l'API

    print(f"\nTerminé — {total} chunks au total dans {DATA_DIR}")


if __name__ == "__main__":
    main()
