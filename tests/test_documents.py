"""C1: thu thập + hợp nhất documents. Không cần mạng: HTTP được giả lập."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from data import news_gdelt, news_rss, news_sec, build_documents as bd

UTC = lambda s: pd.Timestamp(s, tz="UTC")


class R:
    def __init__(self, status=200, text="", content=b""):
        self.status_code, self.text, self.content = status, text, content or text.encode()

    def raise_for_status(self):
        assert self.status_code < 400

    def json(self):
        return json.loads(self.text)


def gkg_zip(rows):
    import io, zipfile
    lines = []
    for date, url, title, trans in rows:
        c = [""] * 27
        c[1], c[3], c[4], c[25], c[26] = date, "x.com", url, trans, f"<PAGE_TITLE>{title}</PAGE_TITLE>"
        lines.append(chr(9).join(c))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("f.csv", chr(10).join(lines))
    return R(200, content=buf.getvalue())


def test_gkg_filters_titles_and_caches_day(tmp_path, monkeypatch):
    monkeypatch.setattr(news_gdelt, "cache_dir", lambda lang: tmp_path)
    z = gkg_zip([("20240301100000", "https://x.com/a", "Bitcoin &amp; ETF jump", ""),
                 ("20240301100000", "https://x.com/b", "Ripple effect of rate cuts", "")])
    calls = []
    get = lambda url, **kw: (calls.append(url), z if url.endswith("10" + "0000.gkg.csv.zip") else None)[1]
    assert news_gdelt.collect("en", "2024-03-01", "2024-03-01", get=get, workers=1) == 1
    assert len(calls) == 24 and calls[0].endswith("20240301000000.gkg.csv.zip")
    assert news_gdelt.collect("en", "2024-03-01", "2024-03-01", get=get, workers=1) == 0   # cache
    df = news_gdelt.load("en")
    assert list(df.title) == ["Bitcoin & ETF jump"] and df.first_seen_utc.iloc[0] == UTC("2024-03-01 10:00")
    assert df.source.iloc[0] == "gdelt" and df.published_at_utc.isna().all()


def test_gkg_vi_keeps_only_vietnamese_rows():
    z = gkg_zip([("20240301100000", "https://v.vn/a", "Giá Bitcoin tăng mạnh", "srclc:vie;eng:GT"),
                 ("20240301100000", "https://v.vn/b", "Tiền mã hóa bị siết", "srclc:vie;eng:GT"),
                 ("20240301100000", "https://f.fr/c", "Le bitcoin monte", "srclc:fra;eng:GT")])
    assert [r["url"] for r in news_gdelt.fetch("20240301100000", "vi", lambda u, **k: z)] == ["https://v.vn/a", "https://v.vn/b"]


def test_meta_published_needs_timezone():
    assert news_gdelt.meta_published('<meta property="article:published_time" content="2024-03-01T08:00:00+07:00">') \
        == UTC("2024-03-01 01:00")
    assert news_gdelt.meta_published('"datePublished": "2024-03-01T08:00:00"') is None


RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>ETF &amp; Bitcoin</title><link>https://ct.com/a</link><description>&lt;p&gt;Sum&lt;/p&gt;</description>
<pubDate>Fri, 16 Oct 2026 14:09:00 +0700</pubDate></item></channel></rss>"""


def test_rss_parse_utc_and_summary_policy():
    now = UTC("2026-10-16 08:00")
    a = news_rss.parse("coindesk", RSS, now)[0]
    assert a["title"] == "ETF & Bitcoin" and a["body"] == "Sum" and a["published_at_utc"].startswith("2026-10-16T07:09")
    assert news_rss.parse("cointelegraph", RSS, now)[0]["body"] is None


def test_sec_accepted_is_new_york_time():
    html = '<div class="infoHead">Accepted</div>\n<div class="info">2023-01-25 18:04:15</div>'
    assert news_sec.accepted(html) == UTC("2023-01-25 23:04:15")


