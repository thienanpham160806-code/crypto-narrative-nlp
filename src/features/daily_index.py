"""documents + doc_scores → data/processed/text_daily.parquet (DATA_CONTRACT §3).

Cắt ngày: tin thuộc ngày t ⇔ public_ts_utc ∈ [t, t+1) UTC; chỉ is_canonical. Nhánh chính tiếng Anh (lang = en);
tin tiếng Việt chỉ báo cáo riêng, không trộn vào chỉ số. Trọng số w_d = 1 (equal).
asset = 'ALL' (mọi tin, đủ lịch ngày của mẫu) + từng mã (chỉ ngày có tin gắn mã đó).
neg_accel_t = neg_sent_t − neg_sent_{t−1} (ngày lịch liền kề; ngày trước không có tin → NaN). Chỉ dùng quá khứ.
Chạy: python -m features.daily_index
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd
from utils.common import CFG, D

NARR = CFG["nlp"]["narratives"]


def daily(g: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    s = g.finbert_sentiment
    g = g.assign(pos=s.clip(lower=0), neg=(-s).clip(lower=0),
                 **{f"attention_{k}": g.narrative.eq(k).astype(float) for k in NARR})
    out = g.groupby("date").agg(n_docs=("doc_id", "size"), sent_finbert=("finbert_sentiment", "mean"),
                                sent_lm=("lm_net", "mean"), sent_hv=("hv_net", "mean"), pos_sent=("pos", "mean"),
                                neg_sent=("neg", "mean"), **{f"attention_{k}": (f"attention_{k}", "mean") for k in NARR})
    out = out.reindex(dates)
    out["n_docs"] = out.n_docs.fillna(0).astype(int)
    out["neg_accel"] = out.neg_sent.diff()
    return out.rename_axis("date").reset_index()


def build(docs: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    df = docs[docs.is_canonical & docs.lang.eq("en")].merge(scores, on="doc_id")
    df["date"] = df.public_ts_utc.dt.tz_convert("UTC").dt.floor("D")
    dates = pd.date_range(CFG["sample"]["start"], CFG["sample"]["end"], freq="D", tz="UTC")
    df = df[df.date.isin(dates)]
    parts = [daily(df, dates).assign(asset="ALL")]
    for a in CFG["sample"]["assets"]:
        d = daily(df[df.asset_tags.map(lambda t, a=a: a in list(t))], dates).assign(asset=a)
        parts.append(d[d.n_docs > 0])
    out = pd.concat(parts, ignore_index=True)
    cols = ["date", "asset", "n_docs", "sent_finbert", "sent_lm", "sent_hv", "pos_sent", "neg_sent"]
    return out[cols + [f"attention_{k}" for k in NARR] + ["neg_accel"]]


def main():
    out = build(pd.read_parquet(D("interim", "documents.parquet")), pd.read_parquet(D("interim", "doc_scores.parquet")))
    out.to_parquet(D("processed", "text_daily.parquet"), index=False)
    print(out.groupby("asset").agg(days=("date", "size"), docs=("n_docs", "sum"), sent=("sent_finbert", "mean")))


if __name__ == "__main__":
    main()
