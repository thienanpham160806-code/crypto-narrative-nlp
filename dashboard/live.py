"""Tab Live: tin RSS mới nhất, chấm FinBERT + zero-shot narrative. KHÔNG đưa vào chỉ số nghiên cứu.

Local (server.py) dùng mọi feed trong news_rss.FEEDS (dùng cá nhân, phi thương mại).
Bản công khai (Vercel, `python dashboard/live.py`) chỉ dùng PUBLIC_FEEDS: CoinDesk, Cointelegraph, Decrypt cấm
robot/scraper trong ToS (docs/SOURCES.md); The Block khai `ai-input=yes` trong robots.txt. Chỉ tiêu đề + link.
"""
from __future__ import annotations
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np, pandas as pd

PUBLIC_FEEDS = ("theblock",)
LIMIT = 40
_models = {}


def models():
    if not _models:
        from transformers import pipeline
        from features import narrative
        from utils.common import CFG
        enc = narrative.encoder()
        _models.update(clf=pipeline("text-classification", model=CFG["nlp"]["finbert_model"], top_k=None, truncation=True),
                       enc=enc, proto=np.asarray(enc.encode([narrative.PROTO[k] for k in narrative.NARR], normalize_embeddings=True)))
    return _models


def score(items: pd.DataFrame, clf, enc, proto) -> pd.DataFrame:
    from features.narrative import NARR
    if items.empty:
        return items
    out = clf(items.title.tolist(), batch_size=32)
    probs = [{d["label"]: d["score"] for d in o} for o in out]
    emb = np.asarray(enc.encode(items.title.tolist(), normalize_embeddings=True))
    return items.assign(finbert_sentiment=[p["positive"] - p["negative"] for p in probs],
                        narrative=np.array(NARR, object)[(emb @ proto.T).argmax(1)])


def fetch(feeds, get=None) -> pd.DataFrame:
    from data import news_rss
    from utils.http import Client
    get = get or Client(rps=1).get
    now, rows = pd.Timestamp.now(tz="UTC"), []
    for name in feeds:
        r = get(news_rss.FEEDS[name][0])
        if r is not None:
            rows += [x for x in news_rss.parse(name, r.content, now) if x["lang"] == "en"]
    df = pd.DataFrame(rows, columns=["feed", "lang", "url", "title", "body", "published_at_utc", "first_seen_utc"])
    df["public_ts_utc"] = df.published_at_utc.fillna(df.first_seen_utc)
    return df.dropna(subset=["title", "url"]).drop_duplicates("url").sort_values("public_ts_utc", ascending=False).head(LIMIT)


def payload(feeds) -> dict:
    m = models()
    df = score(fetch(feeds), m["clf"], m["enc"], m["proto"])
    items = [dict(url=r.url, title=r.title, source=r.feed, public_ts_utc=str(r.public_ts_utc).replace("+00:00", "Z"),
                  finbert_sentiment=round(float(r.finbert_sentiment), 3), narrative=r.narrative) for r in df.itertuples()]
    return dict(updated_utc=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"), feeds=list(feeds), items=items)


if __name__ == "__main__":
    out = ROOT / "dashboard" / "web" / "public" / "data" / "live.json"
    out.write_text(json.dumps(payload(PUBLIC_FEEDS), ensure_ascii=False), encoding="utf-8")
    print("ghi", out)
