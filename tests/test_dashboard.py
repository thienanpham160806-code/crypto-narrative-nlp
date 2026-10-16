"""Dashboard: thẻ tóm tắt point-in-time, helicorder, snippets, chấm Live. Không mạng, không tải model."""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import numpy as np, pandas as pd
from dashboard import export, live

UTC = lambda s: pd.Timestamp(s, tz="UTC")
NARR = export.NARR


def text_frame(days=40, last_news="2023-02-05"):
    dates = pd.date_range("2023-01-01", periods=days, freq="D", tz="UTC")
    n = np.where(dates <= UTC(last_news), 10, 0)
    df = pd.DataFrame(dict(date=dates, asset="ALL", n_docs=n, sent_finbert=np.where(n > 0, 0.2, np.nan),
                           neg_sent=np.where(n > 0, 0.1, np.nan)))
    for k in NARR:
        df[f"soft_attention_{k}"] = np.where(n > 0, 0.5 if k == "defi" else 0.5 / 7, np.nan)
    df.loc[df.date > UTC("2023-01-29"), "neg_sent"] = 0.2                  # tuần cuối có tin: tin xấu gấp đôi
    return df


def market_frame():
    dates = pd.date_range("2022-01-01", "2023-03-31", freq="D", tz="UTC")
    rv = np.linspace(1, 2, len(dates))
    rv[dates > UTC("2023-02-05")] = 100.0                                     # tương lai: không được dùng
    return pd.DataFrame(dict(date=dates, asset="BTC", close=1.0, ret=0.0, rv=rv))


def test_summary_is_point_in_time():
    s = export.summary(text_frame(), market_frame(), pd.DataFrame())
    assert s["as_of"] == "2023-02-05" and s["dominant"]["narrative"] == "defi"
    assert np.isclose(s["neg_accel"]["value"], 1.0) and np.isclose(s["sentiment"]["value"], 0.2)
    assert s["vol_risk"]["source"] == "realized" and s["vol_risk"]["value"] < 100   # không đọc RV sau as_of
    assert s["vol_risk"]["level"] == "high"                                         # RV cuối là cao nhất 365 ngày


def test_summary_prefers_forecast_up_to_as_of():
    fc = pd.DataFrame(dict(asset="BTC", target="rv", horizon=1, date=["2023-02-04", "2023-02-20"], prediction=[1.0, 50.0]))
    s = export.summary(text_frame(), market_frame(), fc)
    assert s["vol_risk"]["source"] == "forecast" and s["vol_risk"]["value"] == 1.0


def test_helicorder_and_snippets_skip_sec_and_duplicates():
    docs = pd.DataFrame(dict(doc_id=list("abcd"), source=["gdelt", "gdelt", "sec", "gdelt"], lang="en",
                             is_canonical=[True, True, True, False], title=list("ABCD"), url=list("abcd"), ts_source="x",
                             public_ts_utc=[UTC("2023-01-01 03:00"), UTC("2023-01-01 03:00"), UTC("2023-01-01 05:00"),
                                            UTC("2023-01-01 03:00")], asset_tags=[["BTC"], [], [], []]))
    sc = pd.DataFrame(dict(doc_id=list("abcd"), finbert_sentiment=[.5, -.1, 0, 0], narrative="defi", narrative_prob=.5))
    d = export.news(docs, sc)
    h = export.helicorder(d)
    assert h.counts.iloc[0][3] == 2 and sum(h.counts.iloc[0]) == 2
    s = export.snippets(d)
    assert s.doc_id.tolist() == ["a", "b"] and s.asset_tags.iloc[0] == ["BTC"]


def test_live_score_labels_without_network():
    class Enc:
        def encode(self, texts, **kw):
            return np.array([np.eye(8)[1] for _ in texts])
    clf = lambda xs, batch_size: [[{"label": "positive", "score": .6}, {"label": "negative", "score": .1},
                                   {"label": "neutral", "score": .3}] for _ in xs]
    out = live.score(pd.DataFrame(dict(title=["ETF inflows"])), clf, Enc(), np.eye(8))
    assert np.isclose(out.finbert_sentiment.iloc[0], .5) and out.narrative.iloc[0] == NARR[1]
