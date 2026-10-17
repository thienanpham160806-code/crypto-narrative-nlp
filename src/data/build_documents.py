"""Hợp nhất mọi nguồn → data/interim/documents.parquet (DATA_CONTRACT §1)
+ outputs/tables/corpus_stats.csv + outputs/tables/timestamp_accuracy.csv.

public_ts_utc = min(published_at_utc hợp lệ, first_seen_utc). published hợp lệ khi không sau first_seen, không sớm
hơn first_seen quá STALE, và CÙNG NGÀY UTC với first_seen: chữ ta có là bản thấy lúc first_seen; bài có thể đã sửa sau
giờ đăng, nên không được lùi chữ đó sang ngày trước (rò rỉ qua nửa đêm). Khác ngày → dùng first_seen.
URL chuẩn hóa: chỉ hạ chữ thường scheme + host, giữ path và query định danh, bỏ tham số tracking.
Dedup: cùng URL chuẩn hóa, hoặc tiêu đề giống ≥ dedup_threshold với bản canonical trong DEDUP_DAYS ngày trước
→ cùng dup_group; canonical = bản public_ts sớm nhất. Không nối chuỗi (so với canonical, không so với bản trùng).
Chạy: python -m data.build_documents
"""
from __future__ import annotations
import hashlib, json, re, sys, pathlib, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from utils.common import CFG, D, O
from data import news_gdelt, news_rss, news_sec

STALE = pd.Timedelta(hours=48)
DEDUP_DAYS = 3
TAGS = {"BTC": r"(?i:\bbitcoin)|\bBTC\b|\bXBT\b", "ETH": r"(?i:\bethereum|\bether\b)|\bETH\b",
        "SOL": r"(?i:\bsolana)|\bSOL\b", "BNB": r"(?i:\bbinance coin|\bbnb)\b",
        "XRP": r"(?i:\bxrp\b|\bripple\b)"}
TAGS = {k: re.compile(v) for k, v in TAGS.items() if k in CFG["sample"]["assets"]}
COLS = ["doc_id", "source", "url", "lang", "title", "body", "published_at_utc", "first_seen_utc", "ts_source",
        "public_ts_utc", "asset_tags", "dup_group", "is_canonical"]


TRACKING = re.compile(r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|ref|ref_src|cmpid|ocid|soc_src|soc_trk|guccounter|amp)$", re.I)


def norm_url(u: str) -> str:
    from urllib.parse import parse_qsl, urlencode, urlsplit
    p = urlsplit(str(u).strip())
    host = re.sub(r"^(www\.|amp\.|m\.)", "", p.netloc.lower())
    query = urlencode(sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not TRACKING.match(k)))
    return f"{host}{p.path.rstrip('/')}" + (f"?{query}" if query else "")


def norm_title(t: str) -> str:
    t = unicodedata.normalize("NFC", str(t or "")).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def tag(text: str) -> list[str]:
    return [k for k, rx in TAGS.items() if rx.search(text or "")]


def public_ts(pub: pd.Series, seen: pd.Series) -> pd.Series:
    ok = pub.notna() & (seen.isna() | ((pub <= seen) & (pub >= seen - STALE) & (pub.dt.floor("D") == seen.dt.floor("D"))))
    return pub.where(ok).combine_first(seen)


def dedup(df: pd.DataFrame, thr: float, fuzzy: pd.Series) -> pd.Series:
    """df đã sắp theo public_ts_utc. Trả mã canonical (index) cho mỗi dòng."""
    from rapidfuzz import fuzz, process
    canon = df.index.to_series().groupby(df.url.map(norm_url).values).transform("first")   # URL trùng → bản sớm nhất
    pool = df[canon.eq(df.index) & fuzzy & df.title.str.len().ge(20)]
    for _, g in pool.groupby("lang"):
        titles = g.title.map(norm_title).to_numpy()
        ts = g.public_ts_utc.dt.tz_localize(None).to_numpy()
        days = ts.astype("datetime64[D]")
        heads: list[int] = []                                             # vị trí các canonical trong g
        for d in np.unique(days):
            lo = d - np.timedelta64(DEDUP_DAYS, "D")
            heads = [h for h in heads if ts[h] >= lo]
            for i in np.flatnonzero(days == d):
                if heads:
                    sc = process.cdist([titles[i]], titles[heads], scorer=fuzz.ratio, score_cutoff=thr * 100)[0]
                    if sc.max() > 0:
                        canon[g.index[i]] = g.index[heads[int(sc.argmax())]]
                        continue
                heads.append(i)
    return canon.map(canon)        # thành viên của nhóm URL đi theo canonical của bản đầu nhóm


