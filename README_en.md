# anthropic-tokenizer

A fast, offline Claude tokenizer with Python bindings. Built in Rust with PyO3.

[中文文档](README_zh.md)

## Why?

Anthropic does **not** publish a local tokenizer for Python. The only options are:

1. **Official API** (`/v1/messages/count_tokens`) — accurate but requires an API key
2. **Character-based estimation** (`len(text) / 4`) — fast but wildly inaccurate (1.5x–2x error)

This package fills the gap: a **native BPE tokenizer** embedded from the official Anthropic SDK vocabulary, exposed as a Python module compiled from Rust. It also provides an optional API client that calls the official endpoint when an API key is available.

## Features

- **Fast**: Rust-native BPE tokenizer via HuggingFace `tokenizers` crate
- **Offline**: No network required — tokenizer vocabulary is embedded in the binary
- **API fallback**: Optionally use the official Anthropic `count_tokens` API for exact counts
- **Graceful degradation**: API key invalid / missing / network down → automatic fallback to local tokenizer
- **Zero Python dependencies**: Pure stdlib — the API client uses `urllib`, no `httpx`/`requests` needed

## Installation

### From source (requires Rust toolchain)

```bash
conda create -n anthropic_tokenizer python=3.10 -y
conda activate anthropic_tokenizer
conda install -c conda-forge rust maturin -y

git clone https://github.com/Oaklight/anthropic-tokenizer.git
cd anthropic-tokenizer
maturin develop
```

### From PyPI (coming soon)

```bash
pip install anthropic-tokenizer
```

## Quick Start

### Local tokenizer (no API key needed)

```python
import anthropic_tokenizer as at

at.count_tokens("Hello, world!")          # 5
at.encode("Hello, world!")                # [10002, 16, 2253, 64, 5]
at.decode([10002, 16, 2253, 64, 5])       # "Hello, world!"
at.encode_with_tokens("Hello")            # [(10002, "Hello")]
at.vocab_size()                           # 65000
```

### With API fallback (optional)

```python
from anthropic_tokenizer import ApiTokenizer

# Reads ANTHROPIC_API_KEY from env, or pass explicitly
tok = ApiTokenizer(api_key="sk-ant-...")

# Tries API first → falls back to local on failure
tok.count_tokens("Hello, world!", model="claude-sonnet-4-20250514")
```

## API Key Configuration

The API client looks for a key in this order:

1. `api_key` parameter passed to `ApiTokenizer()`
2. `ANTHROPIC_API_KEY` environment variable

If no valid key is found, all calls silently fall back to the local tokenizer.

The official `/v1/messages/count_tokens` endpoint is **free** (no token cost, rate-limited only).

## Accuracy

| Method | Speed | Accuracy | Requires Key |
|--------|-------|----------|-------------|
| **Local tokenizer** | ~1ms / 16KB text | Approximate (old vocabulary, may drift on newer models) | No |
| **API count_tokens** | ~200ms (network) | Exact | Yes |
| `len(text) / 4` | instant | Poor (1.5x–2x error) | No |

> **Note**: The embedded vocabulary originates from `anthropic-sdk-python` (pre-v0.39.0). Anthropic confirmed it is *"not accurate for newer models"*. For production billing or context-window calculations, prefer the API.

## License

MIT
