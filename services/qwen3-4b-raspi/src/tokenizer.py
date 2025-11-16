"""Simple tokenizer wrapper.

This wraps a HF tokenizer if available, otherwise falls back to a trivial whitespace tokenizer
useful for local development and tests.
"""
from __future__ import annotations
from typing import List

try:
    from transformers import AutoTokenizer
except Exception:
    AutoTokenizer = None


class Tokenizer:
    def __init__(self, model_path: str | None = None):
        self._hf = None
        if AutoTokenizer is not None and model_path:
            try:
                self._hf = AutoTokenizer.from_pretrained(model_path)
            except Exception:
                # degrade to simple tokenizer
                self._hf = None

    def encode(self, text: str) -> List[int]:
        if self._hf:
            return self._hf.encode(text)
        # simple whitespace-tokenizer
        return [len(tok) for tok in text.split()]

    def decode(self, token_ids: List[int]) -> str:
        if self._hf:
            return self._hf.decode(token_ids, skip_special_tokens=True)
        # naive decode
        # represent token ids as <tokN> placeholders for development
        return " ".join(f"<tok{t}>" for t in token_ids)


def load_tokenizer(path: str | None = None) -> Tokenizer:
    return Tokenizer(model_path=path)
