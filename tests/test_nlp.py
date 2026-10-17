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
        doc_id=list("abcdefg"), lang=["en", "en", "en", "vi", "en", "en", "en"], source=["gdelt"] * 6 + ["sec"],
        title=["Bitcoin soars to record", "SEC sues exchange over losses", "ETH fine", "Bitcoin sập sàn",
               "dup of a", "Ether gains", "S-1: Bitcoin Trust"],
        body=None, is_canonical=[True, True, True, True, False, True, True],
        public_ts_utc=[UTC("2023-01-01 23:59:59"), UTC("2023-01-02 00:00"), UTC("2023-01-02 12:00"),
                       UTC("2023-01-02 13:00"), UTC("2023-01-01 10:00"), UTC("2023-01-04 01:00"),
                       UTC("2023-01-02 15:00")],
        asset_tags=[["BTC"], [], ["ETH"], ["BTC"], ["BTC"], ["ETH"], ["BTC"]]))


def test_lexicon_routes_by_language():
    lm = {"master": {"BITCOIN", "SOARS", "TO", "RECORD", "SEC", "SUES", "EXCHANGE", "OVER", "LOSSES", "ETH", "FINE",
                     "DUP", "OF", "A", "ETHER", "GAINS"}, "positive": {"SOARS", "GAINS"}, "negative": {"LOSSES"}}
    out = doc_scores.lexicon(docs_frame(), lm=lm, hv={"positive": {"RECORD"}, "negative": {"SUES"}},
                             vn={"negative": {"sập sàn"}}).set_index("doc_id")
    assert out.loc["a", "lm_net"] == 1 and out.loc["b", "lm_net"] == -1 and out.loc["b", "hv_net"] == -1
    assert out.loc["d", "finvn_net"] == -1 and np.isnan(out.loc["d", "lm_net"]) and np.isnan(out.loc["a", "finvn_net"])


def test_assemble_zeroshot_only_and_rejects_duplicate_scores():
    docs = docs_frame()
    lex = pd.DataFrame(dict(doc_id=docs.doc_id, lm_net=0.0))
    fb = pd.DataFrame(dict(doc_id=["a"], sentiment=[.5], positive_prob=[.6], negative_prob=[.1], neutral_prob=[.3]))
    nar = pd.DataFrame(dict(doc_id=docs.doc_id, zs_narr="defi", zs_prob=.4))
    out = doc_scores.assemble(docs, lex, fb, nar).set_index("doc_id")
    assert list(out.columns) == doc_scores.COLS[1:] and (out.narrative_method == "zeroshot").all()
    assert out.loc["a", "finbert_sentiment"] == .5
    with pytest.raises(pd.errors.MergeError):
        doc_scores.assemble(docs, lex, pd.concat([fb, fb]), nar)


def test_llm_labels_refuse_test_period():
    docs = pd.DataFrame(dict(doc_id=["a"], title=["x"], public_ts_utc=[UTC("2026-02-01")]))
    with pytest.raises(ValueError):
        validation.llm_labels(docs)


