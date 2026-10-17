"""Điểm từng tin → data/interim/doc_scores.parquet (DATA_CONTRACT §2).

en: LM (tài chính) + Harvard IV-4 (tổng quát) + FinBERT (tin báo; SEC chỉ LM/Harvard). vi: fin_vn + crypto_vn qua VietScorer (không dịch).
Narrative = zero-shot embedding (features.narrative). LLM KHÔNG bao giờ vào feature (model biết sự kiện sau ngày
tin → rò rỉ vào test); LLM chỉ dùng ở features.validation trên tin trước split.valid_end.
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

NPROB = [f"nprob_{k}" for k in CFG["nlp"]["narratives"]]
COLS = ["doc_id", "lm_pos", "lm_neg", "lm_net", "hv_net", "finvn_net", "finbert_sentiment", "positive_prob",
        "negative_prob", "neutral_prob", "narrative", "narrative_prob", "narrative_method"] + NPROB


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


def assemble(docs: pd.DataFrame, lex: pd.DataFrame, fb: pd.DataFrame, nar: pd.DataFrame) -> pd.DataFrame:
    """Ghép điểm theo doc_id, mỗi bảng tối đa 1 dòng/tin (validate one_to_one: trùng id thì báo lỗi, không nhân bản)."""
    df = docs[["doc_id"]].merge(lex, on="doc_id", how="left", validate="one_to_one")
    df = df.merge(fb.rename(columns={"sentiment": "finbert_sentiment"})[
        ["doc_id", "finbert_sentiment", "positive_prob", "negative_prob", "neutral_prob"]], on="doc_id", how="left",
        validate="one_to_one")
    df = df.merge(nar[["doc_id", "zs_narr", "zs_prob"] + [c for c in NPROB if c in nar]], on="doc_id", how="left",
                  validate="one_to_one")
    df["narrative"], df["narrative_prob"], df["narrative_method"] = df.zs_narr, df.zs_prob, "zeroshot"
    for c in COLS:
        if c not in df:
            df[c] = np.nan
    return df[COLS]


def main():
    from features import finbert
    docs = pd.read_parquet(D("interim", "documents.parquet"))
    docs = docs[docs.is_canonical].reset_index(drop=True)
    en = docs[docs.lang.eq("en") & docs.source.ne("sec")]     # SEC: 20 câu đầu là trang bìa pháp lý → chỉ LM/Harvard
    fb = finbert.score(pd.DataFrame(dict(doc_id=en.doc_id, text=text_of(en, body_chars=20_000))))
    nar = pd.read_parquet(D("interim", "narratives.parquet"))
    out = assemble(docs, lexicon(docs), fb, nar)
    out.to_parquet(D("interim", "doc_scores.parquet"), index=False)
    print(out.describe().round(3).to_string())


if __name__ == "__main__":
    main()
