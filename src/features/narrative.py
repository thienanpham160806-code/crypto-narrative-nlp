"""Narrative cho từng tin: LDA (benchmark) → BERTopic → zero-shot (embedding ↔ mô tả 8 narrative).

Point-in-time: mọi thứ cần "fit" (vectorizer, LDA, BERTopic, ngưỡng 'other') chỉ dùng tin TRAIN
(public_ts ≤ split.train_end); riêng số topic K của LDA chọn bằng perplexity trên VALID. Test không bao giờ chạm.
Text = tiêu đề + 500 ký tự đầu thân bài (GDELT chỉ có tiêu đề); sự kiện chính nằm sâu trong thân bài có thể bị bỏ sót.
Topic của LDA/BERTopic → narrative: embedding của top-10 từ gần mô tả narrative nào nhất.
Zero-shot: cosine(embedding tin, embedding mô tả) → softmax; max cosine < quantile 20% của train → 'other'.
Model embedding đa ngữ → tin tiếng Việt dùng chung mô tả tiếng Anh (không dịch văn bản).
LDA/BERTopic chỉ trên tin báo tiếng Anh (không SEC); zero-shot cho mọi tin.
Ra: data/interim/narratives.parquet, outputs/tables/narrative_topics.csv, outputs/tables/narrative_taxonomy.csv
Chạy: python -m features.narrative
"""
from __future__ import annotations
import hashlib, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from utils.common import CFG, D, O

NARR = CFG["nlp"]["narratives"]
PROTO = {
    "regulation": "crypto regulation, SEC lawsuit against crypto firm, government ban, lawmakers pass crypto bill, "
                  "compliance and legal enforcement",
    "etf_institutional": "bitcoin ETF approval, spot ETF inflows, institutional investors, BlackRock and asset managers, "
                         "banks and corporations buy crypto",
    "security_hacks": "crypto exchange hacked, stolen funds, exploit, scam and fraud, security breach, theft of tokens",
    "stablecoins": "stablecoins such as Tether USDT and USDC, dollar peg and depeg, stablecoin issuers and reserves",
    "defi": "decentralized finance DeFi protocols, lending, decentralized exchanges, liquidity pools, staking and yield",
    "ai_tokens": "artificial intelligence crypto tokens, AI agents on blockchain, AI crypto projects",
    "macro_monetary": "Federal Reserve interest rates, inflation, monetary policy, recession, dollar and stock markets "
                      "drive crypto",
    "price_speculation": "bitcoin price rally or crash, price prediction, traders, technical analysis, bull run, "
                         "liquidations",
}
TEMP = 0.05            # nhiệt độ softmax cố định (không tune)
OTHER_Q = 0.20
K_GRID = (8, 12, 16, 20)
MAX_FIT = 50_000       # shortcut: fit LDA/BERTopic trên ≤50k tin train lấy mẫu (seed); transform toàn bộ


def text_of(df: pd.DataFrame, body_chars: int = 500) -> pd.Series:
    return (df.title.fillna("") + ". " + df.body.fillna("").str[:body_chars]).str.strip(" .")


def periods(ts: pd.Series) -> pd.Series:
    tr = pd.Timestamp(CFG["split"]["train_end"], tz="UTC") + pd.Timedelta(days=1)
    va = pd.Timestamp(CFG["split"]["valid_end"], tz="UTC") + pd.Timedelta(days=1)
    return pd.Series(np.select([ts < tr, ts < va], ["train", "valid"], "test"), index=ts.index)


def encoder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(CFG["nlp"]["embed_model"])


PREP = "title+body[:500].v1"     # đổi cách ghép text thì tăng phiên bản → cache tự vô hiệu


def text_key(text: str, model: str | None = None) -> str:
    """Khóa cache = hash(model + phiên bản tiền xử lý + text): đổi text/model không dùng lại vector cũ."""
    return hashlib.sha256(f"{model or CFG['nlp']['embed_model']}|{PREP}|{text}".encode("utf-8")).hexdigest()[:24]


