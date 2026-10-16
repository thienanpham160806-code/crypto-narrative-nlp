"""FinBERT sentiment cho từng document (tiêu đề/thân tin tiếng Anh).

Port + tổng quát hóa từ disclosure-tone-car/src/analysis/a05_finbert.py:
  • giữ: ProsusAI/finbert, chạy tiếp được nhờ cache theo sha256 đầu vào, tất định.
  • đổi: đầu vào là bảng documents (doc_id, text, lang) thay vì docs.csv của 10-K; trả xác suất pos/neg/neu.
sentiment_d = P(pos) − P(neg) ∈ [−1, 1]  (khớp mục 2.3 blueprint).
Cần: pip install transformers torch (CPU chạy được; GPU nhanh hơn nhiều).
"""
from __future__ import annotations
import argparse, hashlib, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd
from tqdm import tqdm
from utils.common import CFG, D

MODEL = CFG["nlp"]["finbert_model"]


def sentences(text: str, max_sentences: int) -> list[str]:
    s = [x for x in re.split(r"(?<=[.!?])\s+", text or "") if 3 <= len(x.split()) <= 80]
    return s[:max_sentences] or ([text] if text else [])


def score(docs: pd.DataFrame, max_sentences: int = 20, batch_size: int = 32, chunk: int = 512, clf=None) -> pd.DataFrame:
    """Gom câu của `chunk` tin vào một lần gọi model (tiêu đề tin chỉ 1 câu – gọi từng tin quá chậm)."""
    if clf is None:
        from transformers import pipeline
        clf = pipeline("text-classification", model=MODEL, top_k=None, truncation=True)
    prog = D("interim", "finbert_progress.csv")
    done = pd.read_csv(prog) if prog.exists() else pd.DataFrame(columns=["doc_id", "sha"])
    seen = {(r.doc_id, r.sha): r._asdict() for r in done.itertuples(index=False)}
    rows, todo = [], []
    for r in docs.itertuples():
        sents = sentences(r.text, max_sentences)
        if not sents:
            continue
        sha = hashlib.sha256("\n".join(sents).encode("utf-8")).hexdigest()[:16]
        if (r.doc_id, sha) in seen:
            rows.append(seen[(r.doc_id, sha)])
        else:
            todo.append((r.doc_id, sha, sents))
    for i in tqdm(range(0, len(todo), chunk), desc="FinBERT"):
        part = todo[i:i + chunk]
        flat = clf([s for *_, ss in part for s in ss], batch_size=batch_size)
        new, k = [], 0
        for doc_id, sha, ss in part:
            sc = [{d["label"]: d["score"] for d in out} for out in flat[k:k + len(ss)]]
            k += len(ss)
            row = dict(doc_id=doc_id, sha=sha, model=MODEL,
                       **{f"{c}_prob": sum(s[c] for s in sc) / len(sc) for c in ("positive", "negative", "neutral")})
            row["sentiment"] = row["positive_prob"] - row["negative_prob"]
            new.append(row)
        pd.DataFrame(new).to_csv(prog, mode="a", header=not prog.exists(), index=False)
        rows += new
    return pd.DataFrame(rows, columns=["doc_id", "sha", "model", "positive_prob", "negative_prob", "neutral_prob",
                                       "sentiment"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default=str(D("interim", "documents.parquet")))
    ap.add_argument("--out", default=str(D("interim", "finbert.parquet")))
    a = ap.parse_args()
    docs = pd.read_parquet(a.inp)
    score(docs[docs.lang.eq("en")]).to_parquet(a.out, index=False)
