"""Điền số liệu vào bản khuôn paper/paper.md và tạo paper/paper.filled.md.

Chạy từ gốc repo:  python paper/fill_results.py [--check] [--inplace]

Khuôn (paper.md) chứa:
  {{ten}}, {{ham(a,b)}}                      số liệu lấy từ outputs/tables (real/ + bảng đo lường thật khác)
  {{#if bieu_thuc}}A{{#else}}B{{/if}}        câu kết luận đổi theo số liệu (biểu thức Python trên các số liệu)
  [[CHỜ_DỮ_LIỆU: bang_xxx]]                  bảng dựng từ CSV; nếu chưa đủ dữ liệu thì giữ nguyên placeholder
  [[REFERENCES]]                             danh mục APA 7 dựng từ references.bib cho các trích dẫn có trong bài
Khi Codex cập nhật outputs/tables/real/, chạy lại script là số liệu, bảng và câu kết luận có điều kiện cập nhật theo.
--check: kiểm tra token chưa giải, trích dẫn ↔ bib, quy tắc "và cộng sự"/"et al.", bảng/phương trình/chú thích.
--inplace: ghi đè luôn paper.md (mất token; chỉ dùng khi chốt bản cuối).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REAL, TABLES, PROC = ROOT / "outputs" / "tables" / "real", ROOT / "outputs" / "tables", ROOT / "data" / "processed"
TEMPLATE, FILLED, BIB = ROOT / "paper" / "paper.md", ROOT / "paper" / "paper.filled.md", ROOT / "paper" / "references.bib"
ASSETS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
NARR = ["regulation", "etf_institutional", "security_hacks", "stablecoins", "defi", "ai_tokens", "macro_monetary",
        "price_speculation"]
NARR_VI = {"regulation": "Quy định pháp lý", "etf_institutional": "ETF và tổ chức", "security_hacks": "An ninh và tấn công",
           "stablecoins": "Stablecoin", "defi": "DeFi", "ai_tokens": "Token AI", "macro_monetary": "Vĩ mô và tiền tệ",
           "price_speculation": "Giá và đầu cơ", "other": "Nhóm khác"}
MINUS = "\u2212"


# ---------------------------------------------------------------- định dạng
def vn(x, d: int = 2, sign: bool = False) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    s = f"{abs(float(x)):,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    if float(x) < 0 and float(s.replace(".", "").replace(",", ".")) != 0:
        return MINUS + s
    return ("+" + s) if sign and float(x) > 0 else s


def pstr(p) -> str:
    if p is None or not math.isfinite(float(p)):
        return "—"
    return "< 0,001" if float(p) < 0.001 else vn(p, 3)


def stars(p) -> str:
    if p is None or not math.isfinite(float(p)):
        return ""
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""


def win(w: str) -> str:
    """'0_4' → '[0,4]'; 'm4_m2' không dùng, viết '-4_-2'."""
    a, b = w.split("_")
    return f"[{a},{b}]"


def read(path: Path, **kw) -> pd.DataFrame:
    return pd.read_csv(path, **kw) if path.exists() else pd.DataFrame()


# ---------------------------------------------------------------- dữ liệu
class Data:
    def __init__(self):
        self.cov, self.reg = read(REAL / "coverage.csv"), read(REAL / "regressions.csv")
        self.wald, self.quant = read(REAL / "wald.csv"), read(REAL / "quantiles.csv")
        self.evt, self.asym = read(REAL / "event_tests.csv"), read(REAL / "event_asymmetry.csv")
        self.timing, self.oos = read(REAL / "event_timing.csv"), read(REAL / "oos.csv")
        self.gr, self.gw, self.mcs = read(REAL / "granger.csv"), read(REAL / "gw.csv"), read(REAL / "mcs.csv")
        self.rob, self.robst = read(REAL / "robustness.csv"), read(REAL / "robustness_status.csv")
        self.evcov = read(REAL / "event_coverage.csv")
        self.ts, self.weak = read(TABLES / "timestamp_accuracy.csv"), read(TABLES / "sentiment_validation_weak.csv")
        self.hand = read(TABLES / "sentiment_validation.csv")
        self.cor = read(TABLES / "corpus_stats.csv")


D = Data()


def first(df: pd.DataFrame, **cond):
    m = pd.Series(True, index=df.index)
    for k, v in cond.items():
        m &= df[k].astype(str) == str(v)
    return df[m].iloc[0] if m.any() else None


def count(df, expr):
    return int(df.eval(expr).sum()) if len(df) else 0


# ---------------------------------------------------------------- số liệu và hàm tham số
def build_facts() -> tuple[dict, dict]:
    V: dict = {}
    F: dict = {}

    def put(name, value, text=None):
        V[name] = value
        F[name] = text if text is not None else (vn(value, 0) if isinstance(value, (int, np.integer)) else str(value))

    cov = D.cov
    if len(cov):
        btc = cov[cov.asset == "BTC"].iloc[0]
        put("calendar_days", int(btc.calendar_days), vn(btc.calendar_days, 0))
        put("news_days", int(btc.news_days), vn(btc.news_days, 0))
        put("pct_news_days_num", float(btc.pct_days_with_news))
        F["pct_news_days"] = vn(btc.pct_days_with_news, 1)
        for k in ("train", "valid", "test"):
            put(f"btc_{k}", int(btc[f"model_{k}_days"]), vn(btc[f"model_{k}_days"], 0))
        for r in cov.itertuples():
            put(f"pct_{r.asset.lower()}", float(r.pct_days_with_asset_news), vn(r.pct_days_with_asset_news, 1))
    ec = D.evcov
    if len(ec):
        put("n_canon_en", int(ec.canonical_en_articles.iloc[0]), vn(ec.canonical_en_articles.iloc[0], 0))
        put("n_event_rows", int(ec.article_asset_rows.iloc[0]), vn(ec.article_asset_rows.iloc[0], 0))
        put("n_event_days", int(ec.usable_event_days.iloc[0]), vn(ec.usable_event_days.iloc[0], 0))
    # đồng hồ
    ts = D.ts
    g = ts[(ts.source == "gdelt") & ts.comparison.str.startswith("published")]
    if len(g) and g.n_pairs.iloc[0] > 0:
        r = g.iloc[0]
        put("ts_pairs", int(r.n_pairs), vn(r.n_pairs, 0))
        put("ts_med_abs", float(r.median_abs_lag_min), vn(r.median_abs_lag_min, 1))
        put("ts_med_abs_round", round(float(r.median_abs_lag_min)), vn(round(float(r.median_abs_lag_min)), 0))
        put("ts_gt1h", float(r.pct_abs_gt_1h), vn(r.pct_abs_gt_1h, 1))
        put("ts_shift", float(r.pct_day_shift), vn(r.pct_day_shift, 1))
        put("ts_pub_pct", float(r.pct_published), vn(r.pct_published, 1))
        put("ts_docs", int(r.n_docs), vn(r.n_docs, 0))
    s = ts[ts.source == "sec"]
    s = s[s.comparison.str.contains("file_date")]
    if len(s):
        put("sec_pairs", int(s.n_pairs.iloc[0]), vn(s.n_pairs.iloc[0], 0))
        put("sec_shift", float(s.pct_day_shift.iloc[0]), vn(s.pct_day_shift.iloc[0], 1))
    # nhãn yếu
    w = D.weak
    if len(w):
        names = {"Loughran–McDonald": "lm", "LM": "lm", "Harvard IV-4": "hv", "FinBERT": "fb", "CryptoBERT": "cb"}
        for _, r in w.iterrows():
            k = names.get(str(r.method))
            if not k:
                continue
            put(f"auc_{k}", float(r.auc), vn(r.auc, 3))
            put(f"acc_{k}", float(r.accuracy), vn(r.accuracy, 3))
            put(f"f1_{k}", float(r.macro_f1), vn(r.macro_f1, 3))
            put(f"dec_{k}", float(r.pct_decided), vn(r.pct_decided, 0))
        put("weak_n", int(w.n.iloc[0]), vn(w.n.iloc[0], 0))
        put("weak_pos", float(w.pct_positive_labels.iloc[0]), vn(w.pct_positive_labels.iloc[0], 1))
        best = w.loc[w.auc.idxmax(), "method"]
        put("auc_best_name", str(best), str(best))
    # hồi quy dự báo
    reg = D.reg
    if len(reg):
        sig = reg[(reg.version == "text") & (reg.term == reg.sentiment) & (reg.identified == True)]  # noqa: E712
        n = int(len(sig[sig.sentiment == "sent_finbert"]))
        put("reg_n", n, vn(n, 0))
        for k, s in (("fb", "sent_finbert"), ("lm", "sent_lm"), ("hv", "sent_hv")):
            put(f"reg_{k}_sig10", int((sig[sig.sentiment == s].pvalue < .10).sum()), None)
        put("reg_exp", n * .10, vn(n * .10, 1))
        put("reg_holm_sig", int((sig.p_holm < .10).sum()), None)
        att = reg[(reg.version == "text") & (reg.sentiment == "sent_finbert") & reg.term.str.startswith("attention_")
                  & (reg.identified == True)]  # noqa: E712
        put("att_n", int(len(att)), vn(len(att), 0))
        put("att_sig10", int((att.pvalue < .10).sum()), None)
        put("att_exp", len(att) * .10, vn(len(att) * .10, 1))
        put("att_holm", int((att.p_holm < .10).sum()), None)
        top = att[att.pvalue < .10].groupby("term").size().sort_values(ascending=False)
        put("att_top", NARR_VI.get(top.index[0].replace("attention_", ""), top.index[0]) if len(top) else "—")
    # Wald, phân vị
    wd = D.wald
    if len(wd):
        put("wald_n", int(len(wd)), None)
        put("wald_sig10_raw", int((wd.pvalue < .10).sum()), None)
        put("wald_sig10_holm", int((wd.p_holm < .10).sum()), None)
    q = D.quant
    if len(q):
        put("quant_n", int(len(q)), None)
        put("quant_sig10_holm", int((q.p_holm < .10).sum()), None)
    # sự kiện
    ev = D.evt
    if len(ev):
        post = ev[(ev.grouping == "all") & ev.window.isin(["[0,1]", "[0,4]", "[0,24]"])]
        put("evt_car_post_holm", int(((post.metric == "car") & (post.p_t_holm < .10)).sum()), None)
        put("evt_vol_post_holm", int(((post.metric == "volume") & (post.p_t_holm < .10)).sum()), None)
        put("evt_any_holm", V["evt_car_post_holm"] + int(((post.metric == "absret") & (post.p_t_holm < .10)).sum()), None)
        nar = ev[(ev.grouping == "narrative") & (ev.window == "[0,4]") & ev.metric.isin(["car", "absret", "volume"])]
        put("evt_narr_holm", int((nar.p_t_holm < .10).sum()), None)
        put("evt_narr_car_holm", int(((nar.metric == "car") & (nar.p_t_holm < .10)).sum()), None)
        pre = ev[(ev.grouping == "all") & (ev.window == "[-4,-2]")]
        put("evt_pre_car_sig", int(((pre.metric == "car") & (pre.p_t_holm < .10)).sum()), None)
        put("evt_pre_other_sig", int(((pre.metric.isin(["absret", "volume"])) & (pre.p_t_holm < .10)).sum()), None)
    a = D.asym
    if len(a):
        f = a[(a.tone == "finbert_tercile") & a.window.isin(["[0,1]", "[0,4]", "[0,24]"])]
        vol = f[f.metric == "volume"]
        put("asym_vol_holm_sig", int((vol.p_t_holm < .10).sum()), None)
        sv = vol[vol.p_t_holm < .10]
        put("asym_vol_dir", float(np.sign(sv.negative_minus_positive.mean())) if len(sv) else 0.0, None)
        put("asym_price_holm_sig", int((f[f.metric.isin(["car", "absret"])].p_t_holm < .10).sum()), None)
        pre = a[(a.tone == "finbert_tercile") & (a.window == "[-4,0]") & (a.metric == "car")]
        put("asym_pre_sig", int((pre.p_t_holm < .10).sum()), None)
    tm = D.timing
    if len(tm):
        t24 = tm[tm.window == "0_24"].iloc[0]
        put("tim_pairs", int(t24.n_pairs), vn(t24.n_pairs, 0))
        put("tim_changed_holm", bool(t24.significance_changed_holm), None)
    # Granger
    gr = D.gr
    if len(gr):
        ok = gr[(gr.pvalue.notna())] if "pvalue" in gr else gr.iloc[0:0]
        put("gr_n_valid", int(len(ok)), None)
        put("gr_n_sig", int((ok.pvalue < .05).sum()), None)
        ret = ok[ok.outcome == "ret"]
        put("gr_r2s_holm", int(((ret.caused != "ret") & (ret.p_holm < .05)).sum()), None)   # lợi suất → cảm xúc
        put("gr_s2r_holm", int(((ret.caused == "ret") & (ret.p_holm < .05)).sum()), None)   # cảm xúc → lợi suất
        put("gr_s2r_raw", int(((ret.caused == "ret") & (ret.pvalue < .05)).sum()), None)
        put("gr_rv_holm", int(((ok.outcome == "rv") & (ok.p_holm < .05)).sum()), None)
    # dự báo ngoài mẫu
    o = D.oos
    if len(o):
        o = o[(o.horizon == 1) & o.target.isin(["ret", "rv"])]
        t = o[o.version == "text"].set_index(["asset", "target", "model"])
        m = o[o.version == "market"].set_index(["asset", "target", "model"])
        j = t.join(m, lsuffix="_t", rsuffix="_m", how="inner")
        better = int((j.r2_oos_ct_t > j.r2_oos_ct_m).sum())
        sig = int(((j.market_dm_pvalue_t < .10) | (j.market_cw_pvalue_t < .10)).sum())
        put("oos_n", int(len(j)), None)
        put("oos_better", better, None)
        put("oos_better_share", better / max(len(j), 1), None)
        put("oos_sig10", sig, None)
        put("oos_sig_holm", int(((j.market_dm_p_holm_t < .10) | (j.market_cw_p_holm_t < .10)).sum()), None)
        put("oos_infer_max", int(j.inference_nobs_t.max()), None)
    gw = D.gw
    if len(gw) and "gw_p_holm" in gw:
        gw = gw[gw.gw_p_holm.notna()]
        put("gw_n", int(len(gw)), None)
        put("gw_sig_holm", int((gw.gw_p_holm < .10).sum()), None)
        put("gw_nobs_min", int(gw.nobs.min()), vn(gw.nobs.min(), 0))
        put("gw_nobs_max", int(gw.nobs.max()), vn(gw.nobs.max(), 0))
    h = D.hand
    put("hand_n", int(h.n.max()) if len(h) and "n" in h else 0, None)
    # độ vững
    rb = D.rob
    if len(rb):
        r = rb[(rb.variant == "baseline") & (rb.target == "rv") & (rb.horizon == 1) & (rb.term == "sent_finbert")]
        piv = r.pivot_table(index="asset", columns="period", values="coef", aggfunc="first")
        if {"pre_2025", "post_2025"} <= set(piv.columns):
            both = piv.dropna(subset=["pre_2025", "post_2025"])
            same = int((np.sign(both.pre_2025) == np.sign(both.post_2025)).sum())
            put("rob_n", int(len(both)), None)
            put("rob_same_n", same, None)
            put("rob_same_sign", bool(len(both) and same == len(both)), None)
            put("rob_sig10", int((r.pvalue < .10).sum()), None)
    uw = read(REAL / "ucry_wald.csv")
    if len(uw):
        put("ucry_wald_sig_holm", int((uw.p_holm < .10).sum()), None)
    # fallback mặc định để biểu thức điều kiện không lỗi khi thiếu dữ liệu
    for k in ("evt_any_holm", "evt_car_post_holm", "evt_vol_post_holm", "evt_narr_holm", "evt_pre_car_sig", "asym_vol_holm_sig",
              "gr_n_valid", "oos_n", "oos_better", "oos_sig10", "oos_sig_holm", "oos_infer_max", "gw_n", "gw_sig_holm", "hand_n", "gr_r2s_holm", "gr_s2r_holm", "gr_s2r_raw", "gr_rv_holm", "rob_n", "reg_holm_sig", "att_holm", "wald_sig10_holm"):
        V.setdefault(k, 0)
        F.setdefault(k, "0")
    V.setdefault("oos_better_share", 0.0)
    V.setdefault("pct_news_days_num", 100.0)
    V.setdefault("rob_same_sign", False)
    V.setdefault("tim_changed_holm", False)
    V.setdefault("asym_vol_dir", 0.0)
    for k, v in V.items():
        F.setdefault(k, str(v))
    return V, F


def fn_evt(grouping, group, window, metric, field):
    r = first(D.evt, grouping=grouping, group=group, window=win(window), metric=metric)
    if r is None:
        return None
    x = r[field]
    return vn(x * 100 if field == "mean" and metric in ("car", "absret") else x, 3 if field == "mean" else 4) \
        if field not in ("p_t", "p_t_holm", "p_wilcoxon_holm") else pstr(x)


def fn_asym(tone, window, metric, field):
    r = first(D.asym, tone=tone, window=win(window), metric=metric)
    if r is None:
        return None
    x = r[field]
    if field.startswith("p_"):
        return pstr(x)
    return vn(x * 100 if metric in ("car", "absret") else x, 3)


def fn_timing(window, field):
    r = first(D.timing, window=window)
    if r is None:
        return None
    x = r[field]
    if field.startswith("p_"):
        return pstr(x)
    return vn(x * 100 if field.startswith("mean_car") else x, 3)


FUNCS = {"evt": fn_evt, "asym": fn_asym, "timing": fn_timing}


# ---------------------------------------------------------------- bảng
def md(rows: list[list[str]], align: str | None = None) -> str:
    head, body = rows[0], rows[1:]
    assert align is None or len(align) == len(head), (head, align)
    sep = ["---:" if (align or "l" * len(head))[i] == "r" else "---" for i in range(len(head))]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(sep) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in body]
    return "\n".join(out)


def table_mota() -> str | None:
    try:
        from src.models.panel import make_panel
        market, text = pd.read_parquet(PROC / "market_daily.parquet"), pd.read_parquet(PROC / "text_daily.parquet")
    except Exception:
        return None
    panel = make_panel(market, text, 1)
    ucry = read(PROC / "ucry_daily.parquet", engine="pyarrow") if False else (
        pd.read_parquet(PROC / "ucry_daily.parquet") if (PROC / "ucry_daily.parquet").exists() else pd.DataFrame())
    if len(ucry):
        ucry["date"] = pd.to_datetime(ucry.date, utc=True)
        panel = panel.merge(ucry[["date", "ucry_policy", "ucry_price"]], on="date", how="left")
    panel = panel[panel.sent_finbert.notna() & panel.n_docs.gt(0)].copy()
    panel["log_n"] = np.log(panel.n_docs)
    rows = [["Biến", "Số quan sát", "Trung bình", "Độ lệch chuẩn", "Nhỏ nhất", "Lớn nhất"]]

    def add(label, series, scale=1.0, d=4):
        s = series.dropna() * scale
        if len(s):
            rows.append([label, vn(len(s), 0), vn(s.mean(), d), vn(s.std(), d), vn(s.min(), d), vn(s.max(), d)])

    rows.append(["**Panel A. Biến thị trường (tài sản - ngày)**", "", "", "", "", ""])
    add("Lợi suất log ngày (%)", panel.ret, 100, 3)
    add("Biến động thực hiện RV (×10⁴)", panel.rv, 1e4, 3)
    add("Log khối lượng USD", panel.logvol, 1, 3)
    rows.append(["**Panel B. Biến văn bản (tài sản - ngày có tin)**", "", "", "", "", ""])
    add("Log số tin trong ngày", panel.log_n, 1, 3)
    add("Cảm xúc FinBERT (Sent)", panel.sent_finbert)
    add("Cảm xúc Loughran - McDonald", panel.sent_lm)
    add("Cảm xúc Harvard IV-4", panel.sent_hv)
    add("Tin xấu (NegSent)", panel.neg_sent)
    add("Tin tốt (PosSent)", panel.pos_sent)
    if "disagreement_af" in panel:
        add("Bất đồng Antweiler - Frank", panel.disagreement_af)
        add("Độ lệch chuẩn cảm xúc trong ngày", panel.disagreement_std)
    for k in NARR:
        add(f"Chú ý: {NARR_VI[k]}", panel[f"attention_{k}"])
    if "ucry_policy" in panel:
        add("UCRY Policy (chỉ số)", panel.ucry_policy, 1, 2)
        add("UCRY Price (chỉ số)", panel.ucry_price, 1, 2)
    eo = read(REAL / "event_observations.csv", usecols=["finbert_sentiment", "lm_net", "car_0_4", "absret_0_4", "volume_0_4"])
    if len(eo):
        rows.append(["**Panel C. Mẫu sự kiện theo giờ (cặp tin - tài sản)**", "", "", "", "", ""])
        add("Điểm FinBERT của tin", eo.finbert_sentiment)
        add("Điểm Loughran - McDonald của tin", eo.lm_net)
        add("CAR [0, 4] giờ (%)", eo.car_0_4, 100, 3)
        add("Độ lớn lợi suất bất thường [0, 4] giờ (%)", eo.absret_0_4, 100, 3)
        add("Khối lượng bất thường [0, 4] giờ (log)", eo.volume_0_4, 1, 3)
    return md(rows, "lrrrrr")


def table_phu() -> str | None:
    if not len(D.cov):
        return None
    try:
        from src.models.panel import make_panel
        market, text = pd.read_parquet(PROC / "market_daily.parquet"), pd.read_parquet(PROC / "text_daily.parquet")
        specific = text[(text.asset != "ALL") & text.n_docs.gt(0)][["date", "asset"]].assign(tagged=True)
        panel = make_panel(market, text, 1)
        panel = panel[panel.sent_finbert.notna() & panel.y_ret.notna()]
        panel["date"] = pd.to_datetime(panel.date, utc=True)
        specific["date"] = pd.to_datetime(specific.date, utc=True)
        panel = panel.merge(specific, on=["date", "asset"], how="left")
        fall = panel[panel.tagged.isna()].groupby("asset").size()
        tagged = specific.groupby("asset").size()
    except Exception:
        fall, tagged = pd.Series(dtype=int), pd.Series(dtype=int)
    rows = [["Tài sản", "Ngày lịch", "Ngày có tin gắn mã", "Tỷ lệ (%)", "Ngày dùng cho mô hình", "Trong đó dùng chỉ số chung", "Huấn luyện", "Kiểm tra", "Ngoài mẫu"]]
    for a in ASSETS:
        r = D.cov[D.cov.asset == a]
        if r.empty:
            continue
        r = r.iloc[0]
        n_tag = int(tagged.get(a, 0))
        total = int(r.model_train_days + r.model_valid_days + r.model_test_days)
        rows.append([a, vn(r.calendar_days, 0), vn(n_tag, 0), vn(100 * n_tag / r.calendar_days, 1), vn(total, 0),
                     vn(int(fall.get(a, 0)), 0), vn(r.model_train_days, 0), vn(r.model_valid_days, 0), vn(r.model_test_days, 0)])
    return md(rows, "lrrrrrrrr")


def table_dongho() -> str | None:
    ts = D.ts
    if not len(ts):
        return None
    rows = [["So sánh", "Số cặp", "Lệch trung vị (phút)", "Lệch tuyệt đối trung vị (phút)", "Lệch tuyệt đối P90 (phút)", "Lệch > 1 giờ (%)", "Đổi ngày (%)"]]
    for _, r in ts.iterrows():
        if not (r.n_pairs and r.n_pairs > 0):
            continue
        label = "GDELT: giờ thấy tin - giờ đăng trong trang" if r.source == "gdelt" and str(r.comparison).startswith("published") \
            else "SEC: giờ chấp nhận (UTC) - ngày nộp hồ sơ" if r.source == "sec" else None
        if not label:
            continue
        rows.append([label, vn(r.n_pairs, 0), vn(r.median_lag_min, 1), vn(r.median_abs_lag_min, 1), vn(r.p90_abs_lag_min, 1),
                     vn(r.pct_abs_gt_1h, 1), vn(r.pct_day_shift, 1)])
    return md(rows, "lrrrrrr")


def table_nhan_yeu() -> str | None:
    w = D.weak
    if not len(w):
        return None
    rows = [["Thước đo", "Số tin", "Độ chính xác", "F1 trung bình", "AUC", "Phân định (%)"]]
    order = {"Loughran–McDonald": 0, "LM": 0, "Harvard IV-4": 1, "FinBERT": 2, "CryptoBERT": 3}
    for _, r in w.sort_values("method", key=lambda s: s.map(lambda x: order.get(x, 9))).iterrows():
        rows.append([("Loughran - McDonald" if r.method in ("LM", "Loughran–McDonald") else str(r.method)), vn(r.n, 0), vn(r.accuracy, 3),
                     vn(r.macro_f1, 3), vn(r.auc, 3), vn(r.pct_decided, 1)])
    h = D.hand
    if len(h) and "accuracy" in h and (h.n.fillna(0) > 0).any():   # 300 tiêu đề gán tay → Panel B cùng bảng
        rows.insert(1, ["**Panel A. Nhãn yếu CryptoPanic**", "", "", "", "", ""])
        rows.append(["**Panel B. Nhãn thủ công**", "", "", "", "", ""])
        for _, r in h[h.n > 0].iterrows():
            rows.append([str(r.method), vn(r.n, 0), vn(r.accuracy, 3), vn(r.macro_f1, 3), vn(r.get("auc"), 3),
                         vn(r.get("pct_decided"), 1)])
    return md(rows, "lrrrrr")


def table_hoiquy() -> str | None:
    reg = D.reg
    if not len(reg):
        return None
    rows = [["Tài sản", "Loughran - McDonald", "Harvard IV-4", "FinBERT"]]
    for panel, target in (("A. Lợi suất log ngày t + 1", "ret"), ("B. Biến động thực hiện RV ngày t + 1", "rv"),
                          ("C. Log khối lượng ngày t + 1", "logvol")):
        rows.append([f"**Panel {panel}**", "", "", ""])
        for a in ASSETS:
            cells = []
            for s in ("sent_lm", "sent_hv", "sent_finbert"):
                r = first(reg, asset=a, horizon=1, target=target, version="text", sentiment=s, term=s)
                cells.append("—" if r is None or not r.identified else f"{vn(r.coef, 5)}{stars(r.pvalue)} ({vn(r.se, 5)})")
            rows.append([a, *cells])
    return md(rows, "lrrr")


def table_narrative() -> str | None:
    ev = D.evt
    if not len(ev):
        return None
    rows = [["Nhóm tin", "Cặp tin - tài sản", "Số ngày", "CAR (%)", "Độ lớn lợi suất bất thường (%)", "Khối lượng bất thường (log)", "p Holm nhỏ nhất"]]
    for grouping, group, label in [("all", "all", "Toàn bộ")] + [("narrative", k, NARR_VI[k]) for k in NARR + ["other"]]:
        cells, ps = [], []
        for m, scale in (("car", 100), ("absret", 100), ("volume", 1)):
            r = first(ev, grouping=grouping, group=group, window="[0,4]", metric=m)
            if r is None:
                cells.append("—")
                continue
            cells.append(f"{vn(r['mean'] * scale, 3)}{stars(r.p_t)}")
            ps.append(r.p_t_holm)
            n_ev, n_d = int(r.n_events), int(r.n_days)
        if not ps:
            continue
        rows.append([label, vn(n_ev, 0), vn(n_d, 0), *cells, pstr(min(ps))])
    return md(rows, "lrrrrrr")


def table_wald() -> str | None:
    w = D.wald
    if not len(w):
        return None
    rows = [["Tài sản", "Độ trễ h (ngày)", "β⁻", "β⁺", "Số quan sát", "W", "p", "p Holm"]]
    for _, r in w.sort_values(["horizon", "asset"], key=lambda s: s.map(lambda x: ASSETS.index(x) if x in ASSETS else x)).iterrows():
        rows.append([r.asset, vn(r.horizon, 0), vn(r.beta_neg, 5), vn(r.beta_pos, 5), vn(r.nobs, 0), vn(r.statistic, 3),
                     f"{pstr(r.pvalue)}{stars(r.pvalue)}", pstr(r.p_holm)])
    return md(rows, "lrrrrrrr")


def table_bat_doi_xung() -> str | None:
    a = D.asym
    if not len(a):
        return None
    rows = [["Thước đo cảm xúc", "Cửa sổ (giờ)", "Chỉ tiêu", "Số ngày", "Tin xấu", "Tin tốt", "Chênh lệch", "p Holm"]]
    lab = {"car": "CAR (%)", "absret": "Độ lớn lợi suất (%)", "volume": "Khối lượng (log)"}
    for tone, tl in (("finbert_tercile", "FinBERT"), ("lm_tone", "Loughran - McDonald")):
        for w in ("[0,1]", "[0,4]", "[0,24]"):
            for m in ("car", "absret", "volume"):
                r = first(a, tone=tone, window=w, metric=m)
                if r is None:
                    continue
                sc = 100 if m in ("car", "absret") else 1
                rows.append([tl, w, lab[m], vn(r.n_days, 0), vn(r.negative_mean * sc, 3), vn(r.positive_mean * sc, 3),
                             f"{vn(r.negative_minus_positive * sc, 3)}{stars(r.p_t)}", pstr(r.p_t_holm)])
    return md(rows, "lllrrrrr")


def table_granger_kq() -> str | None:
    g = D.gr
    if not len(g) or "pvalue" not in g:
        return None
    ok = g[g.pvalue.notna()]
    if ok.empty:
        return None
    rows = [["Tài sản", "Biến thị trường", "Chiều kiểm định", "Số quan sát", "Độ trễ", "p", "p Holm"]]
    for _, r in ok.iterrows():
        rows.append([r.asset, str(r.outcome), f"{r.get('causing', '')} → {r.get('caused', '')}", vn(r.nobs, 0),
                     vn(r.get("lag"), 0), f"{pstr(r.pvalue)}{stars(r.pvalue)}", pstr(r.get("p_holm"))])
    return md(rows, "llllrrr")


def table_do_nhay() -> str | None:
    t = D.timing
    if not len(t):
        return None
    rows = [["Cửa sổ (giờ)", "Cặp / ngày", "CAR theo giờ đăng (%)", "CAR theo giờ thấy (%)", "p Holm (giờ đăng)", "p Holm (giờ thấy)", "p Holm (chênh lệch ghép cặp)"]]
    for _, r in t.iterrows():
        a, b = str(r.window).split("_")
        rows.append([f"[{a},{b}]", f"{int(r.n_pairs)} / {int(r.n_days)}", f"{vn(r.mean_car_published * 100, 3)}{stars(r.p_public_holm)}",
                     f"{vn(r.mean_car_seen * 100, 3)}{stars(r.p_seen_holm)}", pstr(r.p_public_holm), pstr(r.p_seen_holm),
                     pstr(r.p_paired_t_holm)])
    return md(rows, "lrrrrrr")


def table_dubao() -> str | None:
    o = D.oos
    if not len(o):
        return None
    rows = [["Mô hình", "Phiên bản đặc trưng", "Số ngày", "RMSE", "R²OS", "p (DM)", "p (CW)"]]
    names = {"market": "Chỉ thị trường", "attention": "+ số tin thô", "text": "+ văn bản"}
    for panel, target in (("A. Biến động thực hiện RV ngày t + 1", "rv"), ("B. Lợi suất log ngày t + 1", "ret")):
        rows.append([f"**Panel {panel}**", "", "", "", "", "", ""])
        for model in ("EN", "XGB", "LGBM"):
            for v in ("market", "attention", "text"):
                r = first(o, asset="BTC", target=target, horizon=1, model=model, version=v)
                if r is None:
                    continue
                dm = f"{pstr(r.market_dm_pvalue)}{stars(r.market_dm_pvalue)}" if v == "text" else "—"
                cw = f"{pstr(r.market_cw_pvalue)}{stars(r.market_cw_pvalue)}" if v == "text" else "—"
                rows.append([{"EN": "Elastic Net", "XGB": "XGBoost", "LGBM": "LightGBM"}[model], names[v], vn(r.nobs, 0),
                             vn(r.rmse * (1e4 if target == "rv" else 1), 3 if target == "rv" else 5), vn(r.r2_oos_ct, 4), dm, cw])
    return md(rows, "llrrrrr")


def table_dubao_ben_vung() -> str | None:
    """Bảng GW/MCS: chỉ có khi chuỗi liên tục đủ dài (Codex xuất gw.csv/mcs.csv)."""
    gw = D.gw
    if not len(gw) or "gw_p_holm" not in gw or not gw.gw_p_holm.notna().any():
        return None
    rows = [["Tài sản", "Biến mục tiêu", "Độ trễ h", "Số quan sát", "Elastic Net", "XGBoost", "LightGBM"]]
    for (a, tg, h), g in gw.groupby(["asset", "target", "horizon"], sort=False):
        p = {r.model: f"{pstr(r.gw_p_holm)}{stars(r.gw_p_holm)}" for r in g.itertuples()}
        rows.append([a, "RV" if tg == "rv" else "Lợi suất", vn(h, 0), vn(g.nobs.max(), 0),
                     *(p.get(m, "—") for m in ("EN", "XGB", "LGBM"))])
    return md(rows, "lllrrrr")


def table_do_vung() -> str | None:
    rb = D.rob
    if not len(rb):
        return None
    r = rb[(rb.variant == "baseline") & (rb.target == "rv") & (rb.horizon == 1) & (rb.term == "sent_finbert")]
    if r.empty:
        return None
    rows = [["Tài sản", "Toàn mẫu", "Trước 2025", "Từ 2025"]]
    for a in ASSETS:
        cells = []
        for per in ("full", "pre_2025", "post_2025"):
            x = first(r, asset=a, period=per)
            cells.append("—" if x is None or not x.identified else f"{vn(x.coef, 5)}{stars(x.pvalue)} ({vn(x.se, 5)})")
        rows.append([a, *cells])
    return md(rows, "lrrr")


def table_do_vung_khac() -> str | None:
    st = D.robst
    if not len(st) or st.status.astype(str).str.startswith("pending").any():
        return None
    return None


TABLES = {"bang_mota": table_mota, "bang_phu": table_phu, "bang_dongho": table_dongho, "bang_nhan_yeu": table_nhan_yeu,
          "bang_hoiquy": table_hoiquy, "bang_narrative": table_narrative,
          "bang_wald": table_wald, "bang_bat_doi_xung": table_bat_doi_xung, "bang_granger_ket_qua": table_granger_kq,
          "bang_do_nhay": table_do_nhay, "bang_dubao": table_dubao, "bang_dubao_ben_vung": table_dubao_ben_vung,
          "bang_do_vung": table_do_vung, "bang_do_vung_khac": table_do_vung_khac}


# ---------------------------------------------------------------- bib và danh mục APA 7
ACCENT = {r"{\"u}": "ü", r"{\"U}": "Ü", r"{\'c}": "ć", r"{\v{s}}": "š", r"{\'e}": "é", r"{\"o}": "ö", r"{\"a}": "ä",
          r"{\'a}": "á", r"{\v{c}}": "č", r"{\'i}": "í", "--": "–", r"\&": "&"}


def clean(value: str) -> str:
    for a, b in ACCENT.items():
        value = value.replace(a, b)
    return re.sub(r"[{}]", "", value).strip()


def parse_bib(path: Path) -> dict[str, dict]:
    s, out, i = path.read_text(encoding="utf-8"), {}, 0
    while (m := re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(s, i)):
        kind, key, j, depth = m.group(1).lower(), m.group(2), m.end(), 1
        start = j
        while j < len(s) and depth:
            depth += {"{": 1, "}": -1}.get(s[j], 0)
            j += 1
        body, fields, k = s[start:j - 1], {}, 0
        while (f := re.compile(r"(\w+)\s*=\s*").search(body, k)):
            k = f.end()
            if body[k] == "{":
                d, e = 1, k + 1
                while d:
                    d += {"{": 1, "}": -1}.get(body[e], 0)
                    e += 1
                fields[f.group(1).lower()] = body[k + 1:e - 1]
                k = e
            else:
                e = re.compile(r"[,\n]").search(body, k).start()
                fields[f.group(1).lower()] = body[k:e].strip()
                k = e
        out[key] = {"type": kind, **fields}
        i = j
    return out


def people(entry: dict) -> list[tuple[str, str]]:
    out = []
    for a in re.split(r"\s+and\s+", entry.get("author", "")):
        last, _, given = clean(a).partition(",")
        out.append((last.strip(), given.strip()))
    return out


def initials(given: str) -> str:
    parts = []
    for tok in given.split():
        sub = [x for x in tok.split("-") if x]
        parts.append("-".join((x[0] + ".") for x in sub))
    return " ".join(parts)


def apa_authors(entry: dict) -> str:
    names = [f"{last}, {initials(g)}" for last, g in people(entry)]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + ", & " + names[-1]


def apa(entry: dict) -> str:
    year = entry.get("year", "n.d.")
    head = f"{apa_authors(entry)} ({year}). "
    title = clean(entry.get("title", ""))
    link = f"https://doi.org/{entry['doi']}" if entry.get("doi") else entry.get("url", "")
    t = entry["type"]
    if t == "article" and entry.get("journal") == "arXiv preprint":
        return f"{head}*{title}* (arXiv:{entry['eprint']}). arXiv. {link}"
    if t == "article":
        vol = f"*{clean(entry['journal'])}, {entry['volume']}*" if entry.get("volume") else f"*{clean(entry['journal'])}*"
        vol += f"({clean(entry['number'])})" if entry.get("number") else ""
        pages = clean(entry.get("pages", ""))
        pages = f"Article {pages}" if pages and "–" not in pages else pages
        return f"{head}{title}. {vol}, {pages}. {link}".replace(", . ", ". ")
    if t == "inproceedings":
        pub = f" {clean(entry['publisher'])}." if entry.get("publisher") else ""
        pp = f" (pp. {clean(entry['pages'])})" if entry.get("pages") else ""
        return f"{head}{title}. In *{clean(entry['booktitle'])}*{pp}.{pub} {link}".strip()
    if t == "book":
        return f"{head}*{title}*. {clean(entry['publisher'])}."
    if t == "misc":
        return f"{head}*{title}* [Data set]. {clean(entry.get('howpublished', ''))}. {link}"
    return f"{head}{title}. {link}"


def expected_forms(entry: dict) -> list[tuple[str, str, bool]]:
    """(chuỗi dạng 'tên', năm, là_tiếng_Anh): dạng trong câu và dạng trong ngoặc."""
    s, y = [last for last, _ in people(entry)], entry.get("year", "n.d.")
    if len(s) == 1:
        vi, en = s[0], s[0]
    elif len(s) == 2:
        vi, en = f"{s[0]} và {s[1]}", f"{s[0]} and {s[1]}"
    else:
        vi, en = f"{s[0]} và cộng sự", f"{s[0]} et al."
    out = [(vi, y, False)]
    if len(s) == 2:
        out.append((f"{s[0]} & {s[1]}", y, False))
        out.append((f"{s[0]} & {s[1]}", y, True))
    if en != vi or len(s) == 1:
        out.append((en, y, True))
    return out


def find_citations(text: str) -> list[tuple[str, str, int]]:
    found = []
    for m in re.finditer(r"\(([^()]*?(?:\d{4}|n\.d\.)[^()]*?)\)", text):
        for part in m.group(1).split(";"):
            pm = re.fullmatch(r"\s*(.+?),\s*(\d{4}[a-z]?|n\.d\.)\s*", part)
            if pm and re.match(r"[A-ZÀ-ỸĐ]", pm.group(1)) and not re.search(r"\d", pm.group(1)):
                found.append((pm.group(1), pm.group(2), m.start()))
    name = r"[A-ZÀ-ỸĐ][\w'’\-]*"
    for m in re.finditer(rf"({name}(?: (?:và|&|and) {name}(?: {name})?)?(?: và cộng sự| et al\.)?) \((\d{{4}}[a-z]?|n\.d\.)\)", text):
        found.append((m.group(1), m.group(2), m.start()))
    return found


def match_entry(name: str, year: str, bib: dict) -> str | None:
    for key, e in bib.items():
        for form, y, _ in expected_forms(e):
            if form == name and y == year:
                return key
    return None


def references(text: str, bib: dict) -> tuple[str, list[str], list[str]]:
    keys, bad = set(), []
    for name, year, pos in find_citations(text):
        k = match_entry(name, year, bib)
        (keys.add(k) if k else bad.append(f"{name} ({year})"))
    lst = sorted(keys, key=lambda k: ([ln.lower() for ln, _ in people(bib[k])], bib[k].get("year", "")))
    return "\n\n".join(apa(bib[k]) for k in lst), bad, [k for k in bib if k not in keys]


# ---------------------------------------------------------------- khuôn
def split_if(body: str) -> tuple[str, str]:
    depth = 0
    for m in re.finditer(r"\{\{#if |\{\{/if\}\}|\{\{#else\}\}", body):
        if m.group(0).startswith("{{#if"):
            depth += 1
        elif m.group(0) == "{{/if}}":
            depth -= 1
        elif depth == 0:
            return body[:m.start()], body[m.end():]
    return body, ""


def expand_ifs(text: str, V: dict, errors: list[str]) -> str:
    while (m := re.search(r"\{\{#if (.+?)\}\}", text)):
        depth, j = 1, m.end()
        for t in re.finditer(r"\{\{#if |\{\{/if\}\}", text[j:]):
            depth += 1 if t.group(0).startswith("{{#if") else -1
            if depth == 0:
                end = j + t.start()
                break
        else:
            raise ValueError("{{#if}} thiếu {{/if}}: " + m.group(1))
        a, b = split_if(text[j:end])
        try:
            ok = bool(eval(m.group(1), {"__builtins__": {}}, V))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"điều kiện '{m.group(1)}': {exc}")
            ok = False
        text = text[:m.start()] + expand_ifs(a if ok else b, V, errors) + text[end + len("{{/if}}"):]
    return text


def render(template: str, bib: dict) -> tuple[str, dict]:
    V, F = build_facts()
    errors, missing = [], []
    text = expand_ifs(template, V, errors)

    def sub(m):
        token = m.group(1).strip()
        fm = re.fullmatch(r"(\w+)\((.*)\)", token)
        if fm and fm.group(1) in FUNCS:
            val = FUNCS[fm.group(1)](*[a.strip() for a in fm.group(2).split(",")])
        else:
            val = F.get(token)
        if val is None:
            missing.append(token)
            return f"[[CHỜ_DỮ_LIỆU: {token}]]"
        return val
    text = re.sub(r"\{\{([^{}#/][^{}]*?)\}\}", sub, text)
    pending = []

    def table(m):
        key = m.group(1).strip()
        if key in TABLES:
            t = TABLES[key]()
            if t:
                return t
        pending.append(key)
        return m.group(0)
    text = re.sub(r"\[\[CHỜ_DỮ_LIỆU: (bang_\w+)\]\]", table, text)
    refs, bad, unused = references(text.replace("[[REFERENCES]]", ""), bib)
    text = text.replace("[[REFERENCES]]", refs)
    head, rest = text.split("## ABSTRACT", 1)
    abs_, tail = rest.split("## 1. ", 1)
    text = head + "## ABSTRACT" + re.sub(r"(\d),(\d)", r"\1.\2", abs_) + "## 1. " + tail
    text = text.replace("= < ", "< ")
    return text, {"errors": errors, "missing": missing, "pending": pending, "bad_cites": bad, "unused": unused, "facts": V}


# ---------------------------------------------------------------- kiểm tra
def check(template: str, filled: str, info: dict, bib: dict) -> list[str]:
    err = list(info["errors"]) + [f"token chưa giải: {t}" for t in info["missing"]]
    err += [f"trích dẫn không khớp bib hoặc sai quy tắc: {c}" for c in info["bad_cites"]]
    heads = re.findall(r"^## (.+)$", filled, flags=re.M)
    want = ["TÓM TẮT", "ABSTRACT", "1. Giới thiệu", "2. Cơ sở lý thuyết và tổng quan các nghiên cứu trước đây",
            "3. Phương pháp nghiên cứu", "4. Kết quả nghiên cứu và thảo luận", "5. Kết luận", "Tài liệu tham khảo"]
    if heads != want:
        err.append(f"cấu trúc 05 phần sai: {heads}")
    body = filled.split("## Tài liệu tham khảo")[0]
    if re.search(r"^###|^\s*[-*] ", body.split("---", 2)[-1], flags=re.M):
        err.append("có tiểu mục hoặc gạch đầu dòng trong thân bài")
    nums = re.findall(r"^\*\*Bảng (\d+)\*\*$", filled, flags=re.M)
    if nums != [str(i) for i in range(1, len(nums) + 1)]:
        err.append(f"số bảng không liên tục: {nums}")
    for n in nums:
        if not re.search(rf"[^\n*]Bảng {n}\b", filled):
            err.append(f"Bảng {n} không được nhắc trong văn bản")
    tags = re.findall(r"\\tag\{(\d+)\}", filled)
    if tags != [str(i) for i in range(1, len(tags) + 1)]:
        err.append(f"số phương trình không liên tục: {tags}")
    refs = set(re.findall(r"\[\^(\w+)\](?!:)", filled))
    defs = set(re.findall(r"^\[\^(\w+)\]:", filled, flags=re.M))
    if refs != defs:
        err.append(f"chú thích chân trang lệch: dùng {sorted(refs - defs)}, thiếu dùng {sorted(defs - refs)}")
    abstract = filled.split("## ABSTRACT")[1].split("## 1.")[0]
    rest = filled.replace(abstract, "")
    if "et al." in rest.split("## Tài liệu tham khảo")[0]:
        err.append("'et al.' ngoài ABSTRACT")
    if "và cộng sự" in abstract:
        err.append("'và cộng sự' trong ABSTRACT")
    if "synthetic" in filled.lower():
        err.append("nhắc tới synthetic")
    if re.search(r"\w+\.csv|`", body):
        err.append("tên tệp .csv hoặc ký tự ` trong thân bài")
    for k in info["unused"]:
        if k in template and f"@{k}" not in template:
            pass
    return err


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--inplace", action="store_true")
    ap.add_argument("--output", type=Path, default=FILLED)
    a = ap.parse_args()
    template, bib = TEMPLATE.read_text(encoding="utf-8"), parse_bib(BIB)
    filled, info = render(template, bib)
    out = TEMPLATE if a.inplace else a.output
    out.write_text(filled, encoding="utf-8")
    print(f"Đã ghi {out.relative_to(ROOT)}; placeholder còn lại: {sorted(set(info['pending'])) or 'không'}")
    if info["unused"]:
        print("bib chưa được trích dẫn:", ", ".join(info["unused"]))
    if a.check:
        errors = check(template, filled, info, bib)
        for e in errors:
            print("LỖI:", e)
        print("OK" if not errors else f"{len(errors)} lỗi")
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
