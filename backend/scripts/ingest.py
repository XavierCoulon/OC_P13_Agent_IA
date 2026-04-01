#!/usr/bin/env python3
"""
Ingestion des données chess dans Milvus.

Prérequis : stack Docker running (milvus accessible sur localhost:19530).

Usage (depuis backend/) :
    uv run python scripts/ingest.py
    uv run python scripts/ingest.py --reset   # supprime et recrée la collection
"""
import argparse
import json
import os
import sys
from pathlib import Path

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)
from sentence_transformers import SentenceTransformer

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
COLLECTION_NAME = "chess_openings"
EMBEDDING_DIM = 384
MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = Path(__file__).parent.parent / "data"


def build_schema() -> CollectionSchema:
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="opening_name", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    ]
    return CollectionSchema(fields, description="Chess opening knowledge chunks")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Supprimer et recréer la collection")
    args = parser.parse_args()

    print(f"Connexion à Milvus {MILVUS_HOST}:{MILVUS_PORT}...")
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

    if args.reset and utility.has_collection(COLLECTION_NAME):
        print(f"Suppression de la collection '{COLLECTION_NAME}'...")
        utility.drop_collection(COLLECTION_NAME)

    if utility.has_collection(COLLECTION_NAME):
        count = Collection(COLLECTION_NAME).num_entities
        print(f"Collection '{COLLECTION_NAME}' existe déjà ({count} entités). Utilisez --reset pour réingérer.")
        sys.exit(0)

    collection = Collection(COLLECTION_NAME, build_schema())
    collection.create_index(
        "embedding",
        {"metric_type": "IP", "index_type": "IVF_FLAT", "params": {"nlist": 128}},
    )

    print(f"Chargement du modèle '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    json_files = sorted(DATA_DIR.glob("*.json"))
    if not json_files:
        print(f"Aucun fichier JSON trouvé dans {DATA_DIR}")
        sys.exit(1)

    opening_names, chunk_texts, chunk_indices, texts_to_embed = [], [], [], []
    for path in json_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        name = doc["opening_name"]
        for chunk in doc["chunks"]:
            opening_names.append(name)
            chunk_texts.append(chunk["text"][:2000])
            chunk_indices.append(chunk["index"])
            texts_to_embed.append(chunk["text"])
        print(f"  {path.name}: {len(doc['chunks'])} chunks ({name})")

    print(f"\nEncodage de {len(texts_to_embed)} chunks...")
    embeddings = model.encode(texts_to_embed, normalize_embeddings=True, show_progress_bar=True)

    print("Insertion dans Milvus...")
    collection.insert([opening_names, chunk_texts, chunk_indices, embeddings.tolist()])
    collection.flush()
    collection.load()

    print(f"\nTerminé — {collection.num_entities} entités dans '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
