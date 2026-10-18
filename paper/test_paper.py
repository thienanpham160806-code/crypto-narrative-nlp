import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest

from paper import build_docx, fill_results

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "paper.md"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
needs_real = pytest.mark.skipif(not (ROOT / "outputs" / "tables" / "real").exists(), reason="chưa có outputs/tables/real")


def template() -> str:
    return SOURCE.read_text(encoding="utf-8")


def test_template_has_five_part_structure_without_subsections():
    text = template()
    assert re.findall(r"^## (.+)$", text, flags=re.M) == [
        "TÓM TẮT", "ABSTRACT", "1. Giới thiệu", "2. Cơ sở lý thuyết và tổng quan các nghiên cứu trước đây",
        "3. Phương pháp nghiên cứu", "4. Kết quả nghiên cứu và thảo luận", "5. Kết luận", "Tài liệu tham khảo"]
    assert not re.search(r"^###|^\s*[-+] ", text, flags=re.M)
    tables = re.findall(r"^\*\*Bảng (\d+)\*\*$", text, flags=re.M)
    assert tables == [str(i) for i in range(1, len(tables) + 1)]
    tags = re.findall(r"\\tag\{(\d+)\}", text)
    assert tags == [str(i) for i in range(1, len(tags) + 1)]


def test_every_table_and_figure_is_referenced_in_text():
    body = re.sub(r"^\*\*(Bảng|Hình) \d+\*\*$", "", template(), flags=re.M)
    for label in re.findall(r"^\*\*((?:Bảng|Hình) \d+)\*\*$", template(), flags=re.M):
        assert label in body, label


def test_footnote_references_match_definitions():
    text = template()
    used = set(re.findall(r"\[\^(\w+)\](?!:)", text))
    defined = set(re.findall(r"^\[\^(\w+)\]:", text, flags=re.M))
    assert used == defined


@needs_real
def test_filled_manuscript_passes_citation_and_number_checks():
    bib = fill_results.parse_bib(fill_results.BIB)
    filled, info = fill_results.render(template(), bib)
    assert not info["bad_cites"]
    assert not fill_results.check(template(), filled, info, bib)
    assert "{{" not in filled


def test_omml_converter_handles_fraction_sum_and_accents():
    math = build_docx.omml(r"\frac{1}{N}\sum_{d \in D} \widehat{\beta}_{i} \left(x\right)^{2}")
    tags = {e.tag.split("}")[1] for e in math.iter()}
    assert {"f", "nary", "acc", "sSub", "sSup", "d"} <= tags
    with pytest.raises(ValueError):
        build_docx.omml(r"\unknowncmd")


@needs_real
def test_docx_has_word_equations_footnotes_apa_borders_and_header(tmp_path):
    output = tmp_path / "paper.docx"
    build_docx.package(SOURCE, output)
    text = template()
    with ZipFile(output) as z:
        document = ET.fromstring(z.read("word/document.xml"))
        notes = ET.fromstring(z.read("word/footnotes.xml"))
        header = z.read("word/header1.xml")
    assert len(document.findall(f".//{{{M}}}oMath")) == len(re.findall(r"\\tag\{", text))
    refs = document.findall(f".//{{{W}}}footnoteReference")
    assert len(refs) == len(set(re.findall(r"^\[\^(\w+)\]:", text, flags=re.M)))
    assert len(notes.findall(f"{{{W}}}footnote")) == len(refs) + 2  # + hai separator
    tables = document.findall(f".//{{{W}}}tbl")
    assert len(tables) >= len(re.findall(r"^\*\*Bảng \d+\*\*$", text, flags=re.M)) - 1  # + khung thông tin - bảng chưa có dữ liệu
    assert not any(t.findall(f".//{{{W}}}tblBorders") or t.findall(f".//{{{W}}}insideV") for t in tables)
    assert len(document.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/picture}pic")) == len(
        re.findall(r"^!\[", text, flags=re.M))
    assert b"PAGE" in header
