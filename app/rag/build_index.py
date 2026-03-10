from __future__ import annotations


import os
from typing import Any, Dict, List, Tuple

from app.rag.chunking import chunk_text
from app.rag.embedder import LocalEmbedder
from app.rag.index_io import save_index


def _read_txt_files(docs_dir: str) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for name in sorted(os.listdir(docs_dir)):
        if not name.lower().endswith(".txt"):
            continue
        path = os.path.join(docs_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            items.append((name, f.read()))
    return items


def build_and_save_index() -> None:
    docs_dir = os.getenv("RESBOT_DOCS_DIR", "data/docs")
    index_dir = os.getenv("RESBOT_INDEX_DIR", "data/index")
    chunk_size = int(os.getenv("RESBOT_CHUNK_SIZE", "200"))
    overlap = int(os.getenv("RESBOT_CHUNK_OVERLAP", "40"))

    if not os.path.isdir(docs_dir):
        raise RuntimeError(f"Docs dir not found: {docs_dir}")

    docs = _read_txt_files(docs_dir)
    if not docs:
        raise RuntimeError(f"No .txt files found under: {docs_dir}")

    all_chunks = []
    for filename, text in docs:
        all_chunks.extend(
            chunk_text(
                text=text,
                source=filename,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        )

    texts = [c.text for c in all_chunks]
    print(f"[INFO] Loaded {len(docs)} docs -> {len(texts)} chunks")

    embedder = LocalEmbedder()
    vecs, embed_latency_ms = embedder.embed(texts)

    metadata: List[Dict[str, Any]] = []
    for i, c in enumerate(all_chunks):
        metadata.append({
            "row": i,
            "chunk_id": c.chunk_id,
            "source": c.source,
            "text": c.text,
        })

    save_index(index_dir=index_dir, embeddings=vecs, metadata=metadata)
    print(f"[INFO] Saved index: {vecs.shape[0]} chunks, dim={vecs.shape[1]}")
    print(f"[INFO] Embed latency: {embed_latency_ms} ms")

