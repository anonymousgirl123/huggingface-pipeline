from __future__ import annotations

import re
from typing import Optional

from app.core.schemas import BotResponse


def _clean_answer(text: str) -> str:
    text = text.strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    items: list[str] = []
    seen: set[str] = set()

    for line in lines:
        match = re.match(r"^(?:\d+[\.\)]\s*|-+\s*)(.+)$", line)
        if match:
            candidate = match.group(1).strip()
        else:
            candidate = line.strip()

        lowered = candidate.lower().rstrip(":")
        if not candidate:
            continue
        if lowered.startswith(("answer", "question", "checklist",
                               "bullet point", "here are", "context",
                               "relevant", "based on")):
            continue
        if lowered in seen:
            continue

        seen.add(lowered)
        items.append(candidate[0].upper() + candidate[1:] if candidate else candidate)

    if len(items) < 3:
        chunks = re.split(r"\s(?=\d+[\.\)])", text)
        reparsed: list[str] = []
        seen = set()
        for chunk in chunks:
            match = re.match(r"^\d+[\.\)]\s*(.+)$", chunk.strip())
            if match:
                candidate = match.group(1).strip()
                lowered = candidate.lower().rstrip(":")
                if candidate and lowered not in seen:
                    seen.add(lowered)
                    reparsed.append(
                        candidate[0].upper() + candidate[1:] if candidate else candidate
                    )
        if len(reparsed) >= 3:
            items = reparsed

    items = items[:5]
    return "\n".join(f"- {item}" for item in items)


class ResilienceBot:
    def __init__(self, client, retriever=None) -> None:
        self.client = client
        self.retriever = retriever

    def ask(self, question: str) -> BotResponse:
        # ── Retrieval ──────────────────────────────────────────────
        context_block = ""
        if self.retriever is not None:
            results = self.retriever.retrieve(question)
            if results:
                chunks = "\n---\n".join(r["text"] for r in results)
                context_block = (
                    "Relevant context from internal knowledge base:\n"
                    + chunks
                    + "\n\n"
                )

        # ── Prompt ────────────────────────────────────────────────
        prompt = (
            "Task: Write a troubleshooting checklist for a reliability engineering question.\n"
            "Return exactly 5 short numbered items.\n"
            "Each item must be practical and action-oriented.\n"
            "Focus on API failures, 504 timeouts, retries, retry storms, outages, "
            "upstream dependencies, recent deployments, configuration changes, "
            "logs, metrics, and traces.\n"
            "Do not write headings. Do not write explanations. Do not write paragraphs.\n\n"
            + context_block
            + "Example:\n"
            "Question: Our service latency increased after a deployment. What should I check?\n"
            "Checklist:\n"
            "1. Check recent deployments and configuration changes.\n"
            "2. Review service and dependency latency metrics.\n"
            "3. Inspect logs for new errors or timeout spikes.\n"
            "4. Verify retry and timeout settings between services.\n"
            "5. Use traces to identify the slowest downstream component.\n\n"
            f"Question: {question}\n"
            "Checklist:\n"
        )

        answer = self.client.generate(
            prompt=prompt,
            temperature=0.2,
            max_new_tokens=180,
            top_p=0.9,
        )

        cleaned = _clean_answer(answer)
        final_text = cleaned if cleaned.strip() else answer.strip()

        return BotResponse(text=final_text)
