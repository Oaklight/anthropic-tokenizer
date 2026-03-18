# anthropic-tokenizer

[![PyPI version](https://img.shields.io/pypi/v/anthropic-tokenizer?color=green)](https://pypi.org/project/anthropic-tokenizer/)
[![CI](https://github.com/Oaklight/anthropic-tokenizer/actions/workflows/CI.yml/badge.svg)](https://github.com/Oaklight/anthropic-tokenizer/actions/workflows/CI.yml)

快速、离线的 Claude 分词器，带 Python 绑定。Rust 编写，PyO3 桥接。

[English](README_en.md)

## 为什么需要这个？

Anthropic **没有**为 Python 发布本地分词器。现有的方案：

1. **官方 API** (`/v1/messages/count_tokens`) — 精确，但需要 API key
2. **字符数估算** (`len(text) / 4`) — 快，但误差巨大（1.5x–2x）

本项目填补了这个空白：一个**原生 BPE 分词器**，内嵌官方 Anthropic SDK 的词表，编译为 Python 模块。同时提供可选的 API 客户端，在有 API key 时调用官方端点获取精确计数。

## 特性

- **快速**：基于 HuggingFace `tokenizers` crate 的 Rust 原生 BPE
- **离线**：无需网络 — 词表内嵌于二进制文件中
- **API 回退**：可选使用官方 Anthropic `count_tokens` API 获取精确计数
- **优雅降级**：API key 无效 / 缺失 / 网络不通 → 自动回退到本地分词器
- **零 Python 依赖**：纯标准库 — API 客户端使用 `urllib`，无需 `httpx`/`requests`

## 安装

### 从源码构建（需要 Rust 工具链）

```bash
conda create -n anthropic_tokenizer python=3.10 -y
conda activate anthropic_tokenizer
conda install -c conda-forge rust maturin -y

git clone https://github.com/Oaklight/anthropic-tokenizer.git
cd anthropic-tokenizer
maturin develop
```

### 从 PyPI 安装（即将上线）

```bash
pip install anthropic-tokenizer
```

## 快速开始

### 本地分词器（无需 API key）

```python
import anthropic_tokenizer as at

at.count_tokens("Hello, world!")          # 5
at.encode("Hello, world!")                # [10002, 16, 2253, 64, 5]
at.decode([10002, 16, 2253, 64, 5])       # "Hello, world!"
at.encode_with_tokens("Hello")            # [(10002, "Hello")]
at.vocab_size()                           # 65000
```

### 带 API 回退（可选）

```python
from anthropic_tokenizer import ApiTokenizer

# 从环境变量读取 ANTHROPIC_API_KEY，或直接传入
tok = ApiTokenizer(api_key="sk-ant-...")

# 优先调用 API → 失败时回退到本地
tok.count_tokens("Hello, world!", model="claude-sonnet-4-20250514")
```

## API Key 配置

API 客户端按以下顺序查找 key：

1. 传给 `ApiTokenizer()` 的 `api_key` 参数
2. `ANTHROPIC_API_KEY` 环境变量

如果没有有效的 key，所有调用将静默回退到本地分词器。

官方 `/v1/messages/count_tokens` 端点是**免费的**（不计 token 费用，仅有 RPM 限制）。

## 精度对比

| 方式 | 速度 | 精度 | 需要 Key |
|------|------|------|---------|
| **本地分词器** | ~1ms / 16KB 文本 | 近似（旧词表，新模型可能有偏差） | 否 |
| **API count_tokens** | ~200ms（网络） | 精确 | 是 |
| `len(text) / 4` | 即时 | 差（1.5x–2x 误差） | 否 |

> **注意**：内嵌词表来自 `anthropic-sdk-python`（v0.39.0 之前）。Anthropic 已确认其*"对新模型不准确"*。生产环境的计费或上下文窗口计算建议使用 API。

## 许可证

MIT
