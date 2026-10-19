"""Xuất kết quả nghiên cứu → JSON tĩnh cho dashboard (Vercel và local dùng chung).

Đọc data/processed (text_daily, market_daily, ucry_daily), data/interim (documents, doc_scores), outputs/tables
(của Claude) và outputs/tables/real (của Codex). Ghi dashboard/web/public/data/*.json.
Thẻ tóm tắt tính tại ngày cuối có tin, chỉ dùng dữ liệu ≤ ngày đó (point-in-time):
  dominant = argmax trung bình soft_attention 7 ngày; intensity = z của n_docs 7 ngày so với 90 ngày trước;
  sentiment = trung bình sent_finbert 7 ngày; neg_accel = neg_sent 7 ngày / 7 ngày trước − 1;
  vol risk = phân vị của RV dự báo lập đúng ngày đó (Codex, FORECAST) – không có thì RV thực hiện – trong 365 ngày RV.
Chạy: python dashboard/export.py
"""
from __future__ import annotations
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np, pandas as pd
from utils.common import CFG

NARR = CFG["nlp"]["narratives"]
OUT = ROOT / "dashboard" / "web" / "public" / "data"
RISK = [(0.5, "low"), (0.8, "normal"), (0.95, "elevated"), (1.01, "high")]
SNIPPETS_PER_DAY = 6
FORECAST = ("EN", "text")       # mô hình chỉ định cho thẻ rủi ro: Elastic Net market+text, BTC RV h=1


def read(path: pathlib.Path, **kw) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path, **kw) if path.suffix == ".parquet" else pd.read_csv(path, **kw)


def records(df: pd.DataFrame) -> list[dict]:
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return json.loads(df.to_json(orient="records", force_ascii=False, double_precision=5))


def risk_level(pct: float) -> str:
    return next(name for lim, name in RISK if pct < lim)


def summary(text: pd.DataFrame, market: pd.DataFrame, forecasts: pd.DataFrame) -> dict:
    al = text[text.asset.eq("ALL")].set_index("date").sort_index()
    have = al[al.n_docs > 0]
    if have.empty:
        return {}
    t = have.index[-1]
    w7, prev7 = al.loc[t - pd.Timedelta(days=6):t], al.loc[t - pd.Timedelta(days=13):t - pd.Timedelta(days=7)]
    base = al.loc[t - pd.Timedelta(days=96):t - pd.Timedelta(days=7), "n_docs"]
    soft = w7[[f"soft_attention_{k}" for k in NARR]].mean()
    dom = soft.idxmax().removeprefix("soft_attention_")
    z = (w7.n_docs.mean() - base.mean()) / base.std() if base.std() > 0 else np.nan
    neg = w7.neg_sent.mean() / prev7.neg_sent.mean() - 1 if prev7.neg_sent.mean() > 0 else np.nan
    btc = market[market.asset.eq("BTC")].set_index("date").sort_index().rv.loc[:t]
    fc = forecasts
    if len(fc):
        m, v = FORECAST
        fc = fc[(fc.asset == "BTC") & (fc.target == "rv") & (fc.horizon == 1) & (fc.model == m) & (fc.version == v)
                & (pd.to_datetime(fc.date, utc=True) == t)]                # chỉ dự báo lập đúng ngày t
    vol, vol_src = (float(fc.prediction.iloc[0]), "forecast") if len(fc) else \
        (float(btc.iloc[-1]) if len(btc) else np.nan, "realized")
    hist = btc.loc[t - pd.Timedelta(days=365):t]
    pct = float((hist < vol).mean()) if len(hist) and not np.isnan(vol) else np.nan
    return dict(as_of=t.strftime("%Y-%m-%d"), n_docs_7d=int(w7.n_docs.sum()),
                dominant=dict(narrative=dom, share=float(soft.max())),
                intensity=dict(z=None if np.isnan(z) else float(z),
                               level=None if np.isnan(z) else "high" if z > 1 else "low" if z < -1 else "normal"),
                sentiment=dict(value=float(w7.sent_finbert.mean())),
                neg_accel=dict(value=None if np.isnan(neg) else float(neg)),
                vol_risk=dict(value=vol, percentile=None if np.isnan(pct) else pct, source=vol_src,
                              level=None if np.isnan(pct) else risk_level(pct)))


