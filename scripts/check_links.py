"""Kiểm link trong README và tài liệu Markdown: đường dẫn tương đối phải tồn tại, URL ngoài (badge, web) trả HTTP < 400.

Chạy: python scripts/check_links.py README.md docs/WORKFLOW.md [--offline]
"""
from __future__ import annotations
import re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)\s]+)\)")


def anchors(text: str) -> set[str]:
    """Anchor kiểu GitHub: chữ thường, bỏ dấu câu, khoảng trắng → '-'."""
    return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-") for h in re.findall(r"^#+ (.+)$", text, re.M)}


def check(md: Path, online: bool) -> list[str]:
    text = md.read_text(encoding="utf-8")
    bad = []
    for target in LINK.findall(text):
        if target.startswith("#"):
            if target[1:] not in anchors(text):
                bad.append(f"{md.name}: anchor {target}")
        elif target.startswith("http"):
            if online:
                try:
                    req = urllib.request.Request(target, headers={"User-Agent": "crypto-narrative-nlp link-check research@example.org"})  # SEC chặn UA thiếu email
                    with urllib.request.urlopen(req, timeout=20) as r:
                        if r.status >= 400:
                            bad.append(f"{md.name}: {r.status} {target}")
                except Exception as e:  # mạng lỗi cũng báo, để người chạy xem lại
                    bad.append(f"{md.name}: {e} {target}")
        elif not (md.parent / target.split("#")[0]).exists():
            bad.append(f"{md.name}: thiếu {target}")
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")] or ["README.md"]
    errors = [e for f in args for e in check(ROOT / f, "--offline" not in sys.argv)]
    print("\n".join(errors) or "Mọi link đều tốt")
    sys.exit(1 if errors else 0)
