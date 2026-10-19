"""documents + doc_scores → data/processed/text_daily.parquet (DATA_CONTRACT §3).

Cắt ngày: tin thuộc ngày t ⇔ public_ts_utc ∈ [t, t+1) UTC; chỉ is_canonical. Nhánh chính tiếng Anh (lang = en);
tin tiếng Việt chỉ báo cáo riêng, không trộn vào chỉ số. Trọng số w_d = 1 (equal).
Chỉ tin báo (không SEC): hồ sơ S-1/19b-4 là văn bản pháp lý dài, giọng rủi ro → làm lệch sentiment ngày; SEC dùng cho
event study và timeline.
asset = 'ALL' (mọi tin, đủ lịch ngày của mẫu) + từng mã (chỉ ngày có tin gắn mã đó).
neg_accel_t = neg_sent_t − neg_sent_{t−1} (ngày lịch liền kề; ngày trước không có tin → NaN). Chỉ dùng quá khứ.
soft_attention_k = trung bình xác suất zero-shot nprob_k (không ép nhãn cứng; tổng 8 cột = 1).
disagreement_af = √(1 − A²), A = (N⁺ − N⁻)/(N⁺ + N⁻) theo nhãn FinBERT (Antweiler & Frank 2004); N⁺ + N⁻ = 0 → NaN.
disagreement_std = độ lệch chuẩn (ddof=1) của sentiment FinBERT các tin trong ngày (độ phân tán kiểu Khaksar et al.
2026); < 2 tin → NaN. Hai thước đo khác nhau, không gọi chung là "disagreement".
Mọi tin canonical phải có điểm (merge one_to_one, thiếu điểm → lỗi): không để tin chưa chấm trông như ngày không có tin.
Chạy: python -m features.daily_index
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from utils.common import CFG, D

NARR = CFG["nlp"]["narratives"]


def daily(g: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Trung bình có trọng số w (mặc định 1 → trung bình thường); n_docs luôn là số tin thật."""
    s, probs = g.finbert_sentiment, g[["positive_prob", "negative_prob", "neutral_prob"]]
    top = probs.fillna(-1).to_numpy().argmax(1)
    g = g.assign(pos=s.clip(lower=0), neg=(-s).clip(lower=0), n_pos=((top == 0) & s.notna()).astype(float),
                 n_neg=((top == 1) & s.notna()).astype(float), w=g.get("w", 1.0),
                 **{f"attention_{k}": g.narrative.eq(k).astype(float) for k in NARR})
    src = {"sent_finbert": "finbert_sentiment", "sent_lm": "lm_net", "sent_hv": "hv_net", "pos_sent": "pos",
           "neg_sent": "neg", **{f"attention_{k}": f"attention_{k}" for k in NARR},
           **{f"soft_attention_{k}": f"nprob_{k}" for k in NARR}}
    x = g[list(src.values())].set_axis(list(src), axis=1)
    num = x.mul(g.w, axis=0).groupby(g.date).sum(min_count=1)
    den = x.notna().mul(g.w, axis=0).groupby(g.date).sum()
    out = (num / den.where(den > 0)).join(g.groupby("date").agg(n_docs=("doc_id", "size")))
    out[["n_pos", "n_neg"]] = g[["n_pos", "n_neg"]].mul(g.w, axis=0).groupby(g.date).sum()
    a = (out.n_pos - out.n_neg) / (out.n_pos + out.n_neg)
    out["disagreement_af"] = np.sqrt(1 - a ** 2)
    out["disagreement_std"] = g.groupby("date").finbert_sentiment.std(ddof=1)
    out = out.reindex(dates)
    out["n_docs"] = out.n_docs.fillna(0).astype(int)
    out["neg_accel"] = out.neg_sent.diff()
    return out.rename_axis("date").reset_index()


VARIANTS = {"source_weighted": "text_daily_source_weighted.parquet", "ex_price": "text_daily_ex_price.parquet"}


def build(docs: pd.DataFrame, scores: pd.DataFrame, variant: str | None = None) -> pd.DataFrame:
    """variant: None = chính; 'source_weighted' = mỗi tên miền một phiếu/ngày (w = 1/số tin của tên miền trong ngày);
    'ex_price' = bỏ tin narrative price_speculation (tin mô tả giá, dễ phản ánh ngược giá → văn bản)."""
    news = docs[docs.is_canonical & docs.lang.eq("en") & docs.source.ne("sec")]
    df = news.merge(scores, on="doc_id", how="left", validate="one_to_one", indicator=True)
    if (miss := df._merge.ne("both").sum()):
        raise ValueError(f"{miss} tin canonical chưa có doc_scores – chạy lại features.narrative + features.doc_scores")
    df = df.drop(columns="_merge")
    df["date"] = df.public_ts_utc.dt.tz_convert("UTC").dt.floor("D")
    dates = pd.date_range(CFG["sample"]["start"], CFG["sample"]["end"], freq="D", tz="UTC")
    df = df[df.date.isin(dates)]
    if variant == "ex_price":
        df = df[df.narrative.ne("price_speculation")]
    elif variant == "source_weighted":
        host = df.url.str.extract(r"^\w+://(?:www\.)?([^/:?#]+)", expand=False).str.lower().fillna(df.source)
        df = df.assign(w=1.0 / df.groupby([df.date, host]).doc_id.transform("size"))
    elif variant is not None:
        raise ValueError(f"variant không hợp lệ: {variant}")
    parts = [daily(df, dates).assign(asset="ALL")]
    for a in CFG["sample"]["assets"]:
        d = daily(df[df.asset_tags.map(lambda t, a=a: a in list(t))], dates).assign(asset=a)
        parts.append(d[d.n_docs > 0])
    out = pd.concat(parts, ignore_index=True)
    cols = ["date", "asset", "n_docs", "sent_finbert", "sent_lm", "sent_hv", "pos_sent", "neg_sent"]
    return out[cols + [f"attention_{k}" for k in NARR] + ["neg_accel", "disagreement_af", "disagreement_std"]
               + [f"soft_attention_{k}" for k in NARR]]


def main():
    docs, scores = pd.read_parquet(D("interim", "documents.parquet")), pd.read_parquet(D("interim", "doc_scores.parquet"))
    for variant, name in [(None, "text_daily.parquet"), *VARIANTS.items()]:
        out = build(docs, scores, variant)
        out.to_parquet(D("processed", name), index=False)
        print(name, out.groupby("asset").agg(days=("date", "size"), docs=("n_docs", "sum"), sent=("sent_finbert", "mean")))


if __name__ == "__main__":
    main()
