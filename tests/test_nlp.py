"""C2 – NLP: từ điển Việt crypto, FinBERT gom batch, narrative fit-trên-train, LLM, doc_scores, text_daily, validation.
Chạy: pytest -q (không cần mạng, không tải model)."""
import sys, types, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np, pandas as pd, pytest
from features import daily_index, doc_scores, finbert, narrative, validation
from features.lexicon.dictionaries import load_fin_vn
from features.lexicon.scoring import VietScorer
from utils.llm_client import LLMClient

UTC = lambda s: pd.Timestamp(s, tz="UTC")


def test_crypto_vn_merged_and_longest_match():
    d = load_fin_vn()
    assert "sập sàn" in d["negative"] and "thua lỗ" in d["negative"] and "khởi tố" in d["litigious"]
    _, c, w = VietScorer(d).run("Sàn bị hack, giá bitcoin sập sàn; nhà đầu tư không tăng vọt lợi nhuận")
    assert w["negative"]["sập sàn"] == 1 and c["positive"] == 0      # "tăng vọt" sau "không" bị bỏ


def test_finbert_batches_across_docs_and_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(finbert, "D", lambda *a: tmp_path / a[-1])
    calls = []

    def clf(sents, batch_size):
        calls.append(len(sents))
        return [[{"label": "positive", "score": .7}, {"label": "negative", "score": .1},
                 {"label": "neutral", "score": .2}] for _ in sents]
    docs = pd.DataFrame(dict(doc_id=["a", "b", "c"], text=["Bitcoin jumps.", "ETH falls. Traders sell coins now.", ""]))
    out = finbert.score(docs, chunk=10, clf=clf)
    assert calls == [2] and set(out.doc_id) == {"a", "b"}
    assert np.isclose(out.sentiment, .6).all()
    assert len(finbert.score(docs, chunk=10, clf=clf)) == 2 and calls == [2]        # cache, không gọi lại


def test_periods_split():
    ts = pd.Series([UTC("2025-06-30 23:59"), UTC("2025-07-01"), UTC("2025-12-31 23:00"), UTC("2026-01-01")])
    assert narrative.periods(ts).tolist() == ["train", "valid", "valid", "test"]


def test_zeroshot_other_threshold_from_train_only():
    proto = np.eye(8, 4 + 8)[:, :]
    emb = np.zeros((10, 12))
    emb[:, 0] = np.linspace(.1, 1, 10)                      # cosine với narrative 0 tăng dần
    train = np.r_[np.ones(5, bool), np.zeros(5, bool)]
    lab, p = narrative.zeroshot(emb, proto, train)
    assert lab[0] == "other" and (lab[1:] == narrative.NARR[0]).all()
    emb2 = emb.copy(); emb2[5:, 0] = 0.0                    # đổi tin test không đổi ngưỡng
    assert (narrative.zeroshot(emb2, proto, train)[0][:5] == lab[:5]).all()


def test_lda_vocab_never_sees_test_words():
    rng = np.random.default_rng(0)
    base = ["bitcoin price rally traders", "sec lawsuit regulation crypto", "stablecoin tether reserves peg",
            "defi lending protocol yield"]
    texts = pd.Series([base[i % 4] + " " + " ".join(rng.choice(["market", "coin", "news"], 2)) for i in range(120)]
                      + ["zzleakword quantumtoken " * 3] * 20)
    per = pd.Series(["train"] * 100 + ["valid"] * 20 + ["test"] * 20)
    topic, prob, words, k, grid = narrative.lda(texts, per, 0)
    assert len(topic) == 140 and k in narrative.K_GRID and grid.valid_perplexity.notna().all()
    assert not any("zzleakword" in w for w in words.values())


def test_bertopic_fits_on_train_only(monkeypatch):
    seen = {}

    class Fake:
        def __init__(self, **kw): pass
        def fit(self, docs, embeddings): seen["fit"] = list(docs)
        def transform(self, docs, embeddings): return [0] * len(docs), [.5] * len(docs)
        def get_topics(self): return {-1: [], 0: []}
        def get_topic(self, t): return [("bitcoin", .1)]
    monkeypatch.setitem(sys.modules, "bertopic", types.SimpleNamespace(BERTopic=Fake))
    monkeypatch.setitem(sys.modules, "umap", types.SimpleNamespace(UMAP=lambda **kw: None))
    texts = pd.Series(["tr1", "tr2", "va", "te"])
    t, p, words = narrative.bertopic(texts, np.zeros((4, 3)), pd.Series(["train", "train", "valid", "test"]), 0)
    assert sorted(seen["fit"]) == ["tr1", "tr2"] and len(t) == 4 and words == {0: "bitcoin"}


def test_llm_classify_narrative_cached(tmp_path):
    n = []

    def backend(model, prompt, schema, max_tokens):
        n.append(prompt)
        return '{"narrative": "ufo", "sentiment": "negative", "confidence": 0.9}', {}
    cli = LLMClient(dict(provider="x", model_x="m", max_total_calls=5, requests_per_minute=1e9),
                    cache_dir=tmp_path, backends={"x": backend}, sleep=lambda s: None)
    o = cli.classify_narrative("Exchange hacked, $100m stolen")
    assert o["narrative"] == "other" and o["sentiment"] == "negative"
    assert cli.classify_narrative("Exchange hacked, $100m stolen")["cached"] and len(n) == 1