def test_text_daily_day_cut_canonical_en_and_accel():
    docs = docs_frame()
    fb = np.array([.5, -.8, .2, -1, .9, -.4, -1])
    sc = pd.DataFrame(dict(doc_id=docs.doc_id, finbert_sentiment=fb, lm_net=0.0, hv_net=0.0,
                           positive_prob=(fb > 0) * .8, negative_prob=(fb < 0) * .8, neutral_prob=.1,
                           narrative=["price_speculation", "regulation", "defi", "regulation", "defi", "defi",
                                      "etf_institutional"], **{f"nprob_{k}": 1 / 8 for k in narrative.NARR}))
    sc["nprob_defi"], sc["nprob_regulation"] = [.3, .1, .9, .1, .3, .9, 0], [.0, .8, .0, .8, .0, .0, 0]
    out = daily_index.build(docs, sc)
    al = out[out.asset.eq("ALL")].set_index("date")
    assert str(al.index.tz) == "UTC" and len(al) == 1369
    d1, d2 = al.loc[UTC("2023-01-01")], al.loc[UTC("2023-01-02")]
    assert d1.n_docs == 1 and d1.sent_finbert == .5                  # 23:59:59 ở lại ngày 1; bản trùng e bị loại
    assert d2.n_docs == 2 and np.isclose(d2.neg_sent, .4) and d2.attention_regulation == .5   # tin vi, SEC không vào
    assert np.isclose(d2.neg_accel, .4) and np.isnan(al.loc[UTC("2023-01-04")].neg_accel)     # 01-03 trống → NaN
    assert np.isclose(d2.disagreement_af, 1) and d1.disagreement_af == 0       # 1 dương + 1 âm → bất đồng tối đa
    assert np.isclose(d2.disagreement_std, np.std([-.8, .2], ddof=1)) and np.isnan(d1.disagreement_std)
    assert np.isclose(d2.soft_attention_defi, .5) and np.isclose(d2.soft_attention_regulation, .4)
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


def test_run_topic_models_skip_sec_and_vi(tmp_path, monkeypatch):
    monkeypatch.setattr(narrative, "D", lambda *a: tmp_path / a[-1])
    monkeypatch.setattr(narrative, "O", lambda *a: tmp_path / a[-1])
    seen = {}

    class Enc:
        def encode(self, texts, **kw):
            return np.array([np.eye(8)[hash(t) % 8] for t in texts], dtype=np.float32)

    def fake_lda(texts, per, seed):
        seen["lda"] = list(texts)
        return np.zeros(len(texts), int), np.ones(len(texts)), {0: "bitcoin"}, 8, pd.DataFrame(dict(k=[8]))
    monkeypatch.setattr(narrative, "lda", fake_lda)
    monkeypatch.setattr(narrative, "bertopic", lambda t, e, p, s: (np.zeros(len(t), int), np.ones(len(t)), {0: "x"}))
    out, topics = narrative.run(docs_frame(), enc=Enc())
    assert seen["lda"] == ["Bitcoin soars to record", "SEC sues exchange over losses", "ETH fine", "dup of a", "Ether gains"]
    assert out.set_index("doc_id").loc[["d", "g"], "lda_narr"].isna().all() and out.zs_narr.notna().all()


def test_ucry_available_day_after_week_end_and_not_stale():
    from data import news_ucry
    raw = pd.DataFrame({"Timeline": ["26/12/2022 - 01/01/2023", "02/01/2023 - 08/01/2023"],
                        "UCRY Policy Index": [100.0, 110.0], "UCRY Price Index": [90.0, 95.0]})
    out = news_ucry.daily(raw, "2023-01-01", "2023-01-20").set_index("date")
    assert np.isnan(out.loc[UTC("2023-01-01"), "ucry_policy"])                  # tuần kết thúc 01-01 → dùng từ 01-02
    assert out.loc[UTC("2023-01-02"), "ucry_policy"] == 100 and out.loc[UTC("2023-01-08"), "ucry_policy"] == 100
    assert out.loc[UTC("2023-01-09"), "ucry_price"] == 95 and out.loc[UTC("2023-01-16"), "ucry_price"] == 95
    assert np.isnan(out.loc[UTC("2023-01-17"), "ucry_price"])                    # quá 7 ngày → NaN


def test_cryptopanic_load_utc_window_and_weak_labels(tmp_path):
    from data import news_cryptopanic_ds as cp
    f = tmp_path / "cp.csv"
    f.write_text('"id","title","sourceDomain","newsDatetime","currencies","positive","negative","important"\n'
                 '"1","ETF approved","a.com","2023-05-01 10:00:00","BTC","5","0","1"\n'
                 '"2","Exchange hacked","b.com","2023-05-02 23:30:00",NULL,"0","4","0"\n'
                 '"3","Mixed","c.com","2023-05-03 00:00:00",NULL,"2","2","0"\n'
                 '"4","Old","d.com","2019-01-01 00:00:00",NULL,"9","0","0"\n', encoding="utf-8")
    df = cp.load(f)
    assert df.doc_id.tolist() == ["cp:1", "cp:2", "cp:3"] and str(df.ts_utc.dt.tz) == "UTC"
    assert df.ts_utc.iloc[1] == UTC("2023-05-02 23:30")
    w = cp.weak_labels(df)
    assert w.label.tolist() == ["positive", "negative"]


