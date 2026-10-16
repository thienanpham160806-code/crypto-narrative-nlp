"""Tách từ kiểu Loughran–McDonald. Port từ disclosure-tone-car/src/textkit/us_clean.py
(gốc m4a1ak471994/lm2011-replication, MIT). Đầu vào phải viết HOA (EnglishScorer tự upper())."""
import re

TOKEN_RE = re.compile(r"\b[A-Z][A-Z\-]+\b")


def tokenize(text: str) -> list[str]:
    """LM-style tokenization: alphabetic tokens (length ≥ 2), hyphens allowed."""
    return TOKEN_RE.findall(text)