def embed(texts: pd.Series, enc=None, cache=None) -> np.ndarray:
    """Embedding chuẩn hóa L2, cache theo text_key ở data/interim/embeddings.npz."""
    cache = cache or D("interim", "embeddings.npz")
    keys = texts.map(text_key)
    old = dict(np.load(cache, allow_pickle=True)) if pathlib.Path(cache).exists() else {"ids": np.array([], object)}
    pos = {d: i for i, d in enumerate(old["ids"])}
    need = keys[~keys.isin(pos)].drop_duplicates()
    if len(need):
        enc = enc or encoder()
        e = enc.encode(texts.loc[need.index].tolist(), batch_size=128, normalize_embeddings=True, show_progress_bar=True)
        e = np.asarray(e, dtype=np.float32)
        all_ids = np.concatenate([old["ids"], need.to_numpy(object)])
        all_emb = np.vstack([old["emb"], e]) if len(old["ids"]) else e
        np.savez(cache, ids=all_ids, emb=all_emb)
        pos = {d: i for i, d in enumerate(all_ids)}
        old = {"ids": all_ids, "emb": all_emb}
    return old["emb"][[pos[k] for k in keys]]


def zeroshot(emb: np.ndarray, proto: np.ndarray, train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Trả (nhãn, ma trận xác suất n×8). Xác suất dùng cho attention mềm; nhãn 'other' không đổi xác suất."""
    sim = emb @ proto.T
    p = np.exp((sim - sim.max(1, keepdims=True)) / TEMP)
    p /= p.sum(1, keepdims=True)
    lab = np.array(NARR, object)[sim.argmax(1)]
    lab[sim.max(1) < np.quantile(sim[train].max(1), OTHER_Q)] = "other"
    return lab, p


def map_topics(words: dict[int, str], enc, proto: np.ndarray) -> dict[int, str]:
    keys = list(words)
    e = np.asarray(enc.encode([words[k] for k in keys], normalize_embeddings=True))
    return {k: NARR[i] for k, i in zip(keys, (e @ proto.T).argmax(1))}


def lda(texts: pd.Series, per: pd.Series, seed: int):
    """Fit vectorizer + LDA trên train; chọn K bằng perplexity valid. Trả (topic, prob, top words, K, bảng chọn K)."""
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer
    tr = texts[per.eq("train")]
    tr = tr.sample(min(len(tr), MAX_FIT), random_state=seed)
    vec = CountVectorizer(stop_words="english", min_df=5, max_df=0.5, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b")
    Xtr, Xva = vec.fit_transform(tr), vec.transform(texts[per.eq("valid")])
    fits = {k: LatentDirichletAllocation(k, learning_method="online", random_state=seed).fit(Xtr) for k in K_GRID}
    grid = pd.DataFrame(dict(k=K_GRID, valid_perplexity=[fits[k].perplexity(Xva) if Xva.shape[0] else np.nan
                                                         for k in K_GRID]))
    k = int(grid.k[grid.valid_perplexity.idxmin()]) if grid.valid_perplexity.notna().any() else K_GRID[0]
    theta = fits[k].transform(vec.transform(texts))
    vocab = vec.get_feature_names_out()
    words = {t: " ".join(vocab[np.argsort(-c)[:10]]) for t, c in enumerate(fits[k].components_)}
    return theta.argmax(1), theta.max(1), words, k, grid


def bertopic(texts: pd.Series, emb: np.ndarray, per: pd.Series, seed: int):
    from bertopic import BERTopic
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP
    tr = np.flatnonzero(per.eq("train").to_numpy())
    tr = np.random.default_rng(seed).choice(tr, min(len(tr), MAX_FIT), replace=False)
    m = BERTopic(umap_model=UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=seed),
                 vectorizer_model=CountVectorizer(stop_words="english", min_df=5), min_topic_size=50,
                 calculate_probabilities=False)
    m.fit(texts.iloc[tr].tolist(), embeddings=emb[tr])
    # UMAP.transform có thể trả NaN (điểm trùng/cô lập) và kết quả phụ thuộc lô → giảm chiều MỘT lần, dòng NaN = -1
    # (other), dòng hữu hạn đi qua đúng các bước còn lại của BERTopic.transform 0.17 (approximate_predict + map)
    topic, prob = np.full(len(emb), -1), np.zeros(len(emb))
    if hasattr(m, "_map_predictions"):
        import hdbscan
        red = np.asarray(m.umap_model.transform(emb))
        ok = np.isfinite(red).all(1)
        if ok.any():
            t, p = hdbscan.approximate_predict(m.hdbscan_model, red[ok])
            topic[ok], prob[ok] = m._map_predictions(t), np.asarray(p, dtype=float)
    else:
        t, p = m.transform(texts.tolist(), embeddings=emb)
        topic, prob = np.asarray(t), np.asarray(p, dtype=float)
    words = {t: " ".join(w for w, _ in m.get_topic(t)[:10]) for t in m.get_topics() if t != -1}
    return np.asarray(topic), np.asarray(prob, dtype=float), words


def fill(mask: np.ndarray, vals, dtype=float) -> np.ndarray:
    a = np.full(len(mask), None if dtype is object else np.nan, dtype=dtype)
    a[mask] = vals
    return a


def run(docs: pd.DataFrame, enc=None, seed: int = CFG["seed"]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """docs: doc_id, lang, title, body, public_ts_utc (chỉ canonical). Trả (narratives theo doc, bảng topic)."""
    enc = enc or encoder()
    docs = docs.reset_index(drop=True)
    per, texts = periods(docs.public_ts_utc), text_of(docs)
    emb = embed(texts, enc)
    proto = np.asarray(enc.encode([PROTO[k] for k in NARR], normalize_embeddings=True))
    out = pd.DataFrame(dict(doc_id=docs.doc_id, period=per))
    news = docs.source.ne("sec").to_numpy()                              # SEC: văn bản pháp lý dài, lấn át topic
    out["zs_narr"], prob = zeroshot(emb, proto, per.eq("train").to_numpy() & news)
    out["zs_prob"] = prob.max(1)
    out[[f"nprob_{k}" for k in NARR]] = prob
    en = docs.lang.eq("en").to_numpy() & news
    topics = []
    t, p, words, k, grid = lda(texts[en], per[en], seed)
    names = map_topics(words, enc, proto)
    out["lda_topic"], out["lda_prob"], out["lda_narr"] = fill(en, t), fill(en, p), fill(en, [names[i] for i in t], object)
    topics += [dict(method="lda", topic=i, narrative=names[i], top_words=w, k_selected=k) for i, w in words.items()]
    grid.to_csv(O("tables", "lda_k_selection.csv"), index=False)
    t, p, words = bertopic(texts[en], emb[en], per[en], seed)
    names = {**map_topics(words, enc, proto), -1: "other"}
    out["bt_topic"], out["bt_prob"] = fill(en, t), fill(en, p)
    out["bt_narr"] = fill(en, [names.get(i, "other") for i in t], object)
    topics += [dict(method="bertopic", topic=i, narrative=names[i], top_words=w) for i, w in words.items()]
    return out, pd.DataFrame(topics)


def taxonomy(nar: pd.DataFrame) -> pd.DataFrame:
    """Bảng 2: tỷ trọng tin theo narrative × phương pháp + độ đồng thuận với zero-shot (tin báo en)."""
    en = nar[nar.lda_narr.notna()]
    rows = []
    for k in NARR + ["other"]:
        z = en.zs_narr.eq(k)
        rows.append(dict(narrative=k, **{f"share_{m}": 100 * en[f"{m}_narr"].eq(k).mean() for m in ("zs", "lda", "bt")},
                         agree_lda_with_zs=100 * en.lda_narr[z].eq(k).mean() if z.any() else np.nan,
                         agree_bt_with_zs=100 * en.bt_narr[z].eq(k).mean() if z.any() else np.nan))
    return pd.DataFrame(rows)


def main():
    docs = pd.read_parquet(D("interim", "documents.parquet"))
    nar, topics = run(docs[docs.is_canonical])
    nar.to_parquet(D("interim", "narratives.parquet"), index=False)
    topics.to_csv(O("tables", "narrative_topics.csv"), index=False)
    taxonomy(nar).to_csv(O("tables", "narrative_taxonomy.csv"), index=False)
    print(taxonomy(nar).round(1).to_string())


if __name__ == "__main__":
    main()
