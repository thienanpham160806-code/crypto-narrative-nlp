"""Paired forecast comparison and end-of-day long/flat economic-value diagnostics."""
import numpy as np
from scipy.stats import t, norm, chi2
import pandas as pd
import statsmodels.api as sm


def paired_arrays(actual, market, text):
    arrays = [np.asarray(x, dtype=float) for x in (actual, market, text)]
    if any(x.ndim != 1 or x.shape != arrays[0].shape or not np.isfinite(x).all() for x in arrays):
        raise ValueError('Need finite aligned one-dimensional forecast arrays')
    return arrays


def diebold_mariano(actual, market, text, horizon=1):
    actual, market, text = paired_arrays(actual, market, text)
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError('horizon must be a positive integer')
    difference = (actual-market)**2 - (actual-text)**2
    n = len(difference)
    if n <= horizon + 1:
        raise ValueError('Too few paired forecasts')
    centered = difference - difference.mean()
    variance = centered @ centered / n
    for lag in range(1, horizon):
        variance += 2 * (centered[lag:] @ centered[:-lag] / n)
    if variance <= 0:
        return {'dm': np.nan, 'dm_pvalue': np.nan, 'dm_uncorrected': np.nan, 'dm_hln_factor': np.nan}
    correction = np.sqrt((n+1-2*horizon+horizon*(horizon-1)/n)/n)
    uncorrected = difference.mean() / np.sqrt(variance/n)
    statistic = uncorrected * correction
    return {'dm': statistic, 'dm_pvalue': 2*t.sf(abs(statistic), n-1),
            'dm_uncorrected': uncorrected, 'dm_hln_factor': correction}


def clark_west(actual, restricted, unrestricted, horizon=1):
    """One-sided adjusted-MSPE HAC test (Clark & West, 2007).

    Positive statistic favors unrestricted forecasts. Theory is for nested linear
    models; comparisons of tuned/shrunk trees are exploratory diagnostics only.
    """
    y, small, large = paired_arrays(actual, restricted, unrestricted)
    if horizon < 1 or len(y) <= horizon + 1:
        raise ValueError('Need positive horizon and enough paired forecasts')
    adjusted = (y-small)**2 - (y-large)**2 + (small-large)**2
    fit = sm.OLS(adjusted, np.ones((len(y), 1))).fit(cov_type='HAC', cov_kwds={'maxlags': horizon-1})
    statistic = fit.params[0]/fit.bse[0] if fit.bse[0] > 0 else np.nan
    return {'cw': statistic, 'cw_pvalue': norm.sf(statistic), 'cw_adjusted_mspe': adjusted.mean()}


def giacomini_white(actual, first, second, instruments, horizon=1):
    """Conditional predictive ability Wald test for fixed-window forecasts.

    Instruments must be observable at forecast origin. Uses Bartlett HAC for
    multi-step forecasts; chi-square asymptotics require a fixed estimation window.
    """
    y, first, second = paired_arrays(actual, first, second)
    z = np.asarray(instruments, dtype=float)
    if z.ndim == 1:
        z = z[:, None]
    if len(z) != len(y) or not np.isfinite(z).all() or horizon < 1:
        raise ValueError('Invalid GW instruments or horizon')
    z = sm.add_constant(z, has_constant='add')
    moments = z * ((y-first)**2-(y-second)**2)[:, None]
    n, q = moments.shape
    if n <= q + horizon:
        raise ValueError('Too few observations for GW')
    centered = moments - moments.mean(axis=0)
    covariance = centered.T @ centered / n
    for lag in range(1, horizon):
        gamma = centered[lag:].T @ centered[:-lag] / n
        covariance += (1-lag/horizon)*(gamma+gamma.T)
    rank = np.linalg.matrix_rank(covariance)
    if rank < q:
        return {'gw': np.nan, 'gw_pvalue': np.nan, 'gw_df': rank}
    statistic = float(n*moments.mean(axis=0) @ np.linalg.solve(covariance, moments.mean(axis=0)))
    return {'gw': statistic, 'gw_pvalue': chi2.sf(statistic, q), 'gw_df': q}


