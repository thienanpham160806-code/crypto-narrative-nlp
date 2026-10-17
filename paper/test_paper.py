import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from paper import build_docx, fill_results


ROOT = Path(__file__).resolve().parents[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def test_manuscript_follows_five_part_template():
    source = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    assert headings == [
        "TÓM TẮT", "ABSTRACT", "1. Giới thiệu",
        "2. Cơ sở lý thuyết và tổng quan các nghiên cứu trước đây",
        "3. Phương pháp nghiên cứu", "4. Kết quả nghiên cứu và thảo luận",
        "5. Kết luận", "Tài liệu tham khảo",
    ]
    assert not re.search(r"^###|^[-*] ", source, flags=re.M)
    assert re.findall(r"^Bảng (\d+)$", source, flags=re.M) == list("12345678")
    assert re.findall(r"\\tag\{(\d+)\}", source) == list("12345678")
    assert set(re.findall(r"\[\^(\d+)\](?!:)", source)) == set("1234")
    assert "outputs/tables/synthetic" not in source


def test_reference_dois_exist_in_bib_and_are_cited():
    source = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    body, references = source.split("## Tài liệu tham khảo", 1)
    bib = (ROOT / "paper" / "references.bib").read_text(encoding="utf-8")
    bib_dois = {x.lower() for x in re.findall(r"doi\s*=\s*\{([^}]+)\}", bib)}
    references = references.split("[^1]:", 1)[0]
    for paragraph in references.split("\n\n"):
        if "https://doi.org/" not in paragraph:
            continue
        doi = re.search(r"https://doi\.org/(\S+)", paragraph).group(1).lower()
        assert doi in bib_dois, doi
        first_author = paragraph.split(",", 1)[0]
        assert first_author in body, first_author


def test_docx_has_word_equations_true_footnotes_and_apa_borders(tmp_path):
    output = tmp_path / "paper.docx"
    build_docx.package(ROOT / "paper" / "paper.md", output)
    with ZipFile(output) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        notes = ET.fromstring(archive.read("word/footnotes.xml"))
        styles = ET.fromstring(archive.read("word/styles.xml"))
        header = archive.read("word/header1.xml")
        assert len(document.findall(f".//{{{M}}}oMath")) == 8
        assert len(document.findall(f".//{{{W}}}footnoteReference")) == 4
        assert len(notes.findall(f"{{{W}}}footnote")) == 6  # four notes and two separators
        assert len(document.findall(f".//{{{W}}}tbl")) == 9  # information frame and eight numbered tables
        assert len(document.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/picture}pic")) == 2
        assert b"PAGE" in header
        normal = next(x for x in styles.findall(f"{{{W}}}style")
                      if x.get(f"{{{W}}}styleId") == "Normal")
        assert normal.find(f".//{{{W}}}ind").get(f"{{{W}}}firstLine") == "720"
        assert normal.find(f".//{{{W}}}spacing").get(f"{{{W}}}line") == "276"
        for table in document.findall(f".//{{{W}}}tbl"):
            for side in ("insideV", "left", "right"):
                border = table.find(f"./{{{W}}}tblPr/{{{W}}}tblBorders/{{{W}}}{side}")
                assert border.get(f"{{{W}}}val") == "nil"


def test_fill_requires_independent_labels_and_renumbers(tmp_path, monkeypatch):
    monkeypatch.setattr(fill_results, "REAL", tmp_path)
    source = "Bảng 1\nFirst\n\n[[CHỜ_DỮ_LIỆU: bảng RQ1_nhãn_độc_lập]]\n\nBảng 2\nSecond\n\nSee Bảng 2.\n"
    path = tmp_path / "sentiment_validation.csv"
    with path.open("w", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, ["model", "label_source", "n", "macro_f1", "auc"])
        writer.writeheader()
        writer.writerow(dict(model="FinBERT", label_source="weak", n=1000,
                             macro_f1=0.7, auc=0.8))
    unchanged, changed = fill_results.fill(source)
    assert unchanged == source and not changed
    with path.open("a", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, ["model", "label_source", "n", "macro_f1", "auc"])
        writer.writerow(dict(model="FinBERT", label_source="human", n=300,
                             macro_f1=0.7, auc=0.8))
    result, changed = fill_results.fill(source)
    assert changed == ["RQ1_nhãn_độc_lập"]
    assert re.findall(r"^Bảng (\d+)$", result, flags=re.M) == ["1", "2", "3"]
    assert "See Bảng 2." not in result and "See Bảng 3." in result
