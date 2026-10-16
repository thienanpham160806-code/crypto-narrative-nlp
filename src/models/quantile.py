"""Predictive RQ2 quantile asymmetry; 500-calendar-day windows, 20-day steps."""
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools.sm_exceptions import IterationLimitWarning
from sklearn.linear_model import QuantileRegressor
from threadpoolctl import threadpool_limits

from src.models.panel import MARKET, make_panel


def quantile_fit(frame, features, tau, inference=True):
    data = frame[['y_rv', *features]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) < max(30, len(features)+3):
        return None
    # Scaling prevents tiny RV magnitudes from triggering premature solver convergence.
    x, y = data[features], data.y_rv
    sd = x.std()
    x = x.loc[:, sd > 0]
    sd = sd[sd > 0]
    scale = y.std()
    if scale <= 0 or not {'neg_sent', 'pos_sent'}.issubset(x):
        return None
    sample = dict(tau=tau, nobs=len(data), sample_start=frame.loc[data.index].date.min(),
                  sample_end=frame.loc[data.index].date.max(), target_max=frame.loc[data.index].target_date.max())
    sample['identified'] = np.linalg.matrix_rank(sm.add_constant((x-x.mean())/sd)) == len(x.columns)+1
    if not inference:
        fit = QuantileRegressor(quantile=tau, alpha=0, solver='highs').fit((x-x.mean())/sd, y/scale)
        coefficients = pd.Series(fit.coef_*scale/sd, index=x.columns)
        return dict(**sample, beta_neg=coefficients.neg_sent, beta_pos=coefficients.pos_sent,
                    se_neg=np.nan, se_pos=np.nan, statistic=np.nan, pvalue=np.nan, converged=True,
                    inference='rolling coefficients only; exact pinball-loss linear programming')
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', IterationLimitWarning)
        fit = sm.QuantReg(y/scale, sm.add_constant((x-x.mean())/sd)).fit(q=tau, max_iter=5000, p_tol=1e-7)
    restriction = np.zeros((1, len(fit.params)))
    for term, sign in [('neg_sent', 1), ('pos_sent', -1)]:
        restriction[0, fit.params.index.get_loc(term)] = sign*scale/sd[term]
    covariance = fit.cov_params().to_numpy()
    valid_covariance = sample['identified'] and np.isfinite(covariance).all() and float((restriction@covariance@restriction.T)[0, 0]) > 0
    test = fit.wald_test(restriction, scalar=True) if valid_covariance else None
    return dict(**sample,
                beta_neg=fit.params.neg_sent*scale/sd.neg_sent, beta_pos=fit.params.pos_sent*scale/sd.pos_sent,
                se_neg=fit.bse.neg_sent*scale/sd.neg_sent if valid_covariance else np.nan,
                se_pos=fit.bse.pos_sent*scale/sd.pos_sent if valid_covariance else np.nan,
                statistic=float(test.statistic) if test else np.nan, pvalue=float(test.pvalue) if test else np.nan,
                converged=not any(isinstance(w.message, IterationLimitWarning) for w in caught),
                inference='heteroskedastic robust; serial dependence not corrected' if valid_covariance else
                          'coefficient estimate only; covariance unavailable in this sample')


@threadpool_limits.wrap(limits=1)
def run_quantiles(market, text, config):
    rows, rolling, status = [], [], []
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    for horizon in config['model']['horizons']:
        panel = make_panel(market, text, horizon)
        panel = panel.loc[panel.target_date <= cutoff].copy()
        panel['log_n_docs'] = np.log(panel.n_docs.where(panel.n_docs > 0))
        optional = [c for c in panel if c.startswith(('disagreement', 'soft_attention_', 'attention_soft_', 'ucry_'))
                    and not c.endswith('price_speculation')]
        features = [*MARKET, 'log_n_docs', 'neg_sent', 'pos_sent', *optional]
        for asset, frame in panel.groupby('asset'):
            frame = frame.sort_values('date')
            for tau in [.1, .5, .9]:
                result = quantile_fit(frame, features, tau)
                if result:
                    rows.append(dict(asset=asset, horizon=horizon, **result))
            if frame.empty:
                continue
            ends = pd.date_range(frame.date.min()+pd.Timedelta(days=499), frame.date.max(), freq='20D')
            for end in ends:
                start = end-pd.Timedelta(days=499)
                sample = frame.loc[frame.date.between(start, end)]
                for tau in [.1, .5, .9]:
                    result = quantile_fit(sample, features, tau, inference=False)
                    if result:
                        rolling.append(dict(asset=asset, horizon=horizon, window_start=start, window_end=end,
                                            window_days=500, step_days=20, **result))
            status.append(dict(asset=asset, horizon=horizon, rolling_windows=len(ends),
                               status='available' if len(ends) else 'pending: fewer than 500 calendar days'))
    return {'quantiles': pd.DataFrame(rows, columns=None if rows else ['pvalue']),
            'rolling_quantiles': pd.DataFrame(rolling, columns=None if rolling else ['pvalue']),
            'quantile_status': pd.DataFrame(status)}
