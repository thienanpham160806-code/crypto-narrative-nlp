"""Paired forecast comparison and end-of-day long/flat economic-value diagnostics."""
import numpy as np
from scipy.stats import t


def diebold_mariano(actual, market, text, horizon=1):
    difference = (np.asarray(actual)-market)**2 - (np.asarray(actual)-text)**2
    n = len(difference)
    if n <= horizon + 1:
        raise ValueError('Too few paired forecasts')
    centered = difference - difference.mean()
    variance = centered @ centered / n
    for lag in range(1, horizon):
        variance += 2 * (1-lag/horizon) * (centered[lag:] @ centered[:-lag] / n)
    if variance <= 0:
        return {'dm': np.nan, 'dm_pvalue': np.nan}
    correction = np.sqrt((n+1-2*horizon+horizon*(horizon-1)/n)/n)
    statistic = difference.mean() / np.sqrt(variance/n) * correction
    return {'dm': statistic, 'dm_pvalue': 2*t.sf(abs(statistic), n-1)}


def metrics(actual, predicted, baseline, target):
    actual, predicted, baseline = map(np.asarray, (actual, predicted, baseline))
    error = actual - predicted
    denominator = np.sum((actual-baseline)**2)
    result = dict(rmse=np.sqrt(np.mean(error**2)), mae=np.mean(abs(error)),
                  r2_oos=1-np.sum(error**2)/denominator if denominator > 0 else np.nan)
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
