from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TextChunk:
    chunk_id: str
    source: str
    text: str


def chunk_text(text: str, source: str, chunk_size: int, overlap: int) -> List[TextChunk]:
    text = (text or "").strip()
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be < chunk_size")

    chunks: List[TextChunk] = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(
                TextChunk(
                    chunk_id=f"{source}::chunk_{idx}",
                    source=source,
                    text=chunk,
                )
            )
            idx += 1
        if end == len(text):
            break
        start = end - overlap

    return chunks
