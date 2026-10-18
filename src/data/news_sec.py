"""SEC EDGAR full-text search: hồ sơ nhắc crypto (S-1 quỹ ETF, 19b-4, 8-K) → tiêu đề + text (.htm/.txt, không OCR).

Giờ ra công chúng = "Accepted" trên trang index (giờ New York) → UTC. KHÔNG dùng file_date: nộp sau 17:30 ET được
tính ngày làm việc kế tiếp (docs/SOURCES.md). Bắt buộc env CONTACT_EMAIL (SEC fair access: User-Agent có email).
Chạy: python -m data.news_sec
"""
from __future__ import annotations
import json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd
from utils.common import CFG, D, to_utc
from data.news_rss import strip_html

FTS = "https://efts.sec.gov/LATEST/search-index"
QUERY = '"bitcoin" OR "ethereum" OR "crypto asset" OR "digital asset"'
FORMS = "S-1,S-1/A,19b-4,8-K"
BODY_CHARS = 20_000   # shortcut: chỉ giữ 20k ký tự đầu (FinBERT dùng ≤20 câu, LM đủ mẫu); cần toàn văn thì tăng


def archive(cik: str, adsh: str, name: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{name}"


def accepted(index_html: str) -> pd.Timestamp | None:
    m = re.search(r"Accepted</div>\s*<div class=\"info\">([\d\- :]+)</div>", index_html)
    return to_utc(pd.Series([m.group(1)]), "America/New_York")[0] if m else None


def search(get, start: str, end: str) -> list[dict]:
    """Chia theo tháng, phân trang 100 hit/lệnh."""
    hits = []
    for lo in pd.date_range(start, end, freq="MS"):
        hi = min(lo + pd.offsets.MonthEnd(0), pd.Timestamp(end))
        frm = 0
        while True:
            r = get(FTS, params=dict(q=QUERY, forms=FORMS, dateRange="custom", startdt=f"{lo:%Y-%m-%d}",
                                     enddt=f"{hi:%Y-%m-%d}", **({"from": frm} if frm else {})))
            page = r.json()["hits"]["hits"] if r is not None else []
            hits += page
            frm += len(page)
            if len(page) < 100:
                break
    return hits


def collect(start=CFG["sample"]["start"], end=CFG["sample"]["end"], get=None) -> int:
    if get is None:
        if not CFG.get("contact_email"):
            raise SystemExit("Thiếu CONTACT_EMAIL (env hoặc config/config.local.yaml) – SEC yêu cầu email trong User-Agent")
        from utils.http import Client
        get = Client(rps=8).get
    out, n = D("raw", "sec", "filings.jsonl"), 0
    done = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if out.exists() else set()
    with open(out, "a", encoding="utf-8") as f:
        for h in search(get, start, end):
            if h["_id"] in done:
                continue
            s, (adsh, name) = h["_source"], h["_id"].split(":", 1)
            cik = s["ciks"][0]
            idx = get(archive(cik, adsh, f"{adsh}-index.htm"))
            doc = get(archive(cik, adsh, name))
            f.write(json.dumps(dict(id=h["_id"], url=archive(cik, adsh, name), form=s["form"],
                                    file_date=s["file_date"], company=s["display_names"][0],
                                    accepted=str(accepted(idx.text)) if idx is not None else None,
                                    body=strip_html(doc.text)[:BODY_CHARS] if doc is not None else None),
                               ensure_ascii=False) + "\n")
            done.add(h["_id"]); n += 1
    return n


def load() -> pd.DataFrame:
    f = D("raw", "sec", "filings.jsonl")
    df = pd.read_json(f, lines=True, dtype=False) if f.exists() else pd.DataFrame(
        columns=["id", "url", "form", "file_date", "company", "accepted", "body"])
    company = df.company.astype(str).str.replace(r"\s*\(CIK.*$", "", regex=True)
    return pd.DataFrame(dict(
        source="sec", url=df.url, lang="en", title=df.form + ": " + company, body=df.body,
        published_at_utc=pd.to_datetime(df.accepted, utc=True, format="ISO8601"), first_seen_utc=pd.NaT,
        ts_source="api", file_date=pd.to_datetime(df.file_date)))


if __name__ == "__main__":
    print(collect(), "filings")
