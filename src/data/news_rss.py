"""RSS báo crypto (chỉ thu tiếp từ 2026-10 cho dashboard live; RSS không có lịch sử 2023–2026, xem docs/SOURCES.md).

Chỉ lưu tiêu đề + tóm tắt + link + pubDate, không lấy toàn văn. Cointelegraph cấm dùng nội dung cho AI/ML → không lưu
tóm tắt. first_seen_utc = lúc pipeline đọc feed. Mỗi lần chạy append vào data/raw/rss/<feed>.jsonl.
Chạy định kỳ (vd mỗi giờ): python -m data.news_rss
"""
from __future__ import annotations
import calendar, html, json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd
from utils.common import D

FEEDS = {  # tên: (url, ngôn ngữ, giữ tóm tắt)
    "coindesk": ("https://www.coindesk.com/arc/outboundfeeds/rss/", "en", True),
    "cointelegraph": ("https://cointelegraph.com/rss", "en", False),
    "theblock": ("https://www.theblock.co/rss.xml", "en", True),
    "decrypt": ("https://decrypt.co/feed", "en", True),
    "blogtienao": ("https://blogtienao.com/feed/", "vi", True),
}


def strip_html(s: str | None) -> str | None:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip() if s else None


def parse(name: str, content, now: pd.Timestamp) -> list[dict]:
    import feedparser
    _, lang, keep = FEEDS[name]
    out = []
    for e in feedparser.parse(content).entries:
        t = e.get("published_parsed") or e.get("updated_parsed")   # feedparser đã quy về UTC
        out.append(dict(feed=name, lang=lang, url=e.get("link"), title=strip_html(e.get("title")),
                        body=strip_html(e.get("summary")) if keep else None,
                        published_at_utc=pd.Timestamp(calendar.timegm(t), unit="s", tz="UTC").isoformat() if t else None,
                        first_seen_utc=now.isoformat()))
    return out


def poll(get=None) -> int:
    from utils.http import Client
    get = get or Client(rps=1).get
    now, n = pd.Timestamp.now(tz="UTC"), 0
    for name, (url, _, _) in FEEDS.items():
        r = get(url)
        if r is None:
            continue
        rows = parse(name, r.content, now)
        with open(D("raw", "rss", f"{name}.jsonl"), "a", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)
        n += len(rows)
    return n


def load() -> pd.DataFrame:
    fs = sorted(D("raw", "rss", "x").parent.glob("*.jsonl"))
    df = pd.concat([pd.read_json(f, lines=True, dtype=False) for f in fs]) if fs else pd.DataFrame(
        columns=["feed", "lang", "url", "title", "body", "published_at_utc", "first_seen_utc"])
    for c in ["published_at_utc", "first_seen_utc"]:
        df[c] = pd.to_datetime(df[c], utc=True, format="ISO8601")
    df = df.sort_values("first_seen_utc").drop_duplicates("url")      # giữ lần thấy đầu tiên
    src = df.feed.map(lambda f: f"vn:{f}" if FEEDS.get(f, ("", "en"))[1] == "vi" else f"rss:{f}")
    return df.assign(source=src, ts_source="rss_pubdate").drop(columns="feed")


if __name__ == "__main__":
    print(poll(), "items")
