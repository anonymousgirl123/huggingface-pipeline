import os
import re
import time

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.clients.base import LLMClient
from app.core.schemas import LLMRequest, LLMResponse
from app.utils.logger import get_logger

log = get_logger("HFLocalClient")


class HFLocalClient(LLMClient):
    """Local HuggingFace client for FLAN-T5 (CPU)."""

    def __init__(self):
        self.model_name = os.getenv("RESBOT_MODEL_NAME", "google/flan-t5-large")

        log.info(f"Loading model: {self.model_name}")
        t0 = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

        self.device = torch.device("cpu")
        self.model.to(self.device)
        self.model.eval()

        log.info(f"Model loaded in {time.time() - t0:.2f}s")

    def _get_message(self, req: LLMRequest, role: str) -> str:
        for m in req.messages:
            if m.role == role:
                return (m.content or "").strip()
        return ""

    def _build_prompt(self, req: LLMRequest, strong: bool = False) -> str:
        system_prompt = self._get_message(req, "system") or "You are a senior Site Reliability Engineer."
        user_question = self._get_message(req, "user")
        context = (req.context or "").strip()

        context_block = f"\nEnvironment Context:\n{context}\n" if context else ""

        # Key idea:
        # - DO NOT include solved examples close to the user's issue (causes copying)
        # - DO enforce format rules that stop single-line mega-steps

        rules = """
Rules (must follow):

- Start with exactly: Checklist:
- Provide exactly 6 steps, numbered 1) to 6)
- Each step MUST be on its own line
- Each step must include WHAT to check + WHERE to check (logs / metrics / traces / config)
- Each step must be <= 18 words
- Do NOT use hyphens "-" or semicolons ";" inside steps
- Do NOT ask questions
- Do NOT restate the issue
- Do NOT combine multiple checks in one step
"""

        if strong:
            rules += """
If you cannot think of 6 different steps, still output 6 distinct steps by changing the investigation layer
(gateway / upstream / app / db / network / config).
"""

        return f"""{system_prompt}

You are troubleshooting a production incident like an experienced SRE.

Investigation layers to cover (use different layers across steps):

- API gateway / load balancer
- upstream service (latency, errors)
- application (timeouts, pools, threads)
- database (slow queries, connections)
- network / DNS / TLS
- deploys / config changes

{rules}

{context_block}

Issue:

{user_question}

Checklist:

1)"""

    def _normalize(self, text: str) -> str:
        t = (text or "").strip()

        if not t.lower().startswith("checklist"):
            t = "Checklist:\n" + t

        # Normalize numbering variants into "1) ..."
        t = re.sub(r"\bStep\s*(\d+)\s*:\s*", r"\1) ", t, flags=re.IGNORECASE)
        t = re.sub(r"^\s*(\d+)\.\s*", r"\1) ", t, flags=re.MULTILINE)

        # If model jammed steps in one line, split before "2)" "3)" etc.
        t = re.sub(r"\s+(?=\d+\))", "\n", t)

        return t.strip()

    def _extract_steps(self, normalized_text: str):
        lines = [ln.strip() for ln in normalized_text.splitlines() if ln.strip()]
        steps = []

        for ln in lines:
            if re.match(r"^\d+\)\s+", ln):
                steps.append(ln)

        return steps

    def _postprocess(self, text: str) -> str:
        t = self._normalize(text)
        steps = self._extract_steps(t)

        # Cap to 6 steps (lab requirement for stable output)
        steps = steps[:6]

        if len(steps) >= 5:
            return "\n".join(["Checklist:"] + steps)

        # If output is weak (1-4 steps), return normalized raw for debugging/visibility
        return t

    def _generate_once(self, prompt: str, req: LLMRequest, strong: bool = False) -> str:
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        do_sample = os.getenv("RESBOT_DO_SAMPLE", "0") == "1"
        temperature = float(req.temperature or 0.0)
        top_p = float(req.top_p or 1.0)

        # Deterministic by default (fast + repeatable for labs)
        # We slightly increase beams on retry to help the model complete the list.
        num_beams = 2 if not strong else 4

        with torch.no_grad():
            if do_sample:
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=int(req.max_new_tokens),
                    do_sample=True,
                    temperature=max(0.1, temperature),
                    top_p=top_p,
                    num_beams=1,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.1,
                )
            else:
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=int(req.max_new_tokens),
                    # On retry, force a bit more output so it doesn't stop after 1 line
                    min_new_tokens=80 if strong else 0,
                    do_sample=False,
                    num_beams=num_beams,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.1,
                    length_penalty=1.05,
                )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate(self, req: LLMRequest) -> LLMResponse:
        try:
            t0 = time.time()

            prompt = self._build_prompt(req, strong=False)
            raw = self._generate_once(prompt, req, strong=False)
            text = self._postprocess(raw)

            # Retry once if we got fewer than 5 steps
            steps = self._extract_steps(self._normalize(text))

            if len(steps) < 5:
                prompt2 = self._build_prompt(req, strong=True)
                raw2 = self._generate_once(prompt2, req, strong=True)
                text2 = self._postprocess(raw2)

                steps2 = self._extract_steps(self._normalize(text2))

                if len(steps2) >= len(steps):
                    text = text2

            latency = int((time.time() - t0) * 1000)

            return LLMResponse(
                text=text,
                model_name=self.model_name,
                usage={"latency_ms": latency},
                metadata=req.metadata
            )

        except Exception as e:
            log.exception("Generation failed")

            return LLMResponse(
                text="",
                model_name=self.model_name,
                error=str(e),
                metadata=req.metadata
            )

