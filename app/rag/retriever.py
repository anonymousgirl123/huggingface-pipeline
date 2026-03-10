from __future__ import annotations

import os
from typing import Any, Dict, List

import numpy as np

from app.rag.embedder import LocalEmbedder
from app.rag.index_io import load_index


class LocalRetriever:
    def __init__(self) -> None:
        self.top_k = int(os.getenv("RESBOT_RETRIEVAL_TOP_K", "3"))
        self.index_dir = os.getenv("RESBOT_INDEX_DIR", "data/index")
        self.embedder = LocalEmbedder()
        self._embeddings: np.ndarray | None = None
        self._metadata: List[Dict[str, Any]] | None = None

    def _load(self) -> None:
        if self._embeddings is None:
            print(f"[INFO] Loading index from: {self.index_dir}")
            self._embeddings, self._metadata = load_index(self.index_dir)
            print(f"[INFO] Index loaded: {self._embeddings.shape[0]} chunks")

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        self._load()

        query_vec, _ = self.embedder.embed([query])
        # query_vec shape: (1, dim) — normalized, so dot product = cosine similarity
        scores = (self._embeddings @ query_vec.T).squeeze()

        # Handle edge case: single chunk in index
        if scores.ndim == 0:
            scores = scores.reshape(1)

        top_indices = np.argsort(scores)[::-1][: self.top_k]

        results = []
        for idx in top_indices:
            entry = dict(self._metadata[idx])
            entry["score"] = float(scores[idx])
            results.append(entry)

        return results
