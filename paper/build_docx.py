"""Xuất paper/paper.docx từ khuôn paper/paper.md (điền số liệu bằng fill_results trước).

Times New Roman 13, giãn dòng 1.15, thụt đầu dòng 1.27 cm, spacing 0, số trang giữa header,
bảng APA (chỉ đường kẻ ngang), phương trình là Word Equation (OMML), chú thích chân trang thật.
Chạy từ gốc repo: python paper/build_docx.py
"""
from __future__ import annotations

import argparse
import re
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.opc.part import Part
from docx.oxml import OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt
from lxml import etree

try:
    from paper import fill_results
except ImportError:  # chạy trực tiếp: python paper/build_docx.py
    import fill_results

ROOT = Path(__file__).resolve().parents[1]
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
FONT = "Times New Roman"
TEXT_W = 16.0  # cm: A4 trừ lề 2.5 hai bên


# ------------------------------------------------------------------ LaTeX -> OMML (pandoc)
def omml(latex: list[str]) -> list[etree._Element]:
    """Mỗi chuỗi LaTeX → một m:oMath gốc của Word, do pandoc dựng (một lần gọi cho cả bài)."""
    import pypandoc
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "eq.docx"
        pypandoc.convert_text("\n\n".join(f"$${t}$$" for t in latex), "docx", format="markdown",
                              outputfile=str(out))
        with zipfile.ZipFile(out) as z:
            root = etree.fromstring(z.read("word/document.xml"))
    maths = [m for m in root.iter(f"{{{M_NS}}}oMath")]
    if len(maths) != len(latex):
        raise ValueError(f"pandoc trả {len(maths)} phương trình, cần {len(latex)}")
    return maths


# ------------------------------------------------------------------ Word
SUB = re.compile(r"(?<=[\w\u0300-\u036f])_(\{[^}]*\}|[A-Za-z0-9](?!\w))")
TOKEN = re.compile(r"\[\^(\w+)\]|\*\*(.+?)\*\*|\*(.+?)\*")
ALIGN = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER, "r": WD_ALIGN_PARAGRAPH.RIGHT}


def set_fonts(rpr) -> None:
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{a}"), FONT)


def style_document(doc) -> None:
    s = doc.sections[0]
    s.page_width, s.page_height, s.orientation = Cm(21), Cm(29.7), WD_ORIENT.PORTRAIT
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.5)
    s.header_distance = Cm(1.25)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(13)
    rpr = normal.element.get_or_add_rPr()
    set_fonts(rpr)
    lang = OxmlElement("w:lang")
    lang.set(qn("w:val"), "vi-VN")
    lang.set(qn("w:eastAsia"), "vi-VN")
    rpr.append(lang)
    pf = normal.paragraph_format
    pf.space_before = pf.space_after = Pt(0)
    pf.line_spacing = 1.15
    pf.first_line_indent = Cm(1.27)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.widow_control = True
    h = doc.styles["Heading 1"]
    h.font.name, h.font.size, h.font.bold, h.font.italic = FONT, Pt(13), True, False
    h.font.color.rgb = None
    set_fonts(h.element.get_or_add_rPr())
    hp = h.paragraph_format
    hp.first_line_indent, hp.alignment, hp.keep_with_next = Cm(0), WD_ALIGN_PARAGRAPH.LEFT, True
    hp.space_before = hp.space_after = Pt(0)
    p = s.header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    for kind, text in (("begin", None), (None, " PAGE "), ("end", None)):
        r = p.add_run()
        r.font.size = Pt(11)
        if kind:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), kind)
        else:
            f = OxmlElement("w:instrText")
            f.set(XML_SPACE, "preserve")
            f.text = text
        r._r.append(f)


