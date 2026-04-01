import asyncio
import os

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
COLLECTION_NAME = "chess_openings"
EMBEDDING_DIM = 384

_collection: Collection | None = None
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _init_milvus_sync() -> None:
    global _collection
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

    if utility.has_collection(COLLECTION_NAME):
        _collection = Collection(COLLECTION_NAME)
        _collection.load()
        return

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="opening_name", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    ]
    schema = CollectionSchema(fields, description="Chess opening knowledge chunks")
    _collection = Collection(COLLECTION_NAME, schema)
    index_result = _collection.create_index(
        "embedding",
        {"metric_type": "IP", "index_type": "IVF_FLAT", "params": {"nlist": 128}},
    )
    _collection.load()


async def init_milvus() -> None:
    await asyncio.to_thread(_init_milvus_sync)


def _search_sync(query: str, top_k: int) -> list[dict]:
    if _collection is None:
        raise RuntimeError("Milvus non initialisé")
    model = _get_model()
    vec = model.encode([query], normalize_embeddings=True)[0].tolist()
    results = _collection.search(
        data=[vec],
        anns_field="embedding",
        param={"metric_type": "IP", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["opening_name", "chunk_text", "chunk_index"],
    )
    hits = list(results)[0]  # type: ignore[arg-type]
    return [
        {
            "opening_name": hit.entity.get("opening_name"),
            "chunk_text": hit.entity.get("chunk_text"),
            "chunk_index": hit.entity.get("chunk_index"),
            "score": round(hit.score, 4),
        }
        for hit in hits
    ]


async def search(query: str, top_k: int = 3) -> list[dict]:
    return await asyncio.to_thread(_search_sync, query, top_k)
