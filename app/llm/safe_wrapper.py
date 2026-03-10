from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class SafeGenerationResult:
    """Outcome container returned by :func:`safe_generate`."""

    answer: str
    success: bool
    used_fallback: bool
    attempts: int
    error_type: Optional[str] = None
    error_message: Optional[str] = None


def safe_generate(
    *,
    generate_fn: Callable[..., str],
    # the remaining args mirror the parameters that callers expect to pass like
    # ``prompt``, ``temperature`` etc.  ``generate_fn`` is presumed to accept
    # keyword args for this data, so we forward ``**kwargs`` instead of
    # inspecting each one.
    **kwargs: Any,
) -> SafeGenerationResult:
    """Call ``generate_fn`` while catching exceptions and optionally retrying.

    This helper keeps the CLI from crashing when the model or a client throws
    a runtime error.  A simple second attempt is made and a structured result
    is returned describing what happened.

    The caller must always pass ``generate_fn`` as a keyword argument; the
    remainder of the parameters are opaque and forwarded verbatim.
    """

    attempts = 0
    used_fallback = False
    last_error: Optional[Exception] = None

    # try up to two times: the initial request and one fallback retry
    while attempts < 2:
        attempts += 1
        try:
            answer = generate_fn(**kwargs)
            return SafeGenerationResult(
                answer=answer,
                success=True,
                used_fallback=used_fallback,
                attempts=attempts,
            )
        except Exception as exc:  # pylint: disable=broad-except
            last_error = exc
            # mark that we are now using the fallback path and loop again
            used_fallback = True
            continue

    # if we reach here, both attempts failed
    return SafeGenerationResult(
        answer="",
        success=False,
        used_fallback=used_fallback,
        attempts=attempts,
        error_type=type(last_error).__name__ if last_error else None,
        error_message=str(last_error) if last_error else None,
    )
