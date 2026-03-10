from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple

import numpy as np


def save_index(
    index_dir: str,
    embeddings: np.ndarray,
    metadata: List[Dict[str, Any]],
) -> None:
    os.makedirs(index_dir, exist_ok=True)
    np.save(os.path.join(index_dir, "embeddings.npy"), embeddings)
    with open(os.path.join(index_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def load_index(
    index_dir: str,
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    embeddings = np.load(os.path.join(index_dir, "embeddings.npy"))
    with open(os.path.join(index_dir, "metadata.json"), "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return embeddings, metadata