def test_sec_collect_uses_accepted_and_archive_urls(tmp_path, monkeypatch):
    monkeypatch.setattr(news_sec, "D", lambda *a: tmp_path / a[-1])
    hit = {"_id": "0001193125-23-015309:d1.htm", "_source": {"ciks": ["0000012345"], "form": "8-K",
           "file_date": "2023-01-26", "display_names": ["ACME Corp  (CIK 0000012345)"]}}
    pages = {news_sec.FTS: R(200, json.dumps({"hits": {"hits": [hit]}})),
             news_sec.archive("12345", "0001193125-23-015309", "0001193125-23-015309-index.htm"):
                 R(200, '<div class="infoHead">Accepted</div><div class="info">2023-01-25 18:04:15</div>'),
             news_sec.archive("12345", "0001193125-23-015309", "d1.htm"): R(200, "<p>Bitcoin treasury</p>")}
    assert news_sec.collect("2023-01-01", "2023-01-31", get=lambda u, **k: pages[u]) == 1
    df = news_sec.load()
    assert df.published_at_utc[0] == UTC("2023-01-25 23:04:15") and df.title[0] == "8-K: ACME Corp"
    assert df.url[0].endswith("/12345/000119312523015309/d1.htm") and df.body[0] == "Bitcoin treasury"


def doc(source, url, title, seen=None, pub=None, lang="en"):
    return dict(source=source, url=url, title=title, lang=lang, body=None, ts_source="x",
                first_seen_utc=UTC(seen) if seen else pd.NaT, published_at_utc=UTC(pub) if pub else pd.NaT)


def test_public_ts_min_valid():
    pub = pd.Series([UTC("2024-01-01 09:00"), UTC("2024-01-01 12:00"), UTC("2023-12-01"), pd.NaT, UTC("2024-01-05")])
    seen = pd.Series([UTC("2024-01-01 10:00"), UTC("2024-01-01 10:00"), UTC("2024-01-01"), UTC("2024-01-02"), pd.NaT])
    assert list(bd.public_ts(pub, seen)) == [UTC("2024-01-01 09:00"), UTC("2024-01-01 10:00"), UTC("2024-01-01"),
                                             UTC("2024-01-02"), UTC("2024-01-05")]


def test_build_dedup_keeps_earliest_and_does_not_chain():
    t = "Bitcoin price surges past record high as ETF inflows grow"
    df = bd.build([pd.DataFrame([
        doc("gdelt", "https://a.com/x?utm=1", t, seen="2024-01-02 10:00"),
        doc("rss:coindesk", "https://www.a.com/x", t + "!", seen="2024-01-02 12:00", pub="2024-01-02 09:30"),
        doc("gdelt", "https://b.com/y", t.replace("grow", "grows"), seen="2024-01-02 11:00"),
        doc("gdelt", "https://c.com/z", t, seen="2024-01-07 11:00"),        # quá DEDUP_DAYS → canonical mới
        doc("gdelt", "https://d.com/w", "Ethereum devs schedule Dencun upgrade on mainnet", seen="2024-01-02 13:00"),
    ])])
    canon = df[df.is_canonical]
    assert list(canon.url) == ["https://www.a.com/x", "https://d.com/w", "https://c.com/z"]
    canon_ts = df.dup_group.map(df.set_index("doc_id").public_ts_utc)
    assert df.dup_group.nunique() == 3 and (df.groupby("dup_group").public_ts_utc.transform("min") == canon_ts).all()
    assert canon.asset_tags.tolist() == [["BTC"], ["ETH"], ["BTC"]]


def test_tags_ticker_case_sensitive():
    assert bd.tag("SOL rallies; sol is sun") == ["SOL"] and bd.tag("solar panels eth zurich") == []
    assert bd.tag("Ripple wins, XRP up; Binance Coin") == ["BNB", "XRP"]


def test_timestamp_table_gdelt_vs_rss_and_sec_shift():
    df = bd.build([pd.DataFrame([doc("gdelt", "https://a.com/x", "Bitcoin ETF approved by the SEC today",
                                     seen="2024-01-10 23:30")])])
    rss = pd.DataFrame([dict(url="https://a.com/x/", published_at_utc=UTC("2024-01-10 22:30"))])
    sec = pd.DataFrame(dict(published_at_utc=[UTC("2023-01-25 23:04"), UTC("2023-01-26 15:00")],
                            file_date=pd.to_datetime(["2023-01-26", "2023-01-26"])))
    t = bd.timestamp_table(df, rss, sec).set_index("comparison")
    r = t.loc["rss pubDate vs gdelt seendate (cùng URL)"]
    assert r.n_pairs == 1 and r.median_lag_min == 60 and r.pct_abs_gt_1h == 0 and r.pct_day_shift == 0
    assert t.loc["accepted (UTC) vs file_date"].pct_day_shift == 50