def docs_frame():
    return pd.DataFrame(dict(
        doc_id=list("abcdef"), lang=["en", "en", "en", "vi", "en", "en"], source="gdelt",
        title=["Bitcoin soars to record", "SEC sues exchange over losses", "ETH fine", "Bitcoin sập sàn",
               "dup of a", "Ether gains"],
        body=None, is_canonical=[True, True, True, True, False, True],
        public_ts_utc=[UTC("2023-01-01 23:59:59"), UTC("2023-01-02 00:00"), UTC("2023-01-02 12:00"),
                       UTC("2023-01-02 13:00"), UTC("2023-01-01 10:00"), UTC("2023-01-04 01:00")],
        asset_tags=[["BTC"], [], ["ETH"], ["BTC"], ["BTC"], ["ETH"]]))


def test_lexicon_routes_by_language():
    lm = {"master": {"BITCOIN", "SOARS", "TO", "RECORD", "SEC", "SUES", "EXCHANGE", "OVER", "LOSSES", "ETH", "FINE",
                     "DUP", "OF", "A", "ETHER", "GAINS"}, "positive": {"SOARS", "GAINS"}, "negative": {"LOSSES"}}
    out = doc_scores.lexicon(docs_frame(), lm=lm, hv={"positive": {"RECORD"}, "negative": {"SUES"}},
                             vn={"negative": {"sập sàn"}}).set_index("doc_id")
    assert out.loc["a", "lm_net"] == 1 and out.loc["b", "lm_net"] == -1 and out.loc["b", "hv_net"] == -1
    assert out.loc["d", "finvn_net"] == -1 and np.isnan(out.loc["d", "lm_net"]) and np.isnan(out.loc["a", "finvn_net"])


def test_assemble_llm_overrides_zeroshot():
    docs = docs_frame()
    lex = pd.DataFrame(dict(doc_id=docs.doc_id, lm_net=0.0))
    fb = pd.DataFrame(dict(doc_id=["a"], sentiment=[.5], positive_prob=[.6], negative_prob=[.1], neutral_prob=[.3]))
    nar = pd.DataFrame(dict(doc_id=docs.doc_id, zs_narr="defi", zs_prob=.4))
    llm = pd.DataFrame(dict(doc_id=["b"], llm_narr=["regulation"], llm_conf=[.9]))
    out = doc_scores.assemble(docs, lex, fb, nar, llm).set_index("doc_id")
    assert list(out.columns) == doc_scores.COLS[1:]
    assert out.loc["b", "narrative"] == "regulation" and out.loc["b", "narrative_method"] == "llm"
    assert out.loc["a", "narrative_method"] == "zeroshot" and out.loc["a", "finbert_sentiment"] == .5


def test_text_daily_day_cut_canonical_en_and_accel():
    docs = docs_frame()
    sc = pd.DataFrame(dict(doc_id=docs.doc_id, finbert_sentiment=[.5, -.8, .2, -1, .9, -.4], lm_net=0.0, hv_net=0.0,
                           narrative=["price_speculation", "regulation", "defi", "regulation", "defi", "defi"]))
    out = daily_index.build(docs, sc)
    al = out[out.asset.eq("ALL")].set_index("date")
    assert str(al.index.tz) == "UTC" and len(al) == 1369
    d1, d2 = al.loc[UTC("2023-01-01")], al.loc[UTC("2023-01-02")]
    assert d1.n_docs == 1 and d1.sent_finbert == .5                  # 23:59:59 ở lại ngày 1; bản trùng e bị loại
    assert d2.n_docs == 2 and np.isclose(d2.neg_sent, .4) and d2.attention_regulation == .5   # tin vi không vào
    assert np.isclose(d2.neg_accel, .4) and np.isnan(al.loc[UTC("2023-01-04")].neg_accel)     # 01-03 trống → NaN
    btc = out[out.asset.eq("BTC")]
    assert btc.date.tolist() == [UTC("2023-01-01")]                  # mã: chỉ ngày có tin


def test_validation_sample_excludes_test_and_scores():
    docs = pd.DataFrame(dict(doc_id=[f"d{i}" for i in range(10)], lang="en", source="gdelt", is_canonical=True,
                             title="t", public_ts_utc=[UTC("2025-01-01")] * 5 + [UTC("2026-03-01")] * 5))
    s = validation.sample(docs, n=300)
    assert len(s) == 5 and (s.public_ts_utc < UTC("2026-01-01")).all() and (s.label_sentiment == "").all()
    lab = pd.DataFrame(dict(doc_id=["a", "b", "c"], label_sentiment=["positive", "negative", ""],
                            label_narrative=["defi", "", ""]))
    sc = pd.DataFrame(dict(doc_id=["a", "b", "c"], lm_net=[.5, .5, 0], hv_net=[1, -1, 0],
                           positive_prob=[.8, .1, .3], negative_prob=[.1, .8, .3], neutral_prob=[.1, .1, .4]))
    nar = pd.DataFrame(dict(doc_id=["a", "b", "c"], zs_narr="defi", lda_narr="defi", bt_narr="other"))
    r = validation.evaluate(lab, sc, nar).set_index(["task", "method"])
    assert r.loc[("sentiment", "LM"), "accuracy"] == .5 and r.loc[("sentiment", "FinBERT"), "accuracy"] == 1
    assert r.loc[("sentiment", "FinBERT"), "n"] == 2 and r.loc[("narrative", "BERTopic"), "accuracy"] == 0
