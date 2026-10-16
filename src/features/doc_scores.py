"""Điểm từng tin → data/interim/doc_scores.parquet (DATA_CONTRACT §2).

en: LM (tài chính) + Harvard IV-4 (tổng quát) + FinBERT. vi: fin_vn + crypto_vn qua VietScorer (không dịch).
Narrative chính = zero-shot embedding (features.narrative); LLM thay thế khi config.nlp.llm.enabled và có cache/key.
Chạy (sau features.narrative): python -m features.doc_scores
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from utils.common import CFG, D
from features.lexicon.dictionaries import load_fin_vn, load_harvard, load_lm
from features.lexicon.scoring import EnglishScorer, VietScorer, indices
from features.narrative import text_of

COLS = ["doc_id", "lm_pos", "lm_neg", "lm_net", "hv_net", "finvn_net", "finbert_sentiment", "positive_prob",
        "negative_prob", "neutral_prob", "narrative", "narrative_prob", "narrative_method"]


def lexicon(docs: pd.DataFrame, lm=None, hv=None, vn=None) -> pd.DataFrame:
    lm = lm or load_lm()
    lm_sc = EnglishScorer({k: lm[k] for k in ("positive", "negative")}, lm["master"])
    hv_sc = EnglishScorer(hv or load_harvard())
    vn_sc = VietScorer(vn or load_fin_vn())
    rows = []
    for d, lang, text in zip(docs.doc_id, docs.lang, text_of(docs, body_chars=20_000)):
        r = dict(doc_id=d)
        if lang == "en":
            n, c, _ = lm_sc.run(text)
            r |= {k: v for k, v in indices("lm", n, c).items() if k in ("lm_pos", "lm_neg", "lm_net")}
            n, c, _ = hv_sc.run(text)
            r["hv_net"] = indices("hv", n, c)["hv_net"]
        else:
            n, c, _ = vn_sc.run(text)
            r["finvn_net"] = indices("finvn", n, c)["finvn_net"]
        rows.append(r)
    return pd.DataFrame(rows)


def llm_labels(docs: pd.DataFrame) -> pd.DataFrame:
    """Nhãn LLM (chỉ khi bật); hết budget/lỗi thì dừng, giữ phần đã có."""
    from utils.llm_client import LLMClient, BudgetExceeded, LLMError
    cli, rows = LLMClient(CFG["nlp"]["llm"]), []
    for d, t in zip(docs.doc_id, docs.title):
        try:
            o = cli.classify_narrative(t)
        except (BudgetExceeded, LLMError):
            break
        rows.append(dict(doc_id=d, llm_narr=o["narrative"], llm_sent=o["sentiment"], llm_conf=o.get("confidence")))
    return pd.DataFrame(rows, columns=["doc_id", "llm_narr", "llm_sent", "llm_conf"])


def assemble(docs: pd.DataFrame, lex: pd.DataFrame, fb: pd.DataFrame, nar: pd.DataFrame,
             llm: pd.DataFrame | None = None) -> pd.DataFrame:
    df = docs[["doc_id"]].merge(lex, on="doc_id", how="left")
    df = df.merge(fb.rename(columns={"sentiment": "finbert_sentiment"})[
        ["doc_id", "finbert_sentiment", "positive_prob", "negative_prob", "neutral_prob"]], on="doc_id", how="left")
    df = df.merge(nar[["doc_id", "zs_narr", "zs_prob"]], on="doc_id", how="left")
    df["narrative"], df["narrative_prob"], df["narrative_method"] = df.zs_narr, df.zs_prob, "zeroshot"
    if llm is not None and len(llm):
        df = df.merge(llm[["doc_id", "llm_narr", "llm_conf"]], on="doc_id", how="left")
        m = df.llm_narr.notna()
        df.loc[m, ["narrative", "narrative_prob", "narrative_method"]] = \
            np.c_[df.llm_narr[m], df.llm_conf[m], np.full(m.sum(), "llm")]
    for c in COLS:
        if c not in df:
            df[c] = np.nan
    return df[COLS]


def main():
    from features import finbert
    docs = pd.read_parquet(D("interim", "documents.parquet"))
    docs = docs[docs.is_canonical].reset_index(drop=True)
    en = docs[docs.lang.eq("en")]
    fb = finbert.score(pd.DataFrame(dict(doc_id=en.doc_id, text=text_of(en, body_chars=20_000))))
    nar = pd.read_parquet(D("interim", "narratives.parquet"))
    llm = llm_labels(en) if CFG["nlp"]["llm"]["enabled"] else None
    out = assemble(docs, lexicon(docs), fb, nar, llm)
    out.to_parquet(D("interim", "doc_scores.parquet"), index=False)
    print(out.describe().round(3).to_string())


if __name__ == "__main__":
    main()