def fan(forecasts: pd.DataFrame, min_err: int = 30) -> pd.DataFrame:
    """Fan chart RV BTC h=1 (mô hình FORECAST), vẽ tại target_date. Dải 50%/90% = dự báo + phân vị sai số
    (actual − prediction) của các dự báo có target_date < ngày lập dự báo hiện tại: chỉ sai số đã biết lúc đó."""
    cols = ["date", "fan_pred", "fan_lo50", "fan_hi50", "fan_lo90", "fan_hi90"]
    if forecasts.empty:
        return pd.DataFrame(columns=cols)
    m, v = FORECAST
    f = forecasts[(forecasts.asset == "BTC") & (forecasts.target == "rv") & (forecasts.horizon == 1)
                  & (forecasts.model == m) & (forecasts.version == v)].copy()
    f["origin"], f["target"] = pd.to_datetime(f.date, utc=True), pd.to_datetime(f.target_date, utc=True)
    f = f.sort_values("origin")
    err = (f.actual - f.prediction).to_numpy()
    out = []
    for r in f.itertuples():
        past = err[(f.target < r.origin).to_numpy()]
        q = np.quantile(past, [.05, .25, .75, .95]) if len(past) >= min_err else [np.nan] * 4
        lo = lambda v: max(v, 0.0) if not np.isnan(v) else v                 # RV ≥ 0: dải không xuống dưới 0
        out.append([r.target, r.prediction, lo(r.prediction + q[1]), r.prediction + q[2], lo(r.prediction + q[0]),
                    r.prediction + q[3]])
    return pd.DataFrame(out, columns=cols)


def daily(text: pd.DataFrame, market: pd.DataFrame, ucry: pd.DataFrame) -> pd.DataFrame:
    al = text[text.asset.eq("ALL")].drop(columns="asset")
    btc = market[market.asset.eq("BTC")][["date", "close", "ret", "rv"]].rename(columns=lambda c: c if c == "date" else f"btc_{c}")
    out = al.merge(btc, on="date", how="left")
    if len(ucry):
        out = out.merge(ucry[["date", "ucry_policy", "ucry_price"]], on="date", how="left")
    return out


def attention_by_asset(text: pd.DataFrame) -> pd.DataFrame:
    a = text[text.asset.ne("ALL")]
    return a[["date", "asset", "n_docs", "sent_finbert"] + [f"soft_attention_{k}" for k in NARR]]


def news(docs: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    d = docs[docs.is_canonical & docs.source.ne("sec")].merge(scores, on="doc_id")
    d["date"] = d.public_ts_utc.dt.floor("D")
    d["hour"] = d.public_ts_utc.dt.hour
    return d


def helicorder(d: pd.DataFrame) -> pd.DataFrame:
    """Số tin theo (ngày UTC, giờ) – mỗi ngày một hàng 24 giá trị."""
    c = d[d.lang.eq("en")].groupby(["date", "hour"]).size().unstack(fill_value=0).reindex(columns=range(24), fill_value=0)
    return pd.DataFrame(dict(date=c.index, counts=c.to_numpy().tolist()))


def snippets(d: pd.DataFrame) -> pd.DataFrame:
    d = d[d.lang.eq("en")].assign(strength=lambda x: x.finbert_sentiment.abs().fillna(0) + x.narrative_prob.fillna(0))
    top = d.sort_values("strength", ascending=False).groupby("date").head(SNIPPETS_PER_DAY)
    cols = ["doc_id", "public_ts_utc", "source", "title", "url", "narrative", "narrative_prob", "finbert_sentiment",
            "asset_tags", "ts_source"]
    return top.sort_values("public_ts_utc")[cols].assign(asset_tags=lambda x: x.asset_tags.map(list))


def main():
    P, I, T = ROOT / "data" / "processed", ROOT / "data" / "interim", ROOT / "outputs" / "tables"
    text, market, ucry = read(P / "text_daily.parquet"), read(P / "market_daily.parquet"), read(P / "ucry_daily.parquet")
    docs, scores = read(I / "documents.parquet"), read(I / "doc_scores.parquet")
    real = T / "real"
    forecasts = read(real / "forecasts.csv")
    OUT.mkdir(parents=True, exist_ok=True)
    d = news(docs, scores)
    files = {
        "meta": dict(sample=CFG["sample"], split=CFG["split"], narratives=NARR,
                     generated_utc=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
                     news_days=int(text[text.asset.eq("ALL") & text.n_docs.gt(0)].shape[0]),
                     calendar_days=int(text[text.asset.eq("ALL")].shape[0])),
        "summary": summary(text, market, forecasts),
        "daily": records(daily(text, market, ucry)),
        "assets": records(attention_by_asset(text)),
        "helicorder": records(helicorder(d)),
        "snippets": records(snippets(d)),
        "fan": records(fan(forecasts)),
        "timing": dict(accuracy=records(read(T / "timestamp_accuracy.csv")), corpus=records(read(T / "corpus_stats.csv"))),
        "narratives": dict(taxonomy=records(read(T / "narrative_taxonomy.csv")), topics=records(read(T / "narrative_topics.csv"))),
        "validation": records(read(T / "sentiment_validation.csv")),
        "models": {k: records(read(real / f"{k}.csv")) for k in ("coverage", "oos", "wald", "granger", "forecasts", "shap")},
    }
    for name, obj in files.items():
        (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print({k: (OUT / f"{k}.json").stat().st_size for k in files})


if __name__ == "__main__":
    main()
