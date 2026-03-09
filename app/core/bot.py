from __future__ import annotations

import os

from app.clients.base import LLMClient
from app.core.schemas import ChatMessage, LLMRequest, LLMResponse


DEFAULT_SYSTEM = """You are ResilienceBot, an SRE troubleshooting assistant.

Rules:

- Always respond with a numbered checklist.
- Provide at least 6 concrete steps.
- Each step must be actionable (what to check + where to look).
- If you make assumptions, list them under a final section called "Assumptions".
- Do not give vague advice.

Output format:

Checklist:

1) ...
2) ...
...

Assumptions:

- ...
"""


class ResilienceBot:
    def __init__(self, client: LLMClient):
        self.client = client

    def ask(self, user_question: str) -> LLMResponse:
        system_prompt = os.getenv("RESBOT_SYSTEM_PROMPT", DEFAULT_SYSTEM).strip()
        dynamic_context = os.getenv("RESBOT_CONTEXT", "").strip()

        req = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_question),
            ],
            context=dynamic_context,
            max_new_tokens=int(os.getenv("RESBOT_MAX_NEW_TOKENS", "256")),
            temperature=float(os.getenv("RESBOT_TEMPERATURE", "0.0")),
            top_p=float(os.getenv("RESBOT_TOP_P", "1.0")),
            metadata={"component": "ResilienceBot"},
        )

        return self.client.generate(req)
    