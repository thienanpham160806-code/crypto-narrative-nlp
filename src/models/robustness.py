"""Development-only X4 diagnostics and pre-specified sensitivity regressions."""
import warnings

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
from statsmodels.tsa.stattools import adfuller, kpss

from src.models.econometrics import regress
from src.models.panel import make_panel


def adjust_pvalues(table):
    """Treat each exported table as one family, excluding unavailable tests."""
    table = table.copy()
    valid = table.pvalue.notna()
    for method, column in [('holm', 'p_holm'), ('fdr_bh', 'p_bh')]:
        table[column] = np.nan
        if valid.any():
            table.loc[valid, column] = multipletests(table.loc[valid, 'pvalue'], method=method)[1]
    return table


def run_robustness(market, text, config, text_variants=None):
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    diagnostics, rows, status = [], [], []
    base = make_panel(market, text)
    base = base.loc[base.date <= cutoff]
    for asset, frame in base.groupby('asset'):
        for term in ['ret', 'rv', 'logvol', 'sent_finbert', 'n_docs']:
            # Never bridge missing calendar days in a time-series diagnostic.
            series = frame.set_index('date')[term].asfreq('D')
            groups = series.isna().cumsum()
            parts = [part.dropna() for _, part in series.groupby(groups)]
            series = max(parts, key=len)
            if len(series) < 30 or series.nunique() < 2:
                continue
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                for name, result in [('ADF', adfuller(series, autolag='AIC')),
                                     ('KPSS', kpss(series, regression='c', nlags='auto'))]:
                    diagnostics.append(dict(asset=asset, term=term, test=name, statistic=result[0],
                                            pvalue=result[1], nobs=len(series),
                                            sample_start=series.index.min(), sample_end=series.index.max()))
    variants = {'baseline': text, **(text_variants or {})}
    for required in ['source_weighted', 'exclude_price_speculation']:
        status.append(dict(variant=required, status='provided' if required in variants else
                           'pending document-level aggregation; cannot reconstruct from daily means'))
    for variant, daily in variants.items():
        for horizon in config['model']['horizons']:
            panel = make_panel(market, daily, horizon)
            panel = panel.loc[panel.target_date <= cutoff].copy()
            panel['dummy_2025_01'] = panel.date.ge(pd.Timestamp('2025-01-01', tz='UTC')).astype(int)
            # Current return plus six lags gives seven calendar days of momentum.
            panel['momentum_7'] = panel[['ret', *[f'ret_lag{i}' for i in range(1, 7)]]].sum(axis=1, min_count=7)
            for asset, frame in panel.groupby('asset'):
                periods = {'full': frame, 'pre_2025': frame.loc[frame.target_date < pd.Timestamp('2025-01-01', tz='UTC')],
                           'post_2025': frame.loc[frame.date >= pd.Timestamp('2025-01-01', tz='UTC')]}
                attention = [c for c in frame if c.startswith('attention_') and c != 'attention_price_speculation']
                for period, sample in periods.items():
                    # Avoid exact collinearity: momentum replaces its component return lags.
                    features = ['rv', 'logvol', 'momentum_7', 'n_docs', 'sent_finbert', *attention]
                    if sample.dummy_2025_01.nunique() > 1:
                        features.append('dummy_2025_01')
                    for target in ['ret', 'rv', 'logvol']:
                        if len(sample.dropna(subset=[f'y_{target}', *features])) <= len(features) + 2:
                            continue
                        fit = regress(sample, f'y_{target}', features, max(horizon-1, config['model']['hac_lags']))
                        for term in fit.params.index:
                            rows.append(dict(variant=variant, asset=asset, horizon=horizon, period=period,
                                             target=target, term=term, coef=fit.params[term], se=fit.bse[term],
                                             pvalue=fit.pvalues[term], nobs=fit.nobs))
    return {'stationarity': adjust_pvalues(pd.DataFrame(diagnostics, columns=[
                'asset', 'term', 'test', 'statistic', 'pvalue', 'nobs', 'sample_start', 'sample_end'])),
            'robustness': adjust_pvalues(pd.DataFrame(rows, columns=[
                'variant', 'asset', 'horizon', 'period', 'target', 'term', 'coef', 'se', 'pvalue', 'nobs'])),
            'robustness_status': pd.DataFrame(status)}
