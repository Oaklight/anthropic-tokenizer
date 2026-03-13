"""
API client for Anthropic's /v1/messages/count_tokens endpoint.
Falls back to local BPE tokenizer on any failure.

Uses only Python stdlib (urllib) — no external dependencies.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

from anthropic_tokenizer.anthropic_tokenizer import count_tokens as _local_count  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.anthropic.com"
_DEFAULT_MODEL = "claude-sonnet-4-20250514"


class ApiTokenizer:
    """Token counter that tries the official Anthropic API first,
    falling back to the local BPE tokenizer on any failure."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 10.0,
    ):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._base_url = (base_url or os.environ.get("ANTHROPIC_BASE_URL", _DEFAULT_BASE_URL)).rstrip("/")
        self._model = model or _DEFAULT_MODEL
        self._timeout = timeout

        if not self._api_key:
            logger.info("No ANTHROPIC_API_KEY found. All calls will use local tokenizer.")

    def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> int:
        """Count tokens. Tries API first, falls back to local tokenizer.

        Args:
            text: The text to count tokens for.
            model: Model name for API call. Defaults to claude-sonnet-4-20250514.

        Returns:
            Token count (int).
        """
        if self._api_key:
            try:
                return self._count_via_api(text, model)
            except Exception as e:
                logger.debug("API count_tokens failed (%s), falling back to local tokenizer", e)

        return _local_count(text)

    def count_tokens_local(self, text: str) -> int:
        """Always use the local BPE tokenizer."""
        return _local_count(text)

    def _count_via_api(self, text: str, model: str | None = None) -> int:
        url = f"{self._base_url}/v1/messages/count_tokens"
        headers: dict[str, str] = {
            "x-api-key": self._api_key or "",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        payload = json.dumps(
            {
                "model": model or self._model,
                "messages": [{"role": "user", "content": text}],
            }
        ).encode()

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            data = json.loads(resp.read())
        return data["input_tokens"]