class Writer:
    def __init__(self, doc, notes: dict[str, str]):
        self.doc, self.notes, self.order = doc, notes, []

    def run(self, p, text, size=None, bold=False, italic=False, sup=False, sub=False):
        r = p.add_run(text)
        set_fonts(r._r.get_or_add_rPr())
        r.bold, r.italic = bold or None, italic or None
        r.font.size = Pt(size) if size else None
        r.font.superscript, r.font.subscript = sup or None, sub or None
        return r

    def plain(self, p, text, size=None, bold=False, italic=False, subscripts=True):
        pos = 0
        for m in SUB.finditer(text) if subscripts else ():
            self.run(p, text[pos:m.start()], size, bold, italic)
            self.run(p, m.group(1).strip("{}"), size, bold, italic, sub=True)
            pos = m.end()
        self.run(p, text[pos:], size, bold, italic)

    def inline(self, p, text, size=None, subscripts=True):
        pos = 0
        for m in TOKEN.finditer(text):
            self.plain(p, text[pos:m.start()], size, subscripts=subscripts)
            if m.group(1):
                self.footnote_ref(p, m.group(1))
            else:
                self.plain(p, m.group(2) or m.group(3), size, bold=bool(m.group(2)),
                           italic=bool(m.group(3)), subscripts=subscripts)
            pos = m.end()
        self.plain(p, text[pos:], size, subscripts=subscripts)

    def footnote_ref(self, p, key):
        if key not in self.order:
            self.order.append(key)
        r = p.add_run()
        r.font.superscript = True
        ref = OxmlElement("w:footnoteReference")
        ref.set(qn("w:id"), str(self.order.index(key) + 1))
        r._r.append(ref)

    def para(self, text, *, hanging=False, subscripts=True):
        p = self.doc.add_paragraph()
        if hanging:
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent = Cm(1.27), Cm(-1.27)
            pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self.inline(p, text, subscripts=subscripts)

    def flat(self, align=WD_ALIGN_PARAGRAPH.LEFT, after=0, keep=False, spacing=None, before=0):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.first_line_indent, pf.alignment, pf.space_after = Cm(0), align, Pt(after)
        pf.space_before = Pt(before)
        pf.keep_with_next = keep or None
        if spacing:
            pf.line_spacing = spacing
        return p

    def equation(self, source, math):
        """Bảng 3 cột không viền: trống | phương trình căn giữa | (n) căn phải."""
        number = re.search(r"\\tag\{(\d+)\}", source).group(1)
        t = self.doc.add_table(rows=1, cols=3)
        t.autofit = False
        for col, cell, width, align in zip(t.columns, t.rows[0].cells, (1.4, TEXT_W - 2.8, 1.4),
                                           (WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT)):
            col.width = cell.width = Cm(width)  # gridCol cho LibreOffice, tcW cho Word
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            pf = cell.paragraphs[0].paragraph_format
            pf.first_line_indent, pf.alignment, pf.line_spacing = Cm(0), align, 1.0
            pf.space_before = pf.space_after = Pt(3)
        t.cell(0, 1).paragraphs[0]._p.append(math)
        self.run(t.cell(0, 2).paragraphs[0], f"({number})")

    def note(self, text):
        p = self.flat(WD_ALIGN_PARAGRAPH.JUSTIFY, after=8)
        self.run(p, "Ghi chú.", 11, italic=True)
        self.run(p, text[len("*Ghi chú.*"):], 11)

    def caption(self, label, title):
        center = WD_ALIGN_PARAGRAPH.CENTER
        self.run(self.flat(center, keep=True, before=8), label, bold=True)
        self.run(self.flat(center, keep=True), title, italic=True)

    def image(self, alt, path):
        """Ảnh căn giữa, rộng tối đa 15 cm giữ tỉ lệ, dính với dòng nguồn bên dưới."""
        p = self.flat(WD_ALIGN_PARAGRAPH.CENTER, keep=True)
        p.paragraph_format.line_spacing = 1.0
        p.add_run().add_picture(str((ROOT / "paper" / path).resolve()), width=Cm(15))
        for d in p._p.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"):
            d.set("descr", alt)
        self.run(self.flat(WD_ALIGN_PARAGRAPH.CENTER, after=4), "Nguồn: Tính toán của nhóm tác giả", 11, italic=True)

    def table(self, lines):
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
        align = ["r" if c.endswith(":") and not c.startswith(":") else "c" if c.startswith(":") else "l"
                 for c in rows[1]]
        rows = [rows[0]] + rows[2:]
        n = len(rows[0])
        size = 11 if n <= 6 else 9.5
        head = [max(len(x) for x in r.split()) for r in rows[0]]
        weight = [max(min(max(len(r[j]) for r in rows[1:]), 40), head[j]) + 5 for j in range(n)]
        widths = [TEXT_W * x / sum(weight) for x in weight]
        t = self.doc.add_table(rows=len(rows), cols=n)
        t.autofit = False
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(layout)
        margins = OxmlElement("w:tblCellMar")
        for side, w in (("top", "30"), ("left", "60"), ("bottom", "30"), ("right", "60")):
            m = OxmlElement(f"w:{side}")
            m.set(qn("w:w"), w)
            m.set(qn("w:type"), "dxa")
            margins.append(m)
        t._tbl.tblPr.append(margins)
        last = len(rows) - 1
        for i, row in enumerate(rows):
            trpr = t.rows[i]._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:cantSplit"))
            if i == 0:
                trpr.append(OxmlElement("w:tblHeader"))
            for j, text in enumerate(row):
                cell = t.cell(i, j)
                cell.width = Cm(widths[j])
                self.borders(cell, top=i == 0, bottom=i in (0, last))
                p = cell.paragraphs[0]
                pf = p.paragraph_format
                pf.first_line_indent, pf.line_spacing = Cm(0), 1.0
                pf.keep_with_next = i == 0 or None  # bảng dài được ngắt trang, dòng tiêu đề lặp lại
                pf.alignment = ALIGN["c" if i == 0 and j else align[j]]
                panel = re.fullmatch(r"\*\*(.+)\*\*", text)
                stars = None if panel else re.search(r"\*+$", text)
                self.plain(p, panel.group(1) if panel else text[:stars.start()] if stars else text, size,
                           bold=i == 0 or bool(panel))
                if stars:
                    self.run(p, stars.group(0), size, sup=True)
        for j, w in enumerate(widths):
            t.columns[j].width = Cm(w)

    @staticmethod
    def borders(cell, top, bottom):
        b = OxmlElement("w:tcBorders")
        for side, on, sz in (("top", top, "8"), ("bottom", bottom, "4" if top else "8")):
            if on:
                e = OxmlElement(f"w:{side}")
                for k, v in (("val", "single"), ("sz", sz), ("color", "000000")):
                    e.set(qn(f"w:{k}"), v)
                b.append(e)
        cell._tc.get_or_add_tcPr().append(b)

    def title_block(self, fm):
        email = fm["email"] or "[email tác giả liên hệ]"
        for text, size, bold, italic, after in (
                (fm["title_vi"], 15, True, False, 6), (fm["title_en"], 14, True, False, 8),
                (fm["author"], 13, True, False, 4), (fm["affiliation"], 11, False, True, 2),
                (f"Tác giả liên hệ, Email: {email}", 11, False, True, 10)):
            self.run(self.flat(WD_ALIGN_PARAGRAPH.CENTER, after), text, size, bold=bold, italic=italic)

    def frame(self, fm, abstracts):
        t = self.doc.add_table(rows=1, cols=2)
        t.autofit = False
        left, right = t.cell(0, 0), t.cell(0, 1)
        t.columns[0].width = left.width = Cm(4.6)
        t.columns[1].width = right.width = Cm(TEXT_W - 4.6)
        pairs = [("THÔNG TIN", ""), ("DOI:", fm["doi"]), ("Ngày nhận:", fm["received"]),
                 ("Ngày nhận lại:", fm["revised"]), ("Duyệt đăng:", fm["accepted"]),
                 ("Mã phân loại JEL:", fm["jel"]), ("Từ khóa:", fm["keywords_vi"]),
                 ("Keywords:", fm["keywords_en"])]

        def cell_par(cell, first, align=WD_ALIGN_PARAGRAPH.LEFT):
            p = cell.paragraphs[0] if first else cell.add_paragraph()
            pf = p.paragraph_format
            pf.first_line_indent, pf.line_spacing, pf.space_after, pf.alignment = Cm(0), 1.0, Pt(4), align
            return p

        first = True
        for label, value in pairs:
            p = cell_par(left, first)
            first = False
            self.run(p, label, 11, bold=not value and label == "THÔNG TIN")
            if value and len(label) + len(value) < 24:
                self.run(p, " " + value, 11)
            elif value:
                self.run(cell_par(left, False), value, 11)
        first = True
        for head, body in abstracts:
            self.run(cell_par(right, first), head, 11, bold=True)
            first = False
            self.inline(cell_par(right, False, WD_ALIGN_PARAGRAPH.JUSTIFY), body, 11)
        self.flat()


