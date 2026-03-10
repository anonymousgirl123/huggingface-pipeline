from __future__ import annotations

import os
import time
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    """CPU-only embedder using all-MiniLM-L6-v2."""

    def __init__(self) -> None:
        self.model_name = os.getenv(
            "RESBOT_EMBED_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        print(f"[INFO] Loading embed model: {self.model_name}")
        t0 = time.perf_counter()
        self.model = SentenceTransformer(self.model_name, device="cpu")
        load_ms = int((time.perf_counter() - t0) * 1000)
        print(f"[INFO] Embed model loaded in {load_ms} ms")

    def embed(self, texts: List[str]) -> Tuple[np.ndarray, int]:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32), 0
        t0 = time.perf_counter()
        vecs = self.model.encode(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return vecs, latency_ms