def test_weak_validation_scores_sign_auc_and_undecided():
    lab = pd.DataFrame(dict(doc_id=list("abcd"), label=["positive", "positive", "negative", "negative"]))
    sc = pd.DataFrame(dict(doc_id=list("abcd"), lm_net=[1.0, 0.0, -1.0, 0.0], finbert_sentiment=[.9, .2, -.5, -.1]))
    r = validation.weak(lab, sc).set_index("method")
    assert r.loc["LM", "accuracy"] == .5 and r.loc["LM", "pct_decided"] == 50      # điểm 0 = không chọn phía = sai
    assert r.loc["FinBERT", "accuracy"] == 1 and r.loc["FinBERT", "auc"] == 1 and "CryptoBERT" not in r.index


def test_embedding_cache_keyed_by_text_and_model(tmp_path, monkeypatch):
    calls = []

    class Enc:
        def encode(self, texts, **kw):
            calls.append(list(texts))
            return np.ones((len(texts), 3))
    cache = tmp_path / "emb.npz"
    narrative.embed(pd.Series(["a", "b", "a"]), Enc(), cache)
    narrative.embed(pd.Series(["a", "b"]), Enc(), cache)
    assert calls == [["a", "b"]]                                         # trùng text: tính 1 lần; lần 2 dùng cache
    narrative.embed(pd.Series(["a edited"]), Enc(), cache)
    monkeypatch.setitem(narrative.CFG["nlp"], "embed_model", "other-model")
    narrative.embed(pd.Series(["a"]), Enc(), cache)
    assert calls[1:] == [["a edited"], ["a"]]                            # đổi text hoặc model → tính lại


def test_finbert_cache_invalidated_by_model(tmp_path, monkeypatch):
    monkeypatch.setattr(finbert, "D", lambda *a: tmp_path / a[-1])
    n = []
    clf = lambda s, batch_size: (n.append(len(s)), [[{"label": "positive", "score": 1}, {"label": "negative", "score": 0},
                                                    {"label": "neutral", "score": 0}] for _ in s])[1]
    docs = pd.DataFrame(dict(doc_id=["a"], text=["Bitcoin rises sharply today."]))
    finbert.score(docs, clf=clf); finbert.score(docs, clf=clf)
    monkeypatch.setattr(finbert, "MODEL", "another/finbert")
    finbert.score(docs, clf=clf)
    assert n == [1, 1]


def test_bertopic_nan_reduction_rows_become_other(monkeypatch):
    class Umap:
        def transform(self, e): return np.where(np.arange(len(e))[:, None] == 2, np.nan, 0.0) * np.ones((len(e), 2))

    class Fake:
        def __init__(self, **kw): self.umap_model = Umap()
        def fit(self, docs, embeddings): pass
        def transform(self, docs, embeddings): return [0] * len(docs), [.5] * len(docs)
        def get_topics(self): return {0: []}
        def get_topic(self, t): return [("eth", .1)]
    monkeypatch.setitem(sys.modules, "bertopic", types.SimpleNamespace(BERTopic=Fake))
    monkeypatch.setitem(sys.modules, "umap", types.SimpleNamespace(UMAP=lambda **kw: None))
    t, p, _ = narrative.bertopic(pd.Series(list("abcd")), np.zeros((4, 3)), pd.Series(["train"] * 4), 0)
    assert t.tolist() == [0, 0, -1, 0] and p[2] == 0
