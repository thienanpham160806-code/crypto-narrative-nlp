import pandas as pd
import pytest

from features.daily_index import NARR, build


def frames():
    ts = pd.Timestamp("2024-03-01 10:00", tz="UTC")
    urls = ["https://a.com/1", "https://www.a.com/2", "https://b.com/3"]
    docs = pd.DataFrame({"doc_id": ["d1", "d2", "d3"], "source": "gdelt", "url": urls, "lang": "en",
                         "public_ts_utc": ts, "asset_tags": [["BTC"]] * 3, "is_canonical": True})
    scores = pd.DataFrame({"doc_id": ["d1", "d2", "d3"], "finbert_sentiment": [1.0, 1.0, -1.0],
                           "positive_prob": [.9, .9, .05], "negative_prob": [.05, .05, .9], "neutral_prob": .05,
                           "lm_net": 0.0, "hv_net": 0.0,
                           "narrative": ["price_speculation", "regulation", "regulation"],
                           **{f"nprob_{k}": 1 / len(NARR) for k in NARR}})
    return docs, scores


def btc(out):
    return out[(out.asset == "BTC")].iloc[0]


def test_source_weighting_gives_each_domain_one_vote():
    docs, scores = frames()
    assert btc(build(docs, scores)).sent_finbert == pytest.approx(1 / 3)
    row = btc(build(docs, scores, "source_weighted"))
    assert row.sent_finbert == pytest.approx(0.0)          # a.com (+1) và b.com (−1) mỗi bên một phiếu
    assert row.n_docs == 3


def test_ex_price_drops_price_speculation_docs():
    docs, scores = frames()
    row = btc(build(docs, scores, "ex_price"))
    assert row.n_docs == 2 and row.attention_price_speculation == 0


def test_validation_maps_duplicate_sample_ids_to_canonical():
    from features.validation import canonical_ids
    docs = pd.DataFrame({"doc_id": ["a", "b", "c"], "dup_group": ["g1", "g1", "g2"], "is_canonical": [True, False, True]})
    assert canonical_ids(pd.Series(["b", "c", "z"]), docs).tolist() == ["a", "c", "z"]
