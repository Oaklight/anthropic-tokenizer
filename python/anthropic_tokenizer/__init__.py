"""
anthropic_tokenizer - Fast Claude tokenizer with API fallback.

Core functions (Rust-native, always available):
    count_tokens(text) -> int
    encode(text) -> list[int]
    decode(ids) -> str
    encode_with_tokens(text) -> list[tuple[int, str]]
    vocab_size() -> int

API fallback class:
    ApiTokenizer(api_key=None, base_url=None) - tries official API first, falls back to local.
"""

from anthropic_tokenizer._api import ApiTokenizer
from anthropic_tokenizer.anthropic_tokenizer import (  # type: ignore[import-untyped]
    count_tokens,
    decode,
    encode,
    encode_with_tokens,
    vocab_size,
)

__all__ = [
    "count_tokens",
    "encode",
    "decode",
    "encode_with_tokens",
    "vocab_size",
    "ApiTokenizer",
]
