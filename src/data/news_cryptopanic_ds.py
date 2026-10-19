"""CryptoPanic news dataset (soheilrahsaz/cryptoNewsDataset, CC0; 248k tin 2017-09 → 2025-12-03): CHỈ làm nhãn yếu RQ1.

Phiếu người dùng positive/negative = kỳ vọng giá của đám đông (bullish/bearish) cho từng tiêu đề.
Múi giờ newsDatetime = UTC: 695 tiêu đề trùng GDELT (2023–2025) có GDELT seendate − newsDatetime trung vị +1,3 giờ,
mode +1 giờ, P10 +0,6 giờ (khớp độ trễ seendate ≈ 2 giờ đo bằng HTML meta). Kiểm 2026-10-18.
Không đưa vào documents/text_daily: nguồn dừng 2025-12-03, không phủ kỳ test → gãy cấu trúc số tin và thành phần nguồn.
Chạy: python -m data.news_cryptopanic_ds  (tải + giải nén vào data/raw/cryptopanic_ds/)
"""
from __future__ import annotations
import subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, requests
from utils.common import CFG, D

URL = "https://github.com/soheilrahsaz/cryptoNewsDataset/raw/main/csvOutput/news_currencies_source_joinedResult.rar"
CSV = "news_currencies_source_joinedResult.csv"
VOTES = ["positive", "negative", "important"]


def download() -> pathlib.Path:
    f = D("raw", "cryptopanic_ds", CSV)
    if not f.exists():
        rar = f.with_name("joined.rar")
        rar.write_bytes(requests.get(URL, timeout=300).content)
        subprocess.run(["tar", "-xf", str(rar), "-C", str(f.parent)], check=True)    # bsdtar của Windows đọc được RAR5
    return f


def load(path=None, start=CFG["sample"]["start"], end=CFG["sample"]["end"]) -> pd.DataFrame:
    path = path or D("raw", "cryptopanic_ds", CSV)
    df = pd.read_csv(path, na_values=["NULL"], keep_default_na=False, low_memory=False,
                     usecols=["id", "title", "sourceDomain", "newsDatetime", "currencies", *VOTES])
    df["ts_utc"] = pd.to_datetime(df.newsDatetime, errors="coerce").dt.tz_localize("UTC")
    for c in VOTES:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    lo, hi = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
    df = df[(df.ts_utc >= lo) & (df.ts_utc < hi) & df.title.notna()]
    return df.assign(doc_id="cp:" + df.id.astype(str), source=df.sourceDomain).drop(columns=["newsDatetime", "sourceDomain"])


def weak_labels(df: pd.DataFrame, min_votes: int = 3, margin: int = 2) -> pd.DataFrame:
    """Nhãn positive/negative khi đủ phiếu và chênh lệch rõ; còn lại bỏ (không gán neutral)."""
    d = df.positive - df.negative
    keep = (df.positive + df.negative >= min_votes) & (d.abs() >= margin)
    return df[keep].assign(label=np.where(d[keep] > 0, "positive", "negative"))


if __name__ == "__main__":
    w = weak_labels(load(download()))
    print(len(w), w.label.value_counts().to_dict())