def build(frames: list[pd.DataFrame], extra: dict | None = None) -> pd.DataFrame:
    df = pd.concat([f for f in frames if len(f)], ignore_index=True)
    df = df[df.url.notna() & df.title.fillna("").str.strip().ne("")].copy()
    for c in ["published_at_utc", "first_seen_utc"]:
        df[c] = pd.to_datetime(df[c], utc=True)
    df["public_ts_utc"] = public_ts(df.published_at_utc, df.first_seen_utc)
    df = df[df.public_ts_utc.notna()].sort_values(["public_ts_utc", "source", "url"], kind="stable")
    df["doc_id"] = (df.source + df.url).map(lambda s: hashlib.sha1(s.encode()).hexdigest())
    df = df.drop_duplicates("doc_id").reset_index(drop=True)
    canon = dedup(df, CFG["text"]["dedup_threshold"], df.source.ne("sec"))
    df["is_canonical"] = canon.eq(df.index)
    df["dup_group"] = df.doc_id.values[canon.values]
    df["asset_tags"] = (df.title + " " + df.body.fillna("").str[:2000]).map(tag)
    return df


def lag_stats(source: str, comparison: str, pub: pd.Series, ref: pd.Series) -> dict:
    """lag = ref − pub (phút). Dương: ref (vd GDELT seendate) đến sau giờ đăng."""
    m = pub.notna() & ref.notna()
    lag = (ref[m] - pub[m]).dt.total_seconds() / 60
    return dict(source=source, comparison=comparison, n_pairs=int(m.sum()),
                median_lag_min=lag.median(), median_abs_lag_min=lag.abs().median(),
                p90_abs_lag_min=lag.abs().quantile(.9), pct_abs_gt_1h=100 * (lag.abs() > 60).mean(),
                pct_day_shift=100 * (ref[m].dt.floor("D") != pub[m].dt.floor("D")).mean())


def timestamp_table(df: pd.DataFrame, rss: pd.DataFrame, sec: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for s, g in df.groupby("source"):
        p = g.published_at_utc.dropna()
        rows.append({**lag_stats(s, "published vs first_seen", g.published_at_utc, g.first_seen_utc),
                     "n_docs": len(g), "pct_published": 100 * len(p) / len(g),
                     "pct_has_time": 100 * (p != p.dt.floor("D")).mean() if len(p) else np.nan})
    gd = df[df.source.eq("gdelt")].assign(k=lambda x: x.url.map(norm_url))
    m = gd.merge(rss.assign(k=rss.url.map(norm_url))[["k", "published_at_utc"]], on="k", suffixes=("", "_rss"))
    rows.append(lag_stats("gdelt", "rss pubDate vs gdelt seendate (cùng URL)", m.published_at_utc_rss, m.first_seen_utc))
    if len(sec):
        acc = sec.published_at_utc.dropna()
        fd = sec.loc[acc.index, "file_date"]
        rows.append(dict(source="sec", comparison="accepted (UTC) vs file_date", n_pairs=len(acc),
                         pct_day_shift=100 * (acc.dt.tz_localize(None).dt.floor("D") != fd).mean()))
    return pd.DataFrame(rows)


def corpus_table(df: pd.DataFrame) -> pd.DataFrame:
    s0, s1 = pd.Timestamp(CFG["sample"]["start"], tz="UTC"), pd.Timestamp(CFG["sample"]["end"], tz="UTC") + pd.Timedelta(days=1)
    rows = []
    for (s, lang), g in list(df.groupby(["source", "lang"])) + [(("ALL", "all"), df)]:
        c = g[g.is_canonical]
        ins = c[(c.public_ts_utc >= s0) & (c.public_ts_utc < s1)]
        per_day = ins.public_ts_utc.dt.floor("D").value_counts()
        rows.append(dict(source=s, lang=lang, n_docs=len(g), n_canonical=len(c), dup_rate=1 - len(c) / len(g),
                         n_in_sample=len(ins), days_with_docs=len(per_day), docs_per_day_median=per_day.median(),
                         first=g.public_ts_utc.min(), last=g.public_ts_utc.max(), pct_body=100 * g.body.notna().mean(),
                         pct_any_asset=100 * c.asset_tags.str.len().gt(0).mean(),
                         **{f"pct_{k}": 100 * c.asset_tags.map(lambda t, k=k: k in t).mean() for k in TAGS}))
    return pd.DataFrame(rows)


def load_meta() -> pd.DataFrame:
    f = D("raw", "html_meta.jsonl")
    m = pd.read_json(f, lines=True, dtype=False) if f.exists() else pd.DataFrame(columns=["url", "published_at_utc"])
    return m.dropna().assign(published_at_utc=lambda x: pd.to_datetime(x.published_at_utc, utc=True, format="ISO8601"))


def main():
    gd = pd.concat([news_gdelt.load("en"), news_gdelt.load("vi")], ignore_index=True)
    meta = load_meta().drop_duplicates("url").set_index("url").published_at_utc
    gd["published_at_utc"] = pd.to_datetime(gd.url.map(meta.astype(object)), utc=True)
    gd.loc[gd.published_at_utc.notna(), "ts_source"] = "html_meta"
    rss, sec = news_rss.load(), news_sec.load()
    df = build([gd, rss, sec.drop(columns="file_date")])
    df[COLS].to_parquet(D("interim", "documents.parquet"), index=False)
    corpus_table(df).to_csv(O("tables", "corpus_stats.csv"), index=False)
    timestamp_table(df, rss, sec).to_csv(O("tables", "timestamp_accuracy.csv"), index=False)
    print(corpus_table(df).to_string())


if __name__ == "__main__":
    main()
