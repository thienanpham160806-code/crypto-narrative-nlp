"""paper/paper.md → dashboard/web/public/data/paper.json (HTML) cho trang "Bài báo" của dashboard.

Điền số liệu bằng paper/fill_results.py rồi chuyển Markdown → HTML; phương trình giữ nguyên LaTeX trong
<div class="eq"> để KaTeX vẽ ở trình duyệt. Chỉ chuyển nội dung do nhóm viết. Chạy: python dashboard/paper.py
"""
from __future__ import annotations
import html, json, pathlib, re, sys
import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
import fill_results  # noqa: E402

SUB = re.compile(r"(?<=[\w\u0300-\u036f])_(\{[^}]*\}|[A-Za-z0-9](?!\w))")
FIG = "../outputs/figures/real/"


def split_front(text: str) -> tuple[dict, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm = {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in m.group(1).split("\n"))}
    return fm, text[m.end():]


def render(filled: str) -> str:
    fm, body = split_front(filled)
    math: list[str] = []

    def keep(m: re.Match) -> str:
        math.append(m.group(1).strip())
        return f"\n\nMATHSLOT{len(math) - 1}END\n\n"

    body = re.sub(r"^\$\$(.+?)\$\$\s*$", keep, body, flags=re.M | re.S)
    refs_at = body.index("## Tài liệu tham khảo")
    prose, refs = body[:refs_at], body[refs_at:]
    prose = "\n".join(ln if ln.startswith(("|", "![", "[^")) else SUB.sub(lambda m: f"<sub>{m.group(1).strip('{}')}</sub>", ln)
                      for ln in prose.split("\n"))
    out = markdown.markdown(prose + "\n" + refs, extensions=["tables", "sane_lists", "footnotes"], output_format="html")
    for i, tex in enumerate(math):
        number = re.search(r"\\tag\{(\d+)\}", tex).group(1)
        tex = re.sub(r"\\tag\{\d+\}", "", tex).strip()
        out = out.replace(f"<p>MATHSLOT{i}END</p>",
                          f'<div class="eq"><span class="eq-tex" data-tex="{html.escape(tex, quote=True)}"></span>'
                          f'<span class="eq-no">({number})</span></div>')
    out = out.replace(f'src="{FIG}', 'src="/outputs/figures/real/')
    head = (f'<h1>{html.escape(fm["title_vi"])}</h1><p class="subtitle">{html.escape(fm["title_en"])}</p>'
            f'<p class="kw"><b>JEL:</b> {html.escape(fm["jel"])} · <b>Từ khóa:</b> {html.escape(fm["keywords_vi"])} · '
            f'<b>Keywords:</b> {html.escape(fm["keywords_en"])}</p>')
    return head + out


def main():
    template = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    filled, _ = fill_results.render(template, fill_results.parse_bib(fill_results.BIB))
    out = ROOT / "dashboard" / "web" / "public" / "data" / "paper.json"
    out.write_text(json.dumps(dict(html=render(filled)), ensure_ascii=False), encoding="utf-8")
    print("ghi", out)


if __name__ == "__main__":
    main()
