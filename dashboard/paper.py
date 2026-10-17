"""paper/paper.md → dashboard/web/public/data/paper.json (HTML) cho trang "Bài báo" của dashboard.

Chỉ chuyển nội dung do nhóm viết (không nhận Markdown ngoài). Chạy: python dashboard/paper.py
"""
from __future__ import annotations
import json, pathlib, re
import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]


LIST = re.compile(r"^\s*(?:[-*]|\d+\.)\s")


def render(md: str) -> str:
    """Python-Markdown cần dòng trống trước danh sách; chèn khi danh sách nối ngay sau một đoạn văn."""
    lines, out = md.splitlines(), []
    for i, line in enumerate(lines):
        prev = lines[i - 1] if i else ""
        if LIST.match(line) and prev.strip() and not LIST.match(prev) and not prev.startswith((" ", "|", ">")):
            out.append("")
        out.append(line)
    return markdown.markdown("\n".join(out), extensions=["tables", "sane_lists"], output_format="html")


def main():
    md = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    out = ROOT / "dashboard" / "web" / "public" / "data" / "paper.json"
    out.write_text(json.dumps(dict(html=render(md)), ensure_ascii=False), encoding="utf-8")
    print("ghi", out)


if __name__ == "__main__":
    main()
