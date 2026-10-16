"""RQ1 – kiểm định sentiment/narrative bằng 300 tiêu đề gán tay.

sample : 300 tiêu đề en canonical ngẫu nhiên (seed), chỉ lấy tin ≤ split.valid_end (test không dùng để chọn phương pháp)
         → data/interim/validation_sample.csv, cột label_sentiment (positive|negative|neutral) và label_narrative
         (8 narrative | other) để trống cho người gán.
evaluate: so nhãn tay với LM, Harvard, FinBERT, LLM zero-shot (nếu có) → outputs/tables/sentiment_validation.csv.
          Điểm liên tục → 3 lớp: > 0 positive, < 0 negative, = 0 neutral. FinBERT: lớp xác suất lớn nhất.
Chạy: python -m features.validation sample | evaluate
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from utils.common import CFG, D, O

N = 300
FILE = D("interim", "validation_sample.csv")


def sample(docs: pd.DataFrame, n: int = N, seed: int = CFG["seed"]) -> pd.DataFrame:
    end = pd.Timestamp(CFG["split"]["valid_end"], tz="UTC") + pd.Timedelta(days=1)
    pool = docs[docs.is_canonical & docs.lang.eq("en") & docs.source.ne("sec") & (docs.public_ts_utc < end)]
    s = pool.sample(min(n, len(pool)), random_state=seed).sort_values("public_ts_utc")
    return s[["doc_id", "public_ts_utc", "source", "title"]].assign(label_sentiment="", label_narrative="")


def sign3(x: pd.Series) -> pd.Series:
    return pd.Series(np.select([x > 0, x < 0], ["positive", "negative"], "neutral"), index=x.index).where(x.notna())


def scores(y: pd.Series, p: pd.Series) -> dict:
    from sklearn.metrics import accuracy_score, f1_score
    m = y.notna() & p.notna()
    if not m.any():
        return dict(n=0, accuracy=np.nan, macro_f1=np.nan)
    return dict(n=int(m.sum()), accuracy=accuracy_score(y[m], p[m]),
                macro_f1=f1_score(y[m], p[m], average="macro", zero_division=0))


def evaluate(lab: pd.DataFrame, sc: pd.DataFrame, nar: pd.DataFrame | None = None,
             llm: pd.DataFrame | None = None) -> pd.DataFrame:
    df = lab.merge(sc, on="doc_id", how="left")
    if nar is not None:
        df = df.merge(nar[["doc_id", "zs_narr", "lda_narr", "bt_narr"]], on="doc_id", how="left")
    if llm is not None:
        df = df.merge(llm[["doc_id", "llm_narr", "llm_sent"]], on="doc_id", how="left")
    y = df.label_sentiment.replace("", np.nan).str.strip().str.lower()
    probs = df[["positive_prob", "negative_prob", "neutral_prob"]]
    fb = probs.idxmax(axis=1, skipna=True).str.replace("_prob", "").where(probs.notna().all(axis=1))
    sent = {"LM": sign3(df.lm_net), "Harvard IV-4": sign3(df.hv_net), "FinBERT": fb, "LLM zero-shot": df.get("llm_sent")}
    rows = [dict(task="sentiment", method=k, **scores(y, v)) for k, v in sent.items() if v is not None]
    yn = df.label_narrative.replace("", np.nan).str.strip().str.lower()
    narr = {"LDA": df.get("lda_narr"), "BERTopic": df.get("bt_narr"), "zero-shot embedding": df.get("zs_narr"),
            "LLM zero-shot": df.get("llm_narr")}
    rows += [dict(task="narrative", method=k, **scores(yn, v)) for k, v in narr.items() if v is not None]
    return pd.DataFrame(rows)


def main(cmd: str):
    if cmd == "sample":
        if FILE.exists():
            raise SystemExit(f"{FILE} đã có (có thể đã gán nhãn) – xóa tay nếu muốn sinh lại")
        sample(pd.read_parquet(D("interim", "documents.parquet"))).to_csv(FILE, index=False, encoding="utf-8-sig")
        print("ghi", FILE)
    else:
        lab = pd.read_csv(FILE, keep_default_na=False)
        nar = D("interim", "narratives.parquet")
        llm = None
        if CFG["nlp"]["llm"]["enabled"]:
            from features.doc_scores import llm_labels
            llm = llm_labels(lab)
        out = evaluate(lab, pd.read_parquet(D("interim", "doc_scores.parquet")),
                       pd.read_parquet(nar) if nar.exists() else None, llm)
        out.to_csv(O("tables", "sentiment_validation.csv"), index=False)
        print(out.round(3).to_string())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evaluate")
