"""Predictive HAC regressions and bidirectional VAR tests, using development labels only."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR

from src.models.panel import MARKET, make_panel


def attach_ucry(text, ucry):
    """Join released weekly controls within upstream's seven-day release tolerance."""
    ucry = ucry.copy()
    ucry['date'] = pd.to_datetime(ucry.date, utc=True)
    week_end = pd.to_datetime(ucry.week_end, utc=True)
    if ucry.date.duplicated().any() or not ucry.date.eq(ucry.date.dt.floor('D')).all():
        raise ValueError('UCRY needs unique UTC daily keys')
    release = week_end + pd.Timedelta(days=1)
    available = (ucry.date >= release) & (ucry.date <= release+pd.Timedelta(days=7))
    if ucry.loc[~available, ['ucry_policy', 'ucry_price']].notna().any().any():
        raise ValueError('UCRY values violate weekly release availability')
    text = text.copy()
    text['date'] = pd.to_datetime(text.date, utc=True)
    return text.merge(ucry[['date', 'ucry_policy', 'ucry_price']], on='date', how='left', validate='many_to_one')


def regress(frame, target, features, lags):
    data = frame[[target, *features]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) <= len(features) + 2:
        raise ValueError('Insufficient regression observations')
    fit = sm.OLS(data[target], sm.add_constant(data[features], has_constant='add')).fit(
        cov_type='HAC', cov_kwds={'maxlags': lags})
    fit.identified = fit.model.rank == len(fit.params)
    return fit


def run_econometrics(market, text, config):
    tables, wald, granger = [], [], []
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    for h in config['model']['horizons']:
        panel = make_panel(market, text, h)
        panel = panel.loc[panel.target_date <= cutoff]
        panel['log_n_docs'] = np.log(panel.n_docs.where(panel.n_docs > 0))
        for asset, frame in panel.groupby('asset'):
            # Shares sum to one: price_speculation is the omitted reference category.
            attention = [f'attention_{k}' for k in config['nlp']['narratives'] if k != 'price_speculation']
            optional = [c for c in frame if c.startswith(('disagreement', 'soft_attention_', 'attention_soft_', 'ucry_'))
                        and not c.endswith('price_speculation')]
            for target in ['ret', 'rv', 'logvol']:
                common = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=[
                    f'y_{target}', *MARKET, 'log_n_docs', 'sent_lm', 'sent_hv', 'sent_finbert', *attention, *optional])
                controls = [c for c in optional if c.startswith('ucry_')]
                specifications = [('market', 'none', [*MARKET, *controls]),
                                  ('attention', 'none', [*MARKET, 'log_n_docs', *controls])]
                specifications += [('text', sent, [*MARKET, 'log_n_docs', sent, *attention, *optional])
                                   for sent in ['sent_lm', 'sent_hv', 'sent_finbert']]
                for version, sent, features in specifications:
                    if len(common) <= len(features)+2:
                        continue
                    fit = regress(common, f'y_{target}', features, max(h-1, config['model']['hac_lags']))
                    for term in fit.params.index:
                        tables.append(dict(asset=asset, horizon=h, target=target, sentiment=sent, version=version,
                                           term=term, coef=fit.params[term], se=fit.bse[term] if fit.identified else np.nan,
                                           pvalue=fit.pvalues[term] if fit.identified else np.nan, identified=fit.identified,
                                           nobs=fit.nobs, resid_df=fit.df_resid, r2=fit.rsquared,
                                           sample_start=common.date.min(), sample_end=common.date.max(),
                                           target_max=common.target_date.max()))
            features = [*MARKET, 'log_n_docs', 'neg_sent', 'pos_sent', *optional]
            if len(frame[['y_rv', *features]].dropna()) <= len(features)+2:
                continue
            fit = regress(frame, 'y_rv', features, max(h-1, config['model']['hac_lags']))
            test = fit.wald_test('neg_sent = pos_sent', scalar=True) if fit.identified else None
            used = frame.loc[fit.model.data.row_labels]
            wald.append(dict(asset=asset, horizon=h, beta_neg=fit.params.neg_sent,
                             beta_pos=fit.params.pos_sent, identified=fit.identified,
                             nobs=fit.nobs, resid_df=fit.df_resid, sample_start=used.date.min(), sample_end=used.date.max(),
                             statistic=float(test.statistic) if test else np.nan, pvalue=float(test.pvalue) if test else np.nan))
    panel = make_panel(market, text)
    for asset, frame in panel.loc[panel.date <= cutoff].groupby('asset'):
        for outcome in ['ret', 'rv']:
            data = frame.set_index('date')[['sent_finbert', outcome]].dropna()
            total = len(data)
            if not total:
                granger.append(dict(asset=asset, outcome=outcome, pvalue=np.nan, conclusion='No paired observations'))
                continue
            segments = data.index.to_series().diff().ne(pd.Timedelta(days=1)).cumsum()
            data = max((part for _, part in data.groupby(segments)), key=len)
            if len(data) < 30:
                granger.append(dict(asset=asset, outcome=outcome, pvalue=np.nan,
                                    nobs=len(data), conclusion='VAR pending: fewer than 30 contiguous daily observations'))
                continue
            data = data.asfreq('D')
            sample = dict(nobs=len(data), sample_start=data.index.min(), sample_end=data.index.max(),
                          discarded_observations=total-len(data))
            maximum = min(config['model']['var_maxlags'], (len(data)-5)//3)
            lag = int(VAR(data).select_order(maxlags=maximum).selected_orders['aic'])
            if lag == 0:
                for caused, causing in [(outcome, 'sent_finbert'), ('sent_finbert', outcome)]:
                    granger.append(dict(asset=asset, outcome=outcome, causing=causing, caused=caused,
                                        lag=0, statistic=np.nan, pvalue=np.nan, conclusion='AIC selects no lags; no Granger test', **sample))
                continue
            fit = VAR(data).fit(lag)
            for caused, causing in [(outcome, 'sent_finbert'), ('sent_finbert', outcome)]:
                test = fit.test_causality(caused, [causing], kind='f')
                granger.append(dict(asset=asset, outcome=outcome, causing=causing, caused=caused,
                                    lag=lag, statistic=test.test_statistic, pvalue=test.pvalue,
                                    conclusion='Predictive lead (not structural causality)' if test.pvalue < .05 else 'No predictive lead at 5%', **sample))
    return {name: pd.DataFrame(rows) if rows else pd.DataFrame(columns=['pvalue'])
            for name, rows in [('regressions', tables), ('wald', wald), ('granger', granger)]}