def footnotes_part(package, notes: dict[str, str], order: list[str]) -> Part:
    root = etree.fromstring(f'<w:footnotes {nsdecls("w")}/>'.encode())
    sub = etree.SubElement

    def add(fid: int, kind: str | None = None) -> etree._Element:
        fn = sub(root, qn("w:footnote"))
        fn.set(qn("w:id"), str(fid))
        if kind:
            fn.set(qn("w:type"), kind)
        p = sub(fn, qn("w:p"))
        ppr = sub(p, qn("w:pPr"))
        sp = sub(ppr, qn("w:spacing"))
        for k, v in (("before", "0"), ("after", "0"), ("line", "240"), ("lineRule", "auto")):
            sp.set(qn(f"w:{k}"), v)
        sub(ppr, qn("w:ind")).set(qn("w:firstLine"), "0")
        sub(ppr, qn("w:jc")).set(qn("w:val"), "both")
        return p

    def run(p, text=None, tag=None, vert=None):
        r = sub(p, qn("w:r"))
        rpr = sub(r, qn("w:rPr"))
        fonts = sub(rpr, qn("w:rFonts"))
        for a in ("ascii", "hAnsi", "eastAsia", "cs"):
            fonts.set(qn(f"w:{a}"), FONT)
        sub(rpr, qn("w:sz")).set(qn("w:val"), "20")
        if vert:
            sub(rpr, qn("w:vertAlign")).set(qn("w:val"), vert)
        if tag:
            sub(r, qn(tag))
        if text:
            t = sub(r, qn("w:t"))
            t.text = text
            t.set(XML_SPACE, "preserve")

    sub(add(-1, "separator"), qn("w:r")).append(etree.Element(qn("w:separator")))
    sub(add(0, "continuationSeparator"), qn("w:r")).append(etree.Element(qn("w:continuationSeparator")))
    for i, key in enumerate(order, 1):
        p = add(i)
        run(p, tag="w:footnoteRef", vert="superscript")
        text, pos = " " + notes[key], 0
        for m in SUB.finditer(text):
            run(p, text[pos:m.start()])
            run(p, m.group(1).strip("{}"), vert="subscript")
            pos = m.end()
        run(p, text[pos:])
    blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    return Part(PackURI("/word/footnotes.xml"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml", blob, package)


def parse_front(text: str) -> tuple[dict, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm = {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in m.group(1).split("\n"))}
    return fm, text[m.end():]


def build(filled: str, output: Path) -> None:
    fm, body = parse_front(filled)
    notes = dict(re.findall(r"^\[\^(\w+)\]: (.*)$", body, re.M))
    body = re.sub(r"^\[\^\w+\]: .*$", "", body, flags=re.M)
    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", body) if b.strip()]
    doc = Document()
    style_document(doc)
    w = Writer(doc, notes)
    maths = iter(omml([re.sub(r"\\tag\{\d+\}", "", b.strip("$")).strip() for b in blocks if b.startswith("$$")]))
    heads = [i for i, b in enumerate(blocks) if b.startswith("## ")]
    w.title_block(fm)
    w.frame(fm, [(blocks[i][3:], blocks[i + 1]) for i in heads[:2]])
    in_refs, i = False, heads[2]
    while i < len(blocks):
        b = blocks[i]
        if b.startswith("## "):
            in_refs = b == "## Tài liệu tham khảo"
            doc.add_paragraph(b[3:], style="Heading 1")
        elif b.startswith("$$"):
            w.equation(b, next(maths))
        elif b.startswith("|"):
            w.table(b.split("\n"))
        elif re.fullmatch(r"\*\*(Bảng|Hình) \d+\*\*", b):
            w.caption(b.strip("*"), blocks[i + 1].strip("*"))
            i += 1
        elif b.startswith("!["):
            w.image(*re.match(r"!\[(.*?)\]\((.*?)\)", b).groups())
        elif b.startswith("*Ghi chú.*"):
            w.note(b)
        else:
            w.para(b.replace("\n", " "), hanging=in_refs, subscripts=not in_refs)
        i += 1
    doc.part.relate_to(footnotes_part(doc.part.package, notes, w.order), RT.FOOTNOTES)
    cp = doc.core_properties
    cp.title, cp.author, cp.language = fm["title_vi"], fm["author"], "vi-VN"
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def package(source: Path, output: Path) -> None:
    """Điền số liệu vào khuôn `source` rồi xuất Word."""
    filled, _ = fill_results.render(Path(source).read_text(encoding="utf-8"),
                                    fill_results.parse_bib(fill_results.BIB))
    build(filled, Path(output))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=ROOT / "paper" / "paper.md")
    ap.add_argument("--output", type=Path, default=ROOT / "paper" / "paper.docx")
    a = ap.parse_args()
    package(a.source, a.output)
    print(f"Đã ghi {a.output}")


if __name__ == "__main__":
    main()
