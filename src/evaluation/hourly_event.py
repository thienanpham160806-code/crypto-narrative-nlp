"""Offline hourly event study from canonical English articles and cached Binance bars."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from src.utils.common import ROOT


WINDOWS = ((0, 0), (0, 3), (0, 23), (-4, -1))
ASSETS = ('BTC', 'ETH', 'SOL', 'BNB', 'XRP')


def event_documents(documents, scores, train_end):
    docs = documents.loc[documents.is_canonical & documents.lang.eq('en')].copy()
    docs = docs.merge(scores, on='doc_id', how='left', validate='one_to_one')
    for name in ('public_ts_utc', 'published_at_utc', 'first_seen_utc'):
        docs[name] = pd.to_datetime(docs[name], utc=True)
    training = docs.loc[docs.public_ts_utc.dt.floor('D').le(pd.Timestamp(train_end, tz='UTC'))]
    cuts = training.finbert_sentiment.dropna().quantile([1/3, 2/3]).to_numpy()
    low, high = cuts
    docs['finbert_tercile'] = pd.Series(np.select([docs.finbert_sentiment.le(low), docs.finbert_sentiment.le(high)],
                                                      ['negative', 'middle'], default='positive'), index=docs.index)
    docs.loc[docs.finbert_sentiment.isna(), 'finbert_tercile'] = None
    docs['lm_tone'] = pd.Series(np.select([docs.lm_net.lt(0), docs.lm_net.eq(0)],
                                         ['negative', 'neutral'], default='positive'), index=docs.index)
    docs.loc[docs.lm_net.isna(), 'lm_tone'] = None
    docs['text_scope'] = docs.asset_tags.map(lambda tags: 'coin_specific' if len(tags) else 'market_wide')
    docs['asset'] = docs.asset_tags.map(lambda tags: list(tags) if len(tags) else ['BTC'])
    return docs.explode('asset').loc[lambda frame: frame.asset.isin(ASSETS)].reset_index(drop=True), cuts


def hourly_prices(directory=ROOT/'data/raw'):
    prices = {}
    for asset in ASSETS:
        matches = list(Path(directory).glob(f'{asset}_1h_*.parquet'))
        if len(matches) != 1:
            raise ValueError(f'Expected one cached hourly file for {asset}; found {len(matches)}')
        frame = pd.read_parquet(matches[0], columns=['date', 'close', 'volume'])
        frame['date'] = pd.to_datetime(frame.date, utc=True)
        if frame.date.duplicated().any() or (frame.close <= 0).any() or (frame.volume < 0).any():
            raise ValueError(f'Invalid hourly candles for {asset}')
        prices[asset] = frame.set_index('date').sort_index()
    return prices


def event_observations(documents, prices, timestamp='public_ts_utc'):
    starts = min(frame.index.min() for frame in prices.values())
    ends = max(frame.index.max() for frame in prices.values())
    grid = pd.date_range(starts, ends, freq='h', tz='UTC')
    grid_ns = grid.as_unit('ns').asi8
    arrays = {}
    for asset, frame in prices.items():
        aligned = frame.reindex(grid)
        close = aligned.close.to_numpy(float)
        log_volume = np.log1p((aligned.close*aligned.volume).to_numpy(float))
        returns = np.r_[np.nan, np.diff(np.log(close))]
        arrays[asset] = (returns, log_volume)
    btc_returns = arrays['BTC'][0]
    rows = []
    fit_cache = {}
    for doc in documents.itertuples(index=False):
        ts = getattr(doc, timestamp)
        if pd.isna(ts) or doc.asset not in arrays:
            continue
        if ts.tzinfo is None:
            raise ValueError('Event timestamps must be timezone-aware UTC')
        i0 = int(np.searchsorted(grid_ns, ts.value, side='right'))
        if i0 < 168 or i0+23 >= len(grid):
            continue
        ret, volume = arrays[doc.asset]
        key = (doc.asset, i0)
        if key not in fit_cache:
            y = ret[i0-168:i0-24]
            x = btc_returns[i0-168:i0-24]
            v = volume[i0-168:i0-24]
            good = np.isfinite(y) & np.isfinite(v)
            if doc.asset != 'BTC':
                good &= np.isfinite(x)
            if good.sum() < 96:
                fit_cache[key] = None
            else:
                y, v, x = y[good], v[good], x[good]
                if doc.asset == 'BTC':
                    alpha, beta = y.mean(), 0.0
                else:
                    design = np.column_stack([np.ones(len(x)), x])
                    alpha, beta = np.linalg.lstsq(design, y, rcond=None)[0]
                residual = y-alpha-beta*x
                fit_cache[key] = (alpha, beta, residual.std(ddof=2), np.abs(y).mean(), v.mean(),
                                  len(y), x.mean(), np.sum((x-x.mean())**2))
        fit = fit_cache[key]
        if fit is None:
            continue
        alpha, beta, sigma, abs_base, vol_base, n_est, x_mean, x_ss = fit
        text_scope = getattr(doc, 'text_scope', 'coin_specific')
        row = dict(doc_id=doc.doc_id, asset=doc.asset, source=doc.source,
                   text_scope=text_scope, missing_coin_text=text_scope == 'market_wide',
                   public_ts_utc=doc.public_ts_utc, published_at_utc=doc.published_at_utc,
                   first_seen_utc=doc.first_seen_utc, t0=grid[i0], event_day=grid[i0].floor('D'),
                   narrative=doc.narrative, finbert_tercile=doc.finbert_tercile,
                   lm_tone=doc.lm_tone, finbert_sentiment=doc.finbert_sentiment,
                   lm_net=doc.lm_net, estimation_n=144, residual_sigma=sigma,
                   timestamp_basis=timestamp)
        row['estimation_n'] = n_est
        for lo, hi in WINDOWS:
            sl = slice(i0+lo, i0+hi+1)
            y, x, v = ret[sl], btc_returns[sl], volume[sl]
            if len(y) != hi-lo+1 or not (np.isfinite(y).all() and np.isfinite(v).all()):
                continue
            if doc.asset != 'BTC' and not np.isfinite(x).all():
                continue
            suffix = f'{lo}_{hi}'
            car = float(np.sum(y-alpha-beta*x))
            row[f'car_{suffix}'] = car
            variance = len(y)*(1+len(y)/n_est)
            if doc.asset != 'BTC' and x_ss > 0:
                variance += (np.sum(x)-len(y)*x_mean)**2/x_ss
            row[f'scar_{suffix}'] = car/(sigma*np.sqrt(variance)) if sigma > 0 else np.nan
            row[f'absret_{suffix}'] = float(np.sum(np.abs(y)-abs_base))
            row[f'volume_{suffix}'] = float(np.mean(v-vol_base))
            if i0-24+hi < i0 and i0-24+lo >= 0:
                p = slice(i0-24+lo, i0-24+hi+1)
                py, px = ret[p], btc_returns[p]
                if np.isfinite(py).all() and (doc.asset == 'BTC' or np.isfinite(px).all()):
                    row[f'placebo_car_{suffix}'] = float(np.sum(py-alpha-beta*px))
        rows.append(row)
    return pd.DataFrame(rows)


def daily_inference(days, bootstrap=False):
    """Calendar-lag HAC on event-day means; optional seven-calendar-day bootstrap."""
    days = days.sort_index().astype(float)
    n = len(days)
    if n < 5:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    calendar = days.reindex(pd.date_range(days.index.min(), days.index.max(), freq='D', tz='UTC'))
    mean = float(days.mean())
    centered = calendar.fillna(mean).to_numpy() - mean
    variance = float(np.dot(centered, centered))
    for lag in range(1, 8):
        variance += 2 * (1 - lag/8) * float(np.dot(centered[:-lag], centered[lag:]))
    se = np.sqrt(max(variance, 0))/n
    t = mean/se if se > 0 else np.nan
    p = float(2*stats.norm.sf(abs(t))) if np.isfinite(t) else np.nan
    if not bootstrap:
        return se, t, p, np.nan, np.nan, 2.802*se
    rng = np.random.default_rng(42)
    values = calendar.to_numpy()
    span = len(values)
    starts = rng.integers(0, span, size=(1999, (span+6)//7))
    indices = (starts[:, :, None] + np.arange(7)) % span
    draws = values[indices.reshape(1999, -1)[:, :span]]
    counts = np.isfinite(draws).sum(axis=1)
    while not counts.all():
        missing = np.flatnonzero(counts == 0)
        retry = rng.integers(0, span, size=(len(missing), (span+6)//7))
        draws[missing] = values[((retry[:, :, None] + np.arange(7)) % span).reshape(len(missing), -1)[:, :span]]
        counts[missing] = np.isfinite(draws[missing]).sum(axis=1)
    means = np.nansum(draws, axis=1)/counts
    low, high = np.quantile(means, [.025, .975])
    p_boot = (1 + np.count_nonzero(np.abs(means-mean) >= abs(mean)))/2000
    return se, t, p, float(low), float(high), 2.802*se, float(p_boot)


def clustered_tests(events):
    rows = []
    groups = [('all', 'all', events)]
    for column in ('source', 'finbert_tercile', 'lm_tone', 'narrative'):
        for value, part in events.groupby(column, observed=True):
            groups.append((column, str(value), part))
    for grouping, group, part in groups:
        for lo, hi in WINDOWS:
            for metric in ('car', 'absret', 'volume', 'placebo_car'):
                column = f'{metric}_{lo}_{hi}'
                if column not in part:
                    continue
                valid = part.dropna(subset=[column])
                days = valid.groupby('event_day')[column].mean()
                if len(days) < 5:
                    continue
                primary = grouping == 'all' and (lo, hi) in WINDOWS[:3] and metric in ('car', 'absret', 'volume')
                inference = daily_inference(days, bootstrap=primary)
                se, t, p, ci_low, ci_high, mde = inference[:6]
                scaled = valid.groupby('event_day')[f'scar_{lo}_{hi}'].mean() if metric == 'car' else pd.Series(dtype=float)
                bmp = stats.ttest_1samp(scaled.dropna(), 0) if len(scaled.dropna()) >= 5 else None
                rows.append(dict(grouping=grouping, group=group, window=f'[{lo},{hi}]', metric=metric,
                                 n_events=len(valid), n_days=len(days), mean=float(days.mean()),
                                 median=float(days.median()), t=t, p_t=p, hac_se=se, mde=mde,
                                 bootstrap_ci_low=ci_low, bootstrap_ci_high=ci_high,
                                 p_bootstrap=inference[6] if primary else np.nan,
                                 bmp_t=float(bmp.statistic) if bmp else np.nan,
                                 p_bmp=float(bmp.pvalue) if bmp else np.nan,
                                 p_wilcoxon=float(stats.wilcoxon(days).pvalue) if days.ne(0).any() else 1.0))
    return pd.DataFrame(rows)


def asymmetry_tests(events):
    rows = []
    for tone in ('finbert_tercile', 'lm_tone'):
        for lo, hi in WINDOWS[:4]:
            for metric in ('car', 'absret', 'volume'):
                column = f'{metric}_{lo}_{hi}'
                if column not in events:
                    continue
                daily = events.loc[events[tone].isin(['negative', 'positive'])].pivot_table(
                    index='event_day', columns=tone, values=column, aggfunc='mean', observed=True)
                if not {'negative', 'positive'}.issubset(daily) or len(daily.dropna()) < 5:
                    continue
                diff = daily.positive-daily.negative
                diff = diff.dropna()
                _, t, p, _, _, mde = daily_inference(diff)
                rows.append(dict(tone=tone, window=f'[{lo},{hi}]', metric=metric, n_days=len(diff),
                                 negative_mean=float(daily.negative.loc[diff.index].mean()),
                                 positive_mean=float(daily.positive.loc[diff.index].mean()),
                                 positive_minus_negative=float(diff.mean()),
                                 negative_minus_positive=-float(diff.mean()), t=t, p_t=p, mde=mde,
                                 p_wilcoxon=float(stats.wilcoxon(diff).pvalue) if diff.ne(0).any() else 1.0))
    return pd.DataFrame(rows)


def holm_columns(table):
    for column in [name for name in table if name.startswith('p_')]:
        valid = table[column].notna()
        table[f'{column}_holm'] = np.nan
        if valid.any():
            table.loc[valid, f'{column}_holm'] = multipletests(table.loc[valid, column], method='holm')[1]
    return table


def timing_comparison(documents, prices):
    paired = documents.loc[documents.source.eq('gdelt') & documents.published_at_utc.notna() &
                           documents.first_seen_utc.notna()].copy()
    published = event_observations(paired, prices, 'published_at_utc')
    seen = event_observations(paired, prices, 'first_seen_utc')
    names = [f'car_{lo}_{hi}' for lo, hi in WINDOWS[:3]]
    pairs = published[['doc_id', 'asset', 't0', *[c for c in names if c in published]]].merge(
        seen[['doc_id', 'asset', 't0', *[c for c in names if c in seen]]], on=['doc_id', 'asset'],
        suffixes=('_published', '_seen'), validate='one_to_one')
    summary = []
    for column in names:
        a, b = f'{column}_published', f'{column}_seen'
        if a not in pairs or b not in pairs:
            continue
        sample = pairs.dropna(subset=[a, b]).copy()
        if sample.empty:
            continue
        daily = sample.groupby(sample.t0_published.dt.floor('D'))[[a, b]].mean()
        difference = daily[a]-daily[b]
        p_public = stats.ttest_1samp(daily[a], 0).pvalue if len(daily) >= 5 else np.nan
        p_seen = stats.ttest_1samp(daily[b], 0).pvalue if len(daily) >= 5 else np.nan
        summary.append(dict(window=column.removeprefix('car_'), n_pairs=len(sample), n_days=len(daily),
                            n_unique_articles=sample.doc_id.nunique(),
                            mean_car_published=daily[a].mean(), mean_car_seen=daily[b].mean(),
                            mean_published_minus_seen=difference.mean(),
                            p_paired_t=stats.ttest_1samp(difference, 0).pvalue if len(daily) >= 5 else np.nan,
                            p_paired_wilcoxon=(stats.wilcoxon(difference).pvalue if difference.ne(0).any() else 1.0)
                            if len(daily) >= 5 else np.nan,
                            p_public=float(p_public), p_seen=float(p_seen),
                            significance_changed=bool((p_public < .05) != (p_seen < .05)) if len(daily) >= 5 else None))
    result = holm_columns(pd.DataFrame(summary))
    if not result.empty:
        result['significance_changed_holm'] = result.p_public_holm.lt(.05) != result.p_seen_holm.lt(.05)
    return pairs, result


def run_real_events(documents, scores, prices, train_end, output, figures):
    output, figures = Path(output), Path(figures)
    output.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    docs, cuts = event_documents(documents, scores, train_end)
    events = event_observations(docs, prices)
    tests = holm_columns(clustered_tests(events))
    tests['p_primary_holm'] = np.nan
    primary = tests.grouping.eq('all') & tests.window.isin(['[0,0]', '[0,3]', '[0,23]']) & tests.metric.isin(['car', 'absret', 'volume'])
    assert primary.sum() == 9, 'The preregistered nine-test family is incomplete'
    tests.loc[primary, 'p_primary_holm'] = multipletests(tests.loc[primary, 'p_t'], method='holm')[1]
    asymmetry = holm_columns(asymmetry_tests(events))
    timing_pairs, timing = timing_comparison(docs, prices)
    coverage = pd.DataFrame([dict(canonical_en_articles=docs.doc_id.nunique(), article_asset_rows=len(docs),
                                  scored_finbert_articles=docs.loc[docs.finbert_sentiment.notna(), 'doc_id'].nunique(),
                                  usable_event_rows=len(events), usable_event_days=events.event_day.nunique(),
                                  gdelt_event_rows=int(events.source.eq('gdelt').sum()),
                                  sec_event_rows=int(events.source.eq('sec').sum()),
                                  gdelt_article_days=docs.loc[docs.source.eq('gdelt'), 'public_ts_utc'].dt.floor('D').nunique(),
                                  sec_article_days=docs.loc[docs.source.eq('sec'), 'public_ts_utc'].dt.floor('D').nunique(),
                                  first_event=events.t0.min(), last_event=events.t0.max(),
                                  timing_audited_articles=docs.loc[docs.source.eq('gdelt') & docs.published_at_utc.notna(), 'doc_id'].nunique(),
                                  finbert_train_cut_low=cuts[0], finbert_train_cut_high=cuts[1])])
    scope = events.groupby('asset', observed=True).agg(
        event_rows=('doc_id', 'size'), market_wide_fallback_events=('missing_coin_text', 'sum')).reset_index()
    scope['coin_specific_events'] = scope.event_rows-scope.market_wide_fallback_events
    scope['fallback_pct'] = 100*scope.market_wide_fallback_events/scope.event_rows
    tables = dict(event_observations=events, event_tests=tests, event_asymmetry=asymmetry,
                  event_timing_pairs=timing_pairs, event_timing=timing, event_coverage=coverage,
                  event_text_scope=scope)
    for name, table in tables.items():
        table.to_csv(output/f'{name}.csv', index=False, encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    chosen = tests.loc[(tests.grouping == 'finbert_tercile') & (tests.metric == 'car') &
                       tests.window.isin(['[0,0]', '[0,3]', '[0,23]'])]
    if not chosen.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        for tone, part in chosen.groupby('group'):
            ax.plot(part.window, part['mean']*100, marker='o', label=tone)
        ax.axhline(0, color='grey', linewidth=.8)
        ax.set_ylabel('Cluster-day mean CAR (%)')
        ax.tick_params(labelsize=10)
        ax.yaxis.label.set_size(11)
        ax.legend()
        fig.set_size_inches(6, 3.8)
        fig.tight_layout()
        fig.savefig(figures/'event_car_by_tone.svg', metadata={'Date': None})
        fig.savefig(figures/'event_car_by_tone.png', dpi=300)
        plt.close(fig)
    return tables
