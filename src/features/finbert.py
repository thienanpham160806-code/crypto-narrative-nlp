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


def score(docs: pd.DataFrame, max_sentences: int = 20, batch_size: int = 32) -> pd.DataFrame:
    from transformers import pipeline
    clf = pipeline("text-classification", model=MODEL, top_k=None, truncation=True)
    prog = D("interim", "finbert_progress.csv")
    done = pd.read_csv(prog) if prog.exists() else pd.DataFrame(columns=["doc_id", "sha"])
    seen = {(r.doc_id, r.sha): r for r in done.itertuples()}
    rows = []
    for r in tqdm(docs.itertuples(), total=len(docs), desc="FinBERT"):
        sents = sentences(r.text, max_sentences)
        if not sents:
            continue
        sha = hashlib.sha256("\n".join(sents).encode("utf-8")).hexdigest()[:16]
        if (r.doc_id, sha) in seen:
            rows.append(seen[(r.doc_id, sha)]._asdict()); continue
        sc = [{d["label"]: d["score"] for d in out} for out in clf(sents, batch_size=batch_size)]
        n = len(sc)
        row = dict(doc_id=r.doc_id, sha=sha, model=MODEL,
                   positive_prob=sum(s["positive"] for s in sc) / n,
                   negative_prob=sum(s["negative"] for s in sc) / n,
                   neutral_prob=sum(s["neutral"] for s in sc) / n)
        row["sentiment"] = row["positive_prob"] - row["negative_prob"]
        rows.append(row)
        pd.DataFrame([row]).to_csv(prog, mode="a", header=not prog.exists(), index=False)
    return pd.DataFrame(rows).drop(columns=["Index"], errors="ignore")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default=str(D("interim", "documents.parquet")))
    ap.add_argument("--out", default=str(D("interim", "finbert.parquet")))
    a = ap.parse_args()
    docs = pd.read_parquet(a.inp)
    score(docs[docs.lang.eq("en")]).to_parquet(a.out, index=False)
