"""Build the journal-style Word manuscript from UTF-8 paper/paper.md.

Uses only the Python standard library. Equations are OMML objects, notes are
true Word footnotes, and tables have APA-style horizontal rules.
"""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
XML = "http://www.w3.org/XML/1998/namespace"
for prefix, uri in {"w": W, "r": R, "m": M, "wp": WP, "a": A,
                    "pic": PIC}.items():
    ET.register_namespace(prefix, uri)


def q(uri: str, name: str) -> str:
    return f"{{{uri}}}{name}"


def el(parent: ET.Element, uri: str, name: str, attrs: dict | None = None,
       value: str | None = None) -> ET.Element:
    child = ET.SubElement(parent, q(uri, name), attrs or {})
    child.text = value
    return child


def xml(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rpr(run: ET.Element, *, bold: bool = False, italic: bool = False,
        size: int = 26, superscript: bool = False) -> None:
    props = el(run, W, "rPr")
    el(props, W, "rFonts", {q(W, "ascii"): "Times New Roman",
                            q(W, "hAnsi"): "Times New Roman",
                            q(W, "eastAsia"): "Times New Roman"})
    el(props, W, "sz", {q(W, "val"): str(size)})
    if bold:
        el(props, W, "b")
    if italic:
        el(props, W, "i")
    if superscript:
        el(props, W, "vertAlign", {q(W, "val"): "superscript"})


def add_run(paragraph: ET.Element, value: str, *, bold: bool = False,
            italic: bool = False, size: int = 26) -> None:
    run = el(paragraph, W, "r")
    rpr(run, bold=bold, italic=italic, size=size)
    el(run, W, "t", {q(XML, "space"): "preserve"}, value)


INLINE = re.compile(r"(\[\^(\d+)\]|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)")


def inline(paragraph: ET.Element, value: str, footnotes: dict[int, str],
           *, size: int = 26) -> None:
    position = 0
    for match in INLINE.finditer(value):
        if match.start() > position:
            add_run(paragraph, value[position:match.start()], size=size)
        if match.group(2):
            number = int(match.group(2))
            if number not in footnotes:
                raise ValueError(f"Footnote {number} has no definition")
            run = el(paragraph, W, "r")
            rpr(run, size=size, superscript=True)
            el(run, W, "footnoteReference", {q(W, "id"): str(number)})
        elif match.group(3):
            add_run(paragraph, match.group(3), bold=True, size=size)
        elif match.group(4):
            add_run(paragraph, match.group(4), italic=True, size=size)
        else:
            add_run(paragraph, match.group(5), size=size)
        position = match.end()
    if position < len(value):
        add_run(paragraph, value[position:], size=size)


def paragraph(parent: ET.Element, value: str, footnotes: dict[int, str],
              *, style: str = "Normal", center: bool = False,
              keep_next: bool = False, size: int = 26) -> ET.Element:
    p = el(parent, W, "p")
    props = el(p, W, "pPr")
    el(props, W, "pStyle", {q(W, "val"): style})
    if center:
        el(props, W, "jc", {q(W, "val"): "center"})
    if keep_next:
        el(props, W, "keepNext")
    inline(p, value, footnotes, size=size)
    return p


def styles() -> bytes:
    root = ET.Element(q(W, "styles"))
    for name, indent, size, bold, align in (
        ("Normal", 720, 26, False, None),
        ("Title", 0, 28, True, "center"),
        ("Subtitle", 0, 26, False, "center"),
        ("Heading1", 0, 26, True, None),
        ("Caption", 0, 26, True, None),
        ("TableText", 0, 20, False, None),
        ("TableNote", 0, 20, False, None),
        ("FootnoteText", 0, 20, False, None),
    ):
        style = el(root, W, "style", {q(W, "type"): "paragraph", q(W, "styleId"): name})
        el(style, W, "name", {q(W, "val"): name})
        ppr = el(style, W, "pPr")
        el(ppr, W, "spacing", {q(W, "before"): "0", q(W, "after"): "0",
                               q(W, "line"): "276", q(W, "lineRule"): "auto"})
        el(ppr, W, "ind", {q(W, "firstLine"): str(indent)})
        if align:
            el(ppr, W, "jc", {q(W, "val"): align})
        rp = el(style, W, "rPr")
        el(rp, W, "rFonts", {q(W, "ascii"): "Times New Roman",
                             q(W, "hAnsi"): "Times New Roman"})
        el(rp, W, "sz", {q(W, "val"): str(size)})
        if bold:
            el(rp, W, "b")
    return xml(root)


def table(body: ET.Element, rows: list[list[str]], notes: dict[int, str]) -> None:
    if not rows:
        return
    columns = max(map(len, rows))
    tbl = el(body, W, "tbl")
    props = el(tbl, W, "tblPr")
    el(props, W, "tblW", {q(W, "w"): "9000", q(W, "type"): "dxa"})
    el(props, W, "tblLayout", {q(W, "type"): "autofit"})
    borders = el(props, W, "tblBorders")
    for side in ("top", "bottom"):
        el(borders, W, side, {q(W, "val"): "single", q(W, "sz"): "8",
                              q(W, "color"): "000000"})
    for side in ("left", "right", "insideH", "insideV"):
        el(borders, W, side, {q(W, "val"): "nil"})
    grid = el(tbl, W, "tblGrid")
    for _ in range(columns):
        el(grid, W, "gridCol", {q(W, "w"): str(9000 // columns)})
    for index, cells in enumerate(rows):
        tr = el(tbl, W, "tr")
        trpr = el(tr, W, "trPr")
        el(trpr, W, "cantSplit")
        if index == 0:
            el(trpr, W, "tblHeader", {q(W, "val"): "true"})
        for cell_text in cells + [""] * (columns - len(cells)):
            cell = el(tr, W, "tc")
            if index == 0:
                cp = el(cell, W, "tcPr")
                cb = el(cp, W, "tcBorders")
                el(cb, W, "bottom", {q(W, "val"): "single", q(W, "sz"): "6",
                                      q(W, "color"): "000000"})
            p = paragraph(cell, cell_text.strip(), notes, style="TableText", size=20)
            if index == 0:
                for run in p.findall(q(W, "r")):
                    el(run.find(q(W, "rPr")), W, "b")


def equation(body: ET.Element, source: str, number: str) -> None:
    p = el(body, W, "p")
    ppr = el(p, W, "pPr")
    el(ppr, W, "pStyle", {q(W, "val"): "Normal"})
    el(ppr, W, "ind", {q(W, "firstLine"): "0"})
    el(ppr, W, "jc", {q(W, "val"): "center"})
    math = el(p, M, "oMath")
    run = el(math, M, "r")
    el(run, M, "t", value=source)
    add_run(p, f"    ({number})")


def image(body: ET.Element, source: Path, rel_id: str, description: str) -> None:
    data = source.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Only PNG figures are supported: {source}")
    width, height = struct.unpack(">II", data[16:24])
    cx = 5_600_000
    cy = round(cx * height / width)
    p = el(body, W, "p")
    props = el(p, W, "pPr")
    el(props, W, "jc", {q(W, "val"): "center"})
    run = el(p, W, "r")
    drawing = el(run, W, "drawing")
    inline_shape = el(drawing, WP, "inline")
    el(inline_shape, WP, "extent", {"cx": str(cx), "cy": str(cy)})
    el(inline_shape, WP, "docPr", {"id": rel_id[3:], "name": description})
    graphic = el(inline_shape, A, "graphic")
    graphic_data = el(graphic, A, "graphicData", {"uri": PIC})
    picture = el(graphic_data, PIC, "pic")
    nonvisual = el(picture, PIC, "nvPicPr")
    el(nonvisual, PIC, "cNvPr", {"id": "0", "name": source.name})
    el(nonvisual, PIC, "cNvPicPr")
    fill = el(picture, PIC, "blipFill")
    el(fill, A, "blip", {q(R, "embed"): rel_id})
    stretch = el(fill, A, "stretch")
    el(stretch, A, "fillRect")
    shape = el(picture, PIC, "spPr")
    transform = el(shape, A, "xfrm")
    el(transform, A, "off", {"x": "0", "y": "0"})
    el(transform, A, "ext", {"cx": str(cx), "cy": str(cy)})
    geometry = el(shape, A, "prstGeom", {"prst": "rect"})
    el(geometry, A, "avLst")


def footnotes_part(notes: dict[int, str]) -> bytes:
    root = ET.Element(q(W, "footnotes"))
    for number, kind in ((-1, "separator"), (0, "continuationSeparator")):
        item = el(root, W, "footnote", {q(W, "type"): kind, q(W, "id"): str(number)})
        p = el(item, W, "p")
        run = el(p, W, "r")
        el(run, W, kind)
    for number, content in sorted(notes.items()):
        item = el(root, W, "footnote", {q(W, "id"): str(number)})
        p = el(item, W, "p")
        ppr = el(p, W, "pPr")
        el(ppr, W, "pStyle", {q(W, "val"): "FootnoteText"})
        ref = el(p, W, "r")
        rpr(ref, size=20, superscript=True)
        el(ref, W, "footnoteRef")
        add_run(p, " ", size=20)
        inline(p, content, notes, size=20)
    return xml(root)


def header_part() -> bytes:
    root = ET.Element(q(W, "hdr"))
    p = el(root, W, "p")
    props = el(p, W, "pPr")
    el(props, W, "jc", {q(W, "val"): "center"})
    run = el(p, W, "r")
    rpr(run, size=20)
    el(run, W, "fldChar", {q(W, "fldCharType"): "begin"})
    run = el(p, W, "r")
    el(run, W, "instrText", {q(XML, "space"): "preserve"}, " PAGE ")
    run = el(p, W, "r")
    el(run, W, "fldChar", {q(W, "fldCharType"): "separate"})
    add_run(p, "1", size=20)
    run = el(p, W, "r")
    el(run, W, "fldChar", {q(W, "fldCharType"): "end"})
    return xml(root)


def parse(source: str) -> tuple[list[tuple[str, object]], dict[int, str]]:
    notes: dict[int, str] = {}
    lines = []
    for line in source.splitlines():
        match = re.match(r"^\[\^(\d+)\]:\s*(.*)$", line)
        if match:
            notes[int(match.group(1))] = match.group(2)
        else:
            lines.append(line)
    blocks: list[tuple[str, object]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("| "):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                candidate = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c or "") for c in candidate):
                    rows.append(candidate)
                i += 1
            blocks.append(("table", rows))
            continue
        if line.startswith("$$"):
            match = re.fullmatch(r"\$\$\s*(.*?)\s*\\tag\{(\d+)\}\s*\$\$", line)
            if not match:
                raise ValueError(f"Equation needs \\tag{{n}}: {line}")
            blocks.append(("equation", match.groups()))
            i += 1
            continue
        image_match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", line)
        if image_match:
            blocks.append(("image", image_match.groups()))
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(("title", line[2:]))
        elif line.startswith("## "):
            blocks.append(("heading", line[3:]))
        elif re.fullmatch(r"Bảng \d+", line):
            blocks.append(("caption", line))
        elif re.fullmatch(r"Hình \d+\. .*", line):
            blocks.append(("figure_caption", line))
        elif line.startswith("Ghi chú."):
            blocks.append(("note", line))
        else:
            blocks.append(("paragraph", line))
        i += 1
    return blocks, notes


def document_part(blocks: list[tuple[str, object]], notes: dict[int, str],
                  figure_paths: list[Path]) -> bytes:
    root = ET.Element(q(W, "document"))
    body = el(root, W, "body")
    after_title = 0
    image_number = 0
    for kind, value in blocks:
        if kind == "table":
            table(body, value, notes)
        elif kind == "equation":
            equation(body, *value)
        elif kind == "image":
            description, _ = value
            image_number += 1
            image(body, figure_paths[image_number - 1], f"rId{image_number + 3}", description)
        elif kind == "title":
            paragraph(body, value, notes, style="Title", center=True, keep_next=True)
            after_title = 4
        elif kind == "heading":
            paragraph(body, value, notes, style="Heading1", keep_next=True)
        elif kind == "caption":
            paragraph(body, value, notes, style="Caption", keep_next=True)
        elif kind == "figure_caption":
            paragraph(body, value, notes, style="Caption", center=True)
        elif kind == "note":
            paragraph(body, value, notes, style="TableNote", size=20)
        else:
            centered = after_title > 0
            paragraph(body, value, notes, style="Subtitle" if centered else "Normal",
                      center=centered, keep_next=centered)
            if centered:
                after_title -= 1
    section = el(body, W, "sectPr")
    el(section, W, "headerReference", {q(W, "type"): "default", q(R, "id"): "rId1"})
    el(section, W, "pgSz", {q(W, "w"): "11906", q(W, "h"): "16838"})
    el(section, W, "pgMar", {q(W, "top"): "1440", q(W, "right"): "1300",
                             q(W, "bottom"): "1440", q(W, "left"): "1300",
                             q(W, "header"): "500", q(W, "footer"): "500"})
    return xml(root)


def package(source: Path, output: Path) -> None:
    blocks, notes = parse(source.read_text(encoding="utf-8"))
    figure_paths = [(source.parent / path).resolve() for kind, value in blocks
                    if kind == "image" for _, path in [value]]
    content_types = ET.Element(q(CT, "Types"))
    for ext, kind in (("rels", "application/vnd.openxmlformats-package.relationships+xml"),
                      ("xml", "application/xml"), ("png", "image/png")):
        el(content_types, CT, "Default", {"Extension": ext, "ContentType": kind})
    for part, kind in (("document.xml", "wordprocessingml.document.main+xml"),
                       ("styles.xml", "wordprocessingml.styles+xml"),
                       ("header1.xml", "wordprocessingml.header+xml"),
                       ("footnotes.xml", "wordprocessingml.footnotes+xml")):
        el(content_types, CT, "Override", {"PartName": "/word/" + part,
                                           "ContentType": "application/vnd.openxmlformats-officedocument." + kind})
    root_rels = ET.Element(q(REL, "Relationships"))
    el(root_rels, REL, "Relationship", {"Id": "rId1", "Type": R + "/officeDocument",
                                        "Target": "word/document.xml"})
    doc_rels = ET.Element(q(REL, "Relationships"))
    for ident, role, target in (("rId1", "header", "header1.xml"),
                                ("rId2", "styles", "styles.xml"),
                                ("rId3", "footnotes", "footnotes.xml")):
        el(doc_rels, REL, "Relationship", {"Id": ident, "Type": R + "/" + role,
                                           "Target": target})
    for index, _ in enumerate(figure_paths, 1):
        el(doc_rels, REL, "Relationship", {"Id": f"rId{index + 3}",
            "Type": R + "/image", "Target": f"media/image{index}.png"})
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        parts = {
            "[Content_Types].xml": xml(content_types),
            "_rels/.rels": xml(root_rels),
            "word/document.xml": document_part(blocks, notes, figure_paths),
            "word/styles.xml": styles(),
            "word/header1.xml": header_part(),
            "word/footnotes.xml": footnotes_part(notes),
            "word/_rels/document.xml.rels": xml(doc_rels),
        }
        for name, data in parts.items():
            archive.writestr(name, data)
        for index, figure in enumerate(figure_paths, 1):
            archive.write(figure, f"word/media/image{index}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "paper" / "paper.md")
    parser.add_argument("--output", type=Path, default=ROOT / "paper" / "paper.docx")
    args = parser.parse_args()
    package(args.source, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
