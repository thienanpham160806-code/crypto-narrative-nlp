"""Crypto event study on a continuous UTC calendar, including weekends.

T=0: bar bắt đầu đầu tiên SAU public_ts_utc. Cửa sổ đo bằng số bar.
Hai thước đo lợi suất bất thường (kết quả chính + đối chứng):
  • CAR theo market model  – ước lượng [-150,-11], ≥80 phiên có giao dịch (MacKinlay 1997)
  • BHAR[0,3] = Π(1+R_i) − Π(1+R_m) – đúng định nghĩa "excess return" của LM (2011), theo lm2011-replication
Placebo: dời T=0 về −60 phiên. Đường CAAR [-10,+10] lưu để vẽ hình theo nhóm tone.
Biến kiểm soát từ giá: beta, pre_alpha (hệ số chặn [-252,-6], thay FF-alpha của LM), pre_ret CAR[-30,-2],
  log_tradeval (GTGD bình quân 60 phiên), turnover (Mỹ: KL/số CP lưu hành), log_mcap, bm (Mỹ, từ XBRL).
Kiểm định CAR ≠ 0: t, BMP (Boehmer–Musumeci–Poulsen 1991), Wilcoxon, sign test.
"""
import argparse
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
from src.utils.common import CFG, K

E = CFG["event"]


def mm_fit(y, x):
    ok = y.notna() & x.notna()
    if ok.sum() < E["min_est_obs"]:
        return None
    m = sm.OLS(y[ok], sm.add_constant(x[ok])).fit()
    return m.params.iloc[0], m.params.iloc[1], np.sqrt(m.scale)


def event_row(r, rm, i0):
    a, b = E["est_window"]
    if i0 + min(a, min(w[0] for w in E['windows'])) < 0 or i0 + max(w[1] for w in E["windows"]) >= len(r):
        return None
    fit = mm_fit(r.iloc[i0 + a:i0 + b + 1], rm.iloc[i0 + a:i0 + b + 1])
    if fit is None:
        return None
    al, be, sig = fit
    out = dict(alpha=al, beta=be, sigma=sig, zero_ret_share=float((r.iloc[i0 + a:i0 + b + 1] == 0).mean()))
    for lo, hi in E["windows"]:
        w = slice(i0 + lo, i0 + hi + 1)
        ar = r.iloc[w] - (al + be * rm.iloc[w])
        if ar.isna().any():
            continue
        out[K("car", lo, hi)] = ar.sum()
        out[K("scar", lo, hi)] = ar.sum() / (sig * np.sqrt(hi - lo + 1)) if sig > 0 else np.nan
        out[K("carma", lo, hi)] = (r.iloc[w] - rm.iloc[w]).sum()
    lo, hi = E["main_window"]; w = slice(i0 + lo, i0 + hi + 1)
    if r.iloc[w].notna().all() and rm.iloc[w].notna().all():
        out[K("bhar", lo, hi)] = np.prod(1 + r.iloc[w]) - np.prod(1 + rm.iloc[w])
    pre = slice(max(0, i0 - 30), i0 - 1)
    out["pre_ret"] = (r.iloc[pre] - rm.iloc[pre]).sum()
    pf = mm_fit(r.iloc[max(0, i0 - 252):i0 - 5], rm.iloc[max(0, i0 - 252):i0 - 5])
    out["pre_alpha"] = pf[0] if pf else np.nan
    p0, p1 = E["caar_path"]
    if i0 + p0 >= 0 and i0 + p1 < len(r):
        wp = slice(i0 + p0, i0 + p1 + 1)
        out["_path"] = (r.iloc[wp] - (al + be * rm.iloc[wp])).to_numpy()
    return out


def tests(x, label):
    x = pd.Series(x).dropna()
    if len(x) < 5:
        return None
    return dict(window=label, N=len(x), mean_pct=100 * x.mean(), median_pct=100 * x.median(),
                t=stats.ttest_1samp(x, 0).statistic, p_t=stats.ttest_1samp(x, 0).pvalue,
                p_wilcoxon=stats.wilcoxon(x).pvalue if (x != 0).any() else 1.0, pct_positive=100 * (x > 0).mean(),
                p_sign=stats.binomtest(int((x > 0).sum()), len(x)).pvalue)


def event_study(documents, prices, benchmark='BTC', frequency='1h'):
    """Prices use UTC bar START timestamps and simple returns over that bar."""
    step = pd.Timedelta(frequency)
    if step <= pd.Timedelta(0):
        raise ValueError('frequency must be positive')
    prices = prices.copy()
    prices['date'] = pd.to_datetime(prices.date, utc=True)
    if prices[['date', 'asset']].duplicated().any():
        raise ValueError('Duplicate price bars')
    close = prices.pivot(index='date', columns='asset', values='close').sort_index()
    grid = pd.date_range(close.index.min(), close.index.max(), freq=step)
    if not close.index.isin(grid).all():
        raise ValueError('Price bars do not match frequency')
    close = close.reindex(grid)
    # Return belongs to interval starting at its timestamp, never the preceding bar.
    returns = close.shift(-1).div(close).sub(1)
    if benchmark not in returns:
        raise ValueError('Missing benchmark')
    rows, paths = [], []
    for doc in documents.itertuples():
        ts = pd.Timestamp(doc.public_ts_utc)
        if ts.tzinfo is None:
            raise ValueError('public_ts_utc must be timezone-aware')
        ts = ts.tz_convert('UTC')
        i0 = grid.searchsorted(ts, side='right')
        if doc.asset not in returns or doc.asset == benchmark or i0 >= len(grid):
            continue
        result = event_row(returns[doc.asset], returns[benchmark], i0)
        if result is None:
            continue
        path = result.pop('_path', None)
        if path is not None:
            paths.append(pd.Series(path, name=doc.doc_id))
        lo, hi = E['main_window']
        placebo = event_row(returns[doc.asset], returns[benchmark], i0 + E['placebo_shift'])
        result[K('placebo_car', lo, hi)] = placebo.get(K('car', lo, hi), np.nan) if placebo else np.nan
        result.update(doc_id=doc.doc_id, asset=doc.asset, public_ts_utc=ts, day0=grid[i0])
        rows.append(result)
    car = pd.DataFrame(rows)
    summaries = []
    for lo, hi in E['windows']:
        for prefix in ['car', 'carma']:
            column = K(prefix, lo, hi)
            result = tests(car[column], column) if column in car else None
            if result:
                if prefix == 'car':
                    scaled = car[K('scar', lo, hi)].dropna()
                    result['t_BMP'] = scaled.mean() / (scaled.std(ddof=1) / np.sqrt(len(scaled)))
                summaries.append(result)
    for prefix in ['bhar', 'placebo_car']:
        column = K(prefix, *E['main_window'])
        result = tests(car[column], column) if column in car else None
        if result:
            summaries.append(result)
    return {'events': car, 'event_tests': pd.DataFrame(summaries), 'ar_path': pd.DataFrame(paths)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--documents', required=True, help='Parquet: doc_id, asset, public_ts_utc')
    parser.add_argument('--prices', required=True, help='Parquet: date (bar start), asset, close')
    parser.add_argument('--benchmark', default='BTC')
    parser.add_argument('--frequency', default='1h')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    from pathlib import Path
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    for name, table in event_study(pd.read_parquet(args.documents), pd.read_parquet(args.prices),
                                   args.benchmark, args.frequency).items():
        table.to_csv(output / f'{name}.csv', index=False, encoding='utf-8')


if __name__ == '__main__':
    main()
