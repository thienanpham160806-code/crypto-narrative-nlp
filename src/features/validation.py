"""RQ1 – kiểm định sentiment/narrative bằng 300 tiêu đề gán tay.

sample : 300 tiêu đề en canonical ngẫu nhiên (seed), chỉ lấy tin ≤ split.valid_end (test không dùng để chọn phương pháp)
         → data/interim/validation_sample.csv, cột label_sentiment (positive|negative|neutral) và label_narrative
         (8 narrative | other) để trống cho người gán.
evaluate: so nhãn tay với LM, Harvard, FinBERT, LLM zero-shot (nếu có) và baseline đa số → outputs/tables/
          sentiment_validation.csv (KTC bootstrap 1.999 lần theo tiêu đề), sentiment_confusion.csv,
          sentiment_auc_delong.csv (DeLong FinBERT vs LM/HV), validation_label_counts.csv.
          Điểm liên tục → 3 lớp: > 0 positive, < 0 negative, = 0 neutral. FinBERT: lớp xác suất lớn nhất.
Chạy: python -m features.validation sample | evaluate | weak (nhãn yếu CryptoPanic, + CryptoBERT, AUC)
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


def llm_labels(docs: pd.DataFrame) -> pd.DataFrame:
    """Nhãn LLM zero-shot CHỈ cho validation. Từ chối tin sau split.valid_end: LLM có thể "biết" sự kiện sau ngày tin."""
    from utils.llm_client import LLMClient, BudgetExceeded, LLMError
    end = pd.Timestamp(CFG["split"]["valid_end"], tz="UTC") + pd.Timedelta(days=1)
    ts = pd.to_datetime(docs.public_ts_utc, utc=True)
    if (ts >= end).any() or ts.isna().any():
        raise ValueError("LLM chỉ được gán nhãn tin trước split.valid_end (có public_ts_utc)")
    cli, rows = LLMClient(CFG["nlp"]["llm"]), []
    for d, t in zip(docs.doc_id, docs.title):
        try:
            o = cli.classify_narrative(t)
        except (BudgetExceeded, LLMError):
            break
        rows.append(dict(doc_id=d, llm_narr=o["narrative"], llm_sent=o["sentiment"], llm_conf=o.get("confidence")))
    return pd.DataFrame(rows, columns=["doc_id", "llm_narr", "llm_sent", "llm_conf"])


def auc(y: pd.Series, s: pd.Series) -> float:
    """AUC positive vs negative trên điểm liên tục (bỏ nhãn neutral); không phụ thuộc mất cân bằng lớp."""
    from sklearn.metrics import roc_auc_score
    m = y.isin(["positive", "negative"]) & s.notna()
    return roc_auc_score(y[m].eq("positive"), s[m]) if y[m].nunique() == 2 else np.nan


def bull_bear(texts: list[str], clf=None) -> np.ndarray:
    """CryptoBERT (ElKulako/cryptobert, MIT): P(Bullish) − P(Bearish). Chỉ dùng trong validation."""
    if clf is None:
        from transformers import pipeline
        clf = pipeline("text-classification", model=CFG["nlp"]["cryptobert_model"], top_k=None, truncation=True,
                       max_length=128)
    out = [{d["label"]: d["score"] for d in o} for o in clf(texts, batch_size=32)]
    return np.array([o.get("Bullish", 0) - o.get("Bearish", 0) for o in out])


def weak(lab: pd.DataFrame, sc: pd.DataFrame) -> pd.DataFrame:
    """Nhãn yếu CryptoPanic (positive/negative): dự đoán = dấu của điểm; điểm 0 tính là sai (không chọn phía)."""
    df = lab[["doc_id", "label"]].merge(sc, on="doc_id", how="left")
    methods = {"LM": "lm_net", "Harvard IV-4": "hv_net", "FinBERT": "finbert_sentiment", "CryptoBERT": "cryptobert_sentiment"}
    rows = []
    for name, col in methods.items():
        if col not in df:
            continue
        s = df[col]
        pred = pd.Series(np.select([s > 0, s < 0], ["positive", "negative"], "neutral"), index=df.index).where(s.notna())
        rows.append(dict(task="sentiment (weak, CryptoPanic votes)", method=name, **scores(df.label, pred),
                         auc=auc(df.label, s), pct_decided=100 * (s.fillna(0) != 0).mean(),
                         pct_positive_labels=100 * df.label.eq("positive").mean()))
    return pd.DataFrame(rows)


def canonical_ids(ids: pd.Series, docs: pd.DataFrame) -> pd.Series:
    """Tin trong mẫu có thể thành bản trùng sau khi rebuild kho (chỉ bản canonical được chấm) → lấy điểm của bản
    canonical cùng dup_group; cùng một tin nên nhãn người vẫn đúng."""
    canon = docs[docs.is_canonical].set_index("dup_group").doc_id
    group = docs.set_index("doc_id").dup_group
    return ids.map(lambda d: canon.get(group.get(d), d))


def predictions(lab: pd.DataFrame, sc: pd.DataFrame, nar: pd.DataFrame | None = None,
                llm: pd.DataFrame | None = None) -> tuple:
    """Nhãn tay và dự đoán của từng phương pháp, cùng chỉ số dòng (một dòng = một tiêu đề)."""
    df = lab.merge(sc, on="doc_id", how="left")
    if nar is not None:
        df = df.merge(nar[["doc_id", "zs_narr", "lda_narr", "bt_narr"]], on="doc_id", how="left")
    if llm is not None:
        df = df.merge(llm[["doc_id", "llm_narr", "llm_sent"]], on="doc_id", how="left")
    y = df.label_sentiment.replace("", np.nan).str.strip().str.lower()
    probs = df[["positive_prob", "negative_prob", "neutral_prob"]]
    fb = probs.fillna(-1).idxmax(axis=1).str.replace("_prob", "").where(probs.notna().all(axis=1))
    sent = {k: v for k, v in {"LM": sign3(df.lm_net), "Harvard IV-4": sign3(df.hv_net), "FinBERT": fb,
                              "LLM zero-shot": df.get("llm_sent")}.items() if v is not None}
    sent["Baseline: luôn neutral"] = pd.Series("neutral", index=df.index).where(y.notna())
    cont = {"LM": df.lm_net, "Harvard IV-4": df.hv_net, "FinBERT": df.positive_prob - df.negative_prob}
    yn = df.label_narrative.replace("", np.nan).str.strip().str.lower()
    narr = {k: v for k, v in {"LDA": df.get("lda_narr"), "BERTopic": df.get("bt_narr"),
                              "zero-shot embedding": df.get("zs_narr"), "LLM zero-shot": df.get("llm_narr")}.items()
            if v is not None}
    narr["Baseline: luôn other"] = pd.Series("other", index=df.index).where(yn.notna())
    return y, sent, cont, yn, narr


def fast_metrics(y: np.ndarray, p: np.ndarray, classes: list[str]) -> tuple[float, float]:
    """Accuracy và macro-F1 (trên tập lớp cố định) — đủ nhanh cho bootstrap."""
    acc = float((y == p).mean())
    f1 = []
    for c in classes:
        tp = np.sum((y == c) & (p == c))
        fp, fn = np.sum((y != c) & (p == c)), np.sum((y == c) & (p != c))
        f1.append(2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.0)
    return acc, float(np.mean(f1))


def fast_auc(pos: np.ndarray, s: np.ndarray) -> float:
    """AUC = Mann–Whitney (hạng trung bình cho giá trị trùng)."""
    n1, n0 = pos.sum(), (~pos).sum()
    if not n1 or not n0:
        return np.nan
    r = pd.Series(s).rank().to_numpy()
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def bootstrap(y: pd.Series, p: pd.Series, s: pd.Series | None, n_boot: int, seed: int) -> dict:
    """KTC 95% phân vị, lấy mẫu lại theo tiêu đề (n_boot lần) cho accuracy, macro-F1 và AUC."""
    m = y.notna() & p.notna()
    yy, pp = y[m].to_numpy(), p[m].to_numpy()
    ss = s[m].to_numpy(dtype=float) if s is not None else None
    classes = sorted(set(yy) | set(pp))
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_boot):
        i = rng.integers(0, len(yy), len(yy))
        acc, f1 = fast_metrics(yy[i], pp[i], classes)
        a = np.nan
        if ss is not None:
            keep = np.isin(yy[i], ["positive", "negative"]) & ~np.isnan(ss[i])
            a = fast_auc(yy[i][keep] == "positive", ss[i][keep])
        out.append((acc, f1, a))
    arr = np.array(out, dtype=float)
    q = np.percentile(arr[:, :2], [2.5, 97.5], axis=0)
    ci = dict(accuracy_lo=q[0, 0], accuracy_hi=q[1, 0], macro_f1_lo=q[0, 1], macro_f1_hi=q[1, 1])
    if ss is not None:
        lo, hi = np.nanpercentile(arr[:, 2], [2.5, 97.5])
        ci.update(auc_lo=lo, auc_hi=hi)
    return ci


def evaluate(lab: pd.DataFrame, sc: pd.DataFrame, nar: pd.DataFrame | None = None,
             llm: pd.DataFrame | None = None, n_boot: int = 0, seed: int = CFG["seed"]) -> pd.DataFrame:
    """Accuracy, macro-F1, AUC (+ KTC bootstrap nếu n_boot > 0) cho mọi phương pháp và baseline đa số."""
    y, sent, cont, yn, narr = predictions(lab, sc, nar, llm)
    pct_pos = 100 * y.eq("positive").sum() / max(y.notna().sum(), 1)
    rows = []
    for task, truth, preds in (("sentiment", y, sent), ("narrative", yn, narr)):
        for k, v in preds.items():
            r = dict(task=task, method=k, **scores(truth, v))
            if task == "sentiment":
                r.update(auc=auc(truth, cont[k]) if k in cont else np.nan, pct_positive_labels=pct_pos)
            if n_boot:
                r.update(bootstrap(truth, v, cont.get(k) if task == "sentiment" else None, n_boot, seed))
            rows.append(r)
    return pd.DataFrame(rows)


def confusion(lab: pd.DataFrame, sc: pd.DataFrame) -> pd.DataFrame:
    """Ma trận nhầm lẫn 3 lớp (nhãn tay × dự đoán) cho từng thước đo cảm xúc, dạng dài."""
    y, sent, _, _, _ = predictions(lab, sc)
    classes = ["negative", "neutral", "positive"]
    rows = []
    for k, p in sent.items():
        m = y.notna() & p.notna()
        ct = pd.crosstab(y[m], p[m]).reindex(index=classes, columns=classes, fill_value=0)
        rows += [dict(method=k, label=t, predicted=c, n=int(ct.loc[t, c])) for t in classes for c in classes]
    return pd.DataFrame(rows)


def delong(pos: np.ndarray, a: np.ndarray, b: np.ndarray) -> dict:
    """Kiểm định DeLong cho hai AUC có cặp (cùng tiêu đề): H0 AUC_a = AUC_b."""
    from scipy.stats import norm

    def parts(s):
        x, z = s[pos], s[~pos]
        v10 = ((x[:, None] > z[None, :]) + 0.5 * (x[:, None] == z[None, :])).mean(1)
        v01 = ((x[:, None] > z[None, :]) + 0.5 * (x[:, None] == z[None, :])).mean(0)
        return v10.mean(), v10, v01

    auc_a, a10, a01 = parts(a)
    auc_b, b10, b01 = parts(b)
    s10, s01 = np.cov(np.vstack([a10, b10])), np.cov(np.vstack([a01, b01]))
    var = (s10[0, 0] + s10[1, 1] - 2 * s10[0, 1]) / len(a10) + (s01[0, 0] + s01[1, 1] - 2 * s01[0, 1]) / len(a01)
    z = (auc_a - auc_b) / np.sqrt(var) if var > 0 else np.nan
    return dict(auc_a=auc_a, auc_b=auc_b, diff=auc_a - auc_b, z=z, pvalue=2 * norm.sf(abs(z)) if var > 0 else np.nan)


def auc_tests(lab: pd.DataFrame, sc: pd.DataFrame) -> pd.DataFrame:
    """FinBERT so với LM và Harvard IV-4 trên các tiêu đề gán tích cực/tiêu cực (bỏ trung tính)."""
    y, _, cont, _, _ = predictions(lab, sc)
    m = y.isin(["positive", "negative"]) & pd.concat(cont, axis=1).notna().all(axis=1)
    pos = y[m].eq("positive").to_numpy()
    rows = [dict(method_a="FinBERT", method_b=b, n_pos=int(pos.sum()), n_neg=int((~pos).sum()),
                 **delong(pos, cont["FinBERT"][m].to_numpy(float), cont[b][m].to_numpy(float)))
            for b in ("LM", "Harvard IV-4")]
    return pd.DataFrame(rows)


def label_counts(lab: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for task, col in (("sentiment", "label_sentiment"), ("narrative", "label_narrative")):
        v = lab[col].replace("", np.nan).dropna().str.strip().str.lower()
        rows += [dict(task=task, label=k, n=int(n), pct=100 * n / len(v)) for k, n in v.value_counts().items()]
    return pd.DataFrame(rows)


def main(cmd: str):
    if cmd == "sample":
        if FILE.exists():
            raise SystemExit(f"{FILE} đã có (có thể đã gán nhãn) – xóa tay nếu muốn sinh lại")
        sample(pd.read_parquet(D("interim", "documents.parquet"))).to_csv(FILE, index=False, encoding="utf-8-sig")
        print("ghi", FILE)
    elif cmd == "weak":
        from data import news_cryptopanic_ds as cp
        from features import finbert
        from features.doc_scores import lexicon
        lab = cp.weak_labels(cp.load(cp.download()))
        sc = lexicon(lab.assign(lang="en", body=None))
        fb = finbert.score(pd.DataFrame(dict(doc_id=lab.doc_id, text=lab.title)))
        sc = sc.merge(fb[["doc_id", "sentiment"]].rename(columns={"sentiment": "finbert_sentiment"}), on="doc_id", how="left")
        sc["cryptobert_sentiment"] = bull_bear(lab.title.tolist())
        out = weak(lab, sc)
        out.to_csv(O("tables", "sentiment_validation_weak.csv"), index=False)
        print(out.round(3).to_string())
    else:
        lab = pd.read_csv(FILE, keep_default_na=False)
        lab["doc_id"] = canonical_ids(lab.doc_id, pd.read_parquet(D("interim", "documents.parquet")))
        nar = D("interim", "narratives.parquet")
        llm = None
        if CFG["nlp"]["llm"]["enabled"]:
            llm = llm_labels(lab)
        sc = pd.read_parquet(D("interim", "doc_scores.parquet"))
        out = evaluate(lab, sc, pd.read_parquet(nar) if nar.exists() else None, llm, n_boot=1999)
        out.to_csv(O("tables", "sentiment_validation.csv"), index=False)
        confusion(lab, sc).to_csv(O("tables", "sentiment_confusion.csv"), index=False)
        tests = auc_tests(lab, sc)
        tests.to_csv(O("tables", "sentiment_auc_delong.csv"), index=False)
        label_counts(lab).to_csv(O("tables", "validation_label_counts.csv"), index=False)
        print(out.round(3).to_string())
        print(tests.round(4).to_string())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evaluate")
