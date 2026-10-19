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
    s, probs = g.finbert_sentiment, g[["positive_prob", "negative_prob", "neutral_prob"]]
    top = probs.fillna(-1).to_numpy().argmax(1)
    g = g.assign(pos=s.clip(lower=0), neg=(-s).clip(lower=0), n_pos=(top == 0) & s.notna(),
                 n_neg=(top == 1) & s.notna(), **{f"attention_{k}": g.narrative.eq(k).astype(float) for k in NARR})
    out = g.groupby("date").agg(n_docs=("doc_id", "size"), sent_finbert=("finbert_sentiment", "mean"),
                                sent_lm=("lm_net", "mean"), sent_hv=("hv_net", "mean"), pos_sent=("pos", "mean"),
                                neg_sent=("neg", "mean"), n_pos=("n_pos", "sum"), n_neg=("n_neg", "sum"),
                                **{f"attention_{k}": (f"attention_{k}", "mean") for k in NARR},
                                **{f"soft_attention_{k}": (f"nprob_{k}", "mean") for k in NARR})
    a = (out.n_pos - out.n_neg) / (out.n_pos + out.n_neg)
    out["disagreement_af"] = np.sqrt(1 - a ** 2)
    out["disagreement_std"] = g.groupby("date").finbert_sentiment.std(ddof=1)
    out = out.reindex(dates)
    out["n_docs"] = out.n_docs.fillna(0).astype(int)
    out["neg_accel"] = out.neg_sent.diff()
    return out.rename_axis("date").reset_index()


def build(docs: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    news = docs[docs.is_canonical & docs.lang.eq("en") & docs.source.ne("sec")]
    df = news.merge(scores, on="doc_id", how="left", validate="one_to_one", indicator=True)
    if (miss := df._merge.ne("both").sum()):
        raise ValueError(f"{miss} tin canonical chưa có doc_scores – chạy lại features.narrative + features.doc_scores")
    df = df.drop(columns="_merge")
    df["date"] = df.public_ts_utc.dt.tz_convert("UTC").dt.floor("D")
    dates = pd.date_range(CFG["sample"]["start"], CFG["sample"]["end"], freq="D", tz="UTC")
    df = df[df.date.isin(dates)]
    parts = [daily(df, dates).assign(asset="ALL")]
    for a in CFG["sample"]["assets"]:
        d = daily(df[df.asset_tags.map(lambda t, a=a: a in list(t))], dates).assign(asset=a)
        parts.append(d[d.n_docs > 0])
    out = pd.concat(parts, ignore_index=True)
    cols = ["date", "asset", "n_docs", "sent_finbert", "sent_lm", "sent_hv", "pos_sent", "neg_sent"]
    return out[cols + [f"attention_{k}" for k in NARR] + ["neg_accel", "disagreement_af", "disagreement_std"]
               + [f"soft_attention_{k}" for k in NARR]]


def main():
    out = build(pd.read_parquet(D("interim", "documents.parquet")), pd.read_parquet(D("interim", "doc_scores.parquet")))
    out.to_parquet(D("processed", "text_daily.parquet"), index=False)
    print(out.groupby("asset").agg(days=("date", "size"), docs=("n_docs", "sum"), sent=("sent_finbert", "mean")))


if __name__ == "__main__":
    main()