def model_confidence_set(losses, seed, alpha=.1, bootstrap=999, block_length=10):
    """HLN Tmax elimination, circular block bootstrap of centered loss contrasts.

    Rows must be consecutive observations; columns identify forecast models.
    Reports monotone MCS p-values; no model is chosen using test-set results.
    """
    losses = pd.DataFrame(losses)
    n, m = losses.shape
    if n < 10 or m < 2 or not np.isfinite(losses.to_numpy()).all():
        raise ValueError('MCS needs finite losses for at least ten observations and two models')
    if not 0 < alpha < 1 or bootstrap < 99 or not 1 <= block_length <= n:
        raise ValueError('Invalid MCS bootstrap settings')
    rng = np.random.default_rng(seed)
    starts = rng.integers(n, size=(bootstrap, int(np.ceil(n/block_length))))
    indices = ((starts[..., None] + np.arange(block_length)) % n).reshape(bootstrap, -1)[:, :n]
    active, results, running_p = list(range(m)), {}, 0.0
    values = losses.to_numpy()
    while len(active) > 1:
        selected = values[:, active]
        contrasts = selected - selected.mean(axis=1, keepdims=True)
        means = contrasts.mean(axis=0)
        centered = contrasts - means
        bootstrap_means = centered[indices].mean(axis=1)
        se = bootstrap_means.std(axis=0, ddof=1)
        statistic = np.divide(means, se, out=np.zeros_like(means), where=se > 0)
        statistic[(se == 0) & (means > 0)] = np.inf
        boot_stat = np.divide(bootstrap_means, se, out=np.zeros_like(bootstrap_means), where=se > 0)
        pvalue = (1 + (boot_stat.max(axis=1) >= statistic.max()).sum())/(bootstrap+1)
        running_p = max(running_p, pvalue)
        worst = int(np.argmax(statistic))
        results[active.pop(worst)] = running_p
    results[active[0]] = 1.0
    return pd.DataFrame({'model': losses.columns, 'mcs_pvalue': [results[i] for i in range(m)],
                         'included': [results[i] >= alpha for i in range(m)], 'alpha': alpha,
                         'bootstrap': bootstrap, 'block_length': block_length, 'seed': seed})


def metrics(actual, predicted, baseline, target):
    """Campbell–Thompson OOS R² relative to an origin-specific historical mean."""
    actual, predicted, baseline = paired_arrays(actual, predicted, baseline)
    error = actual - predicted
    denominator = np.sum((actual-baseline)**2)
    result = dict(rmse=np.sqrt(np.mean(error**2)), mae=np.mean(abs(error)),
                  r2_oos=1-np.sum(error**2)/denominator if denominator > 0 else np.nan)
    result['r2_oos_ct'] = result['r2_oos']
    if target == 'rv':
        ratio = np.maximum(actual, 1e-12) / np.maximum(predicted, 1e-12)
        result['qlike'] = np.mean(ratio-np.log(ratio)-1)
    return result


def strategy(actual, predicted, fee=.001):
    actual = np.asarray(actual)
    position = (np.asarray(predicted) > 0).astype(float)
    turnover = np.abs(np.diff(np.r_[0, position]))
    if len(turnover):
        turnover[-1] += position[-1]  # liquidate the final position
    net = position * np.expm1(actual) - fee*turnover
    buy_hold = np.expm1(actual).copy()
    buy_hold[0] -= fee
    buy_hold[-1] -= fee
    def summary(values):
        sd = np.std(values, ddof=1)
        return np.prod(1+values)-1, np.sqrt(365)*np.mean(values)/sd if sd > 0 else np.nan
    total, sharpe = summary(net)
    bh_total, bh_sharpe = summary(buy_hold)
    return dict(net_return=total, sharpe=sharpe, buy_hold_return=bh_total, buy_hold_sharpe=bh_sharpe,
                fee_bps=fee*10000, turnover=turnover.sum())
