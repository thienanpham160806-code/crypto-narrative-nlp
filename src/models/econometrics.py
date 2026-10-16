"""Predictive HAC regressions and bidirectional VAR tests, using development labels only."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR

from src.models.panel import MARKET, make_panel


def regress(frame, target, features, lags):
    data = frame[[target, *features]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) <= len(features) + 2:
        raise ValueError('Insufficient regression observations')
    return sm.OLS(data[target], sm.add_constant(data[features], has_constant='add')).fit(
        cov_type='HAC', cov_kwds={'maxlags': lags})


def run_econometrics(market, text, config):
    tables, wald, granger = [], [], []
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    for h in config['model']['horizons']:
        panel = make_panel(market, text, h)
        panel = panel.loc[panel.target_date <= cutoff]
        for asset, frame in panel.groupby('asset'):
            # Shares sum to one: price_speculation is the omitted reference category.
            attention = [c for c in frame if c.startswith('attention_') and c != 'attention_price_speculation']
            for target in ['ret', 'rv']:
                for sent in ['sent_lm', 'sent_hv', 'sent_finbert']:
                    fit = regress(frame, f'y_{target}', [*MARKET, sent, *attention], max(h-1, config['model']['hac_lags']))
                    for term in fit.params.index:
                        tables.append(dict(asset=asset, horizon=h, target=target, sentiment=sent,
                                           term=term, coef=fit.params[term], se=fit.bse[term], pvalue=fit.pvalues[term],
                                           nobs=fit.nobs, r2=fit.rsquared))
            fit = regress(frame, 'y_rv', [*MARKET, 'neg_sent', 'pos_sent'], max(h-1, config['model']['hac_lags']))
            test = fit.wald_test('neg_sent = pos_sent', scalar=True)
            wald.append(dict(asset=asset, horizon=h, beta_neg=fit.params.neg_sent,
                             beta_pos=fit.params.pos_sent, statistic=float(test.statistic), pvalue=float(test.pvalue)))
    panel = make_panel(market, text)
    for asset, frame in panel.loc[panel.date <= cutoff].groupby('asset'):
        for outcome in ['ret', 'rv']:
            data = frame.set_index('date')[['sent_finbert', outcome]].dropna()
            if len(data) < 30 or not data.index.to_series().diff().dropna().eq(pd.Timedelta(days=1)).all():
                raise ValueError('VAR requires a contiguous daily series with at least 30 observations')
            data = data.asfreq('D')
            maximum = min(config['model']['var_maxlags'], (len(data)-5)//3)
            lag = int(VAR(data).select_order(maxlags=maximum).selected_orders['aic'])
            if lag == 0:
                for caused, causing in [(outcome, 'sent_finbert'), ('sent_finbert', outcome)]:
                    granger.append(dict(asset=asset, outcome=outcome, causing=causing, caused=caused,
                                        lag=0, statistic=np.nan, pvalue=np.nan, conclusion='AIC selects no lags; no Granger test'))
                continue
            fit = VAR(data).fit(lag)
            for caused, causing in [(outcome, 'sent_finbert'), ('sent_finbert', outcome)]:
                test = fit.test_causality(caused, [causing], kind='f')
                granger.append(dict(asset=asset, outcome=outcome, causing=causing, caused=caused,
                                    lag=lag, statistic=test.test_statistic, pvalue=test.pvalue,
                                    conclusion='Predictive lead (not structural causality)' if test.pvalue < .05 else 'No predictive lead at 5%'))
    return {'regressions': pd.DataFrame(tables), 'wald': pd.DataFrame(wald), 'granger': pd.DataFrame(granger)}
