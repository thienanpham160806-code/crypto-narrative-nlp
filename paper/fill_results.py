"""Fill evidence gaps only when corresponding real-data checks become usable.

Run from the repository root: python paper/fill_results.py [--output FILE].
The default updates paper/paper.md in UTF-8; unresolved markers stay visible.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "outputs" / "tables" / "real"
PAPER = ROOT / "paper" / "paper.md"


def rows(name: str) -> list[dict[str, str]]:
    path = REAL / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def number(value: str | None) -> float:
    try:
        return float(value or "nan")
    except ValueError:
        return math.nan


def fmt(value: str | None, digits: int = 4) -> str:
    n = number(value)
    return f"{n:.{digits}f}".replace(".", ",") if math.isfinite(n) else "—"


def note(source: str) -> str:
    return (
        f"Ghi chú. Số liệu từ `{source}`; ***, **, * biểu thị mức ý nghĩa thống kê "
        "lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả."
    )


def validation_table() -> str | None:
    data = rows("sentiment_validation.csv")
    # Weak platform votes do not count as independent tone labels.
    data = [r for r in data if r.get("label_source", "").lower() in {"human", "expert"}
            and number(r.get("n")) >= 100]
    if not data:
        return None
    lines = ["Bảng [mới]", "Độ Chính Xác Cảm Xúc Trên Nhãn Độc Lập", "",
             "| Bộ chấm | N | Macro-F1 | AUC |", "|---|---:|---:|---:|"]
    for r in data:
        lines.append(f"| {r.get('model', '—')} | {int(number(r['n']))} | "
                     f"{fmt(r.get('macro_f1'))} | {fmt(r.get('auc'))} |")
    lines += ["", note("sentiment_validation.csv"), "",
              "Bảng này đo khả năng gán sắc thái trên nhãn độc lập; hệ số dự báo ở Bảng 4 đo một khái niệm khác."]
    return "\n".join(lines)


def granger_table() -> str | None:
    data = [r for r in rows("granger.csv") if number(r.get("nobs")) >= 30
            and math.isfinite(number(r.get("pvalue")))]
    if not data:
        return None
    lines = ["Bảng [mới]", "Kiểm Định Granger Trên Đoạn Ngày Liên Tục", "",
             "| Tài sản | Biến kết quả | N | p thô | p Holm |", "|---|---|---:|---:|---:|"]
    for r in data:
        lines.append(f"| {r['asset']} | {r['outcome']} | {int(number(r['nobs']))} | "
                     f"{fmt(r.get('pvalue'))} | {fmt(r.get('p_holm'))} |")
    lines += ["", note("granger.csv"), "",
              "Kiểm định Granger phản ánh khả năng dự báo có điều kiện, không nhận dạng quan hệ nhân quả."]
    return "\n".join(lines)


def forecast_table() -> str | None:
    data = [r for r in rows("oos.csv") if r.get("asset") == "BTC"
            and r.get("target") == "rv" and r.get("horizon") == "1"
            and r.get("version") == "text" and number(r.get("inference_nobs")) >= 30
            and math.isfinite(number(r.get("dm_p_holm")))]
    gw = {r.get("model"): r for r in rows("gw.csv") if r.get("asset") == "BTC"
          and r.get("target") == "rv" and r.get("horizon") == "1"
          and number(r.get("nobs")) >= 30 and math.isfinite(number(r.get("gw_p_holm")))}
    mcs = {r.get("model"): r for r in rows("mcs.csv") if r.get("asset") == "BTC"
           and r.get("target") == "rv" and r.get("horizon") == "1"
           and r.get("version") == "text"
           and math.isfinite(number(r.get("mcs_p_holm")))}
    data = [r for r in data if r["model"] in gw and r["model"] in mcs]
    if not data:
        return None
    lines = ["Bảng [mới]", "Kiểm Định Giá Trị Dự Báo Gia Tăng", "",
             "| Mô hình | N liên tục | p DM Holm | p CW Holm | p GW Holm | p MCS Holm | R² OOS |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for r in data:
        lines.append(f"| {r['model']} | {int(number(r['inference_nobs']))} | "
                     f"{fmt(r.get('dm_p_holm'))} | {fmt(r.get('cw_p_holm'))} | "
                     f"{fmt(gw[r['model']].get('gw_p_holm'))} | "
                     f"{fmt(mcs[r['model']].get('mcs_p_holm'))} | "
                     f"{fmt(r.get('r2_oos_ct'))} |")
    lines += ["", note("oos.csv`, `gw.csv`, `mcs.csv"), "",
              "Chỉ khi đoạn kiểm định đủ dài mới có thể đối chiếu lợi ích dự báo gia tăng với mô hình thị trường."]
    return "\n".join(lines)


def robustness_table() -> str | None:
    status = rows("robustness_status.csv")
    if not status or any(r.get("status", "").startswith("pending") for r in status):
        return None
    data = rows("robustness.csv")
    if not data:
        return None
    cols = [c for c in ("variant", "asset", "target", "horizon", "coef", "p_holm")
            if c in data[0]]
    if len(cols) < 3:
        return None
    lines = ["Bảng [mới]", "Độ Vững Của Cách Xây Chỉ Số Tin", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in data[:15]:
        lines.append("| " + " | ".join(r.get(c, "—") or "—" for c in cols) + " |")
    lines += ["", note("robustness.csv"), "",
              "Các biến thể chỉ có thể so sánh khi cùng bộ tin được dựng lại theo từng quy tắc nguồn."]
    return "\n".join(lines)


FILLERS = {
    "RQ1_nhãn_độc_lập": validation_table,
    "VAR_Granger_liên_tục": granger_table,
    "RQ5_DM_GW_MCS_đủ_chuỗi": forecast_table,
    "robustness_source_weighted_exclude_price": robustness_table,
}


def renumber_tables(markdown: str) -> str:
    captions = list(re.finditer(r"(?m)^Bảng (\d+|\[mới\])$", markdown))
    old_to_new = {m.group(1): str(i) for i, m in enumerate(captions, 1)
                  if m.group(1).isdigit()}
    # Replace old prose references before changing captions; new labels are unique.
    markdown = re.sub(r"Bảng (\d+)",
                      lambda m: f"Bảng @OLD{m.group(1)}@", markdown)
    markdown = re.sub(r"(?m)^Bảng (?:@OLD\d+@|\[mới\])$", "Bảng [mới]", markdown)
    # Rewrite captions in document order, then restore prose references.
    current = 0
    lines = markdown.splitlines()
    for i, line in enumerate(lines):
        if line == "Bảng [mới]":
            current += 1
            lines[i] = f"Bảng {current}"
    markdown = "\n".join(lines) + "\n"
    return re.sub(r"Bảng @OLD(\d+)@",
                  lambda m: f"Bảng {old_to_new.get(m.group(1), m.group(1))}", markdown)


def fill(markdown: str) -> tuple[str, list[str]]:
    changed = []
    for name, create in FILLERS.items():
        marker = f"[[CHỜ_DỮ_LIỆU: bảng {name}]]"
        if marker not in markdown:
            continue
        table = create()
        if table:
            markdown = markdown.replace(marker, "\n\n" + table)
            changed.append(name)
    if changed:
        markdown = renumber_tables(markdown)
    return markdown, changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PAPER)
    args = parser.parse_args()
    source = PAPER.read_text(encoding="utf-8")
    result, changed = fill(source)
    args.output.write_text(result, encoding="utf-8")
    print("Filled: " + (", ".join(changed) if changed else "none; markers retained"))


if __name__ == "__main__":
    main()
