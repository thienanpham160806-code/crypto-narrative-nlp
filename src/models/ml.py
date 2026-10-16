"""Expanding forecasts; validation chooses settings and SHAP winner before test evaluation."""
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.models.panel import MARKET, TEXT, make_panel
from src.evaluation.oos import (diebold_mariano, clark_west, giacomini_white,
                                model_confidence_set, metrics, strategy)


def estimator(name, setting, seed):
    if name == 'EN':
        return make_pipeline(StandardScaler(), ElasticNet(alpha=setting, l1_ratio=.5, max_iter=10000, random_state=seed))
    if name == 'XGB':
        from xgboost import XGBRegressor
        return XGBRegressor(n_estimators=60, max_depth=setting, learning_rate=.05,
                            random_state=seed, n_jobs=1, objective='reg:squarederror')
    if name == 'LGBM':
        from lightgbm import LGBMRegressor
        return LGBMRegressor(n_estimators=60, num_leaves=setting, learning_rate=.05,
                             random_state=seed, n_jobs=1, verbosity=-1, deterministic=True, force_col_wise=True)
    raise ValueError(name)


def training_rows(frame, origin, horizon=1, embargo=0, window=None):
    """Strict requested purge: max(target_date) + horizon + embargo < origin."""
    if horizon < 1 or embargo < 0:
        raise ValueError('Invalid horizon or embargo')
    eligible = frame.loc[frame.target_date + pd.Timedelta(days=horizon+embargo) < origin]
    return eligible.tail(window) if window is not None else eligible


def expanding(frame, forecast_rows, features, name, setting, seed, refit_days=30,
              horizon=1, embargo=0, window=None, audit=None):
    if refit_days < 1 or not forecast_rows.date.is_monotonic_increasing:
        raise ValueError('Need positive refit interval and chronological forecast origins')
    predictions, baselines, cursor = [], [], 0
    while cursor < len(forecast_rows):
        origin = forecast_rows.iloc[cursor].date
        # Target-date maturity alone is weaker than the requested purge/embargo.
        train = training_rows(frame, origin, horizon, embargo, window)
        if len(train) < (window or 30):
            raise ValueError('Need at least 30 matured training labels')
        scale = train.y.std()
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError('Constant or invalid training target')
        fitted = estimator(name, setting, seed)
        fitted.fit(train[features], train.y / scale)
        stop = forecast_rows.date.searchsorted(origin + pd.Timedelta(days=refit_days))
        block = forecast_rows.iloc[cursor:stop]
        if audit is not None:
            audit.append(dict(origin=origin, train_target_max=train.target_date.max(),
                              train_origin_min=train.date.min(), horizon=horizon, embargo=embargo,
                              n_train=len(train), window=window or 'expanding'))
        predictions.extend(fitted.predict(block[features]) * scale)
        baselines.extend(training_rows(frame, date, horizon, embargo).y.mean() for date in block.date)
        cursor = stop
    return np.array(predictions), np.array(baselines)


def run_ml(market, text, config, refit_days=30):
    comparisons, forecasts, economic, importance, tuning = [], [], [], [], []
    audit, status, gw, mcs = [], [], [], []
    embargo = config['model'].get('embargo_days', 0)
    train_end = pd.Timestamp(config['split']['train_end'], tz='UTC')
    valid_end = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    if train_end >= valid_end:
        raise ValueError('train_end must precede valid_end')
    grids = {'EN': [.01, .1], 'XGB': [2, 3], 'LGBM': [7, 15]}
    for horizon in config['model']['horizons']:
        panel = make_panel(market, text, horizon)
        panel['log_n_docs'] = np.log1p(panel.n_docs)
        features_text = [*MARKET, *TEXT, *[f'attention_{k}' for k in config['nlp']['narratives']]]
        features_text += ['log_n_docs', *[c for c in panel if c.startswith(('disagreement', 'soft_attention_', 'attention_soft_', 'ucry_'))]]
        versions = [('market', MARKET), ('attention', [*MARKET, 'log_n_docs']), ('text', features_text)]
        for asset, asset_frame in panel.groupby('asset'):
            for target in ['ret', 'rv']:
                print(f'ML: {asset}, h={horizon}, target={target}', flush=True)
                frame = asset_frame.rename(columns={f'y_{target}': 'y'}).dropna(subset=[*features_text, 'y', 'target_date']).copy()
                valid = frame.loc[(frame.target_date > train_end) & (frame.target_date <= valid_end) & (frame.date >= train_end)]
                test = frame.loc[(frame.target_date > valid_end) & (frame.date >= valid_end)]
                valid = valid.loc[valid.date.map(lambda date: len(training_rows(frame, date, horizon, embargo)) >= 30)]
                test = test.loc[test.date.map(lambda date: len(training_rows(frame, date, horizon, embargo)) >= 30)]
                if len(valid) < 10 or len(test) < 10:
                    status.append(dict(asset=asset, target=target, horizon=horizon, status='insufficient validation/test coverage',
                                       n_valid=len(valid), n_test=len(test)))
                    continue
                chosen, validation_scores = {}, {}
                for name, settings in grids.items():
                    for version, features in versions:
                        scores = []
                        for setting in settings:
                            refits = []
                            pred, _ = expanding(frame.loc[frame.target_date <= valid_end], valid, features, name,
                                                setting, config['seed'], refit_days, horizon, embargo, audit=refits)
                            audit.extend(dict(asset=asset, target=target, model=name, version=version,
                                              phase='validation', setting=setting, **row) for row in refits)
                            loss = np.mean((valid.y-pred)**2)
                            scores.append((loss, setting))
                            tuning.append(dict(asset=asset, target=target, horizon=horizon, model=name,
                                               version=version, setting=setting, validation_mse=loss))
                        loss, setting = min(scores)
                        chosen[name, version] = setting
                        validation_scores[name, version] = loss
                winner = min(grids, key=lambda name: validation_scores[name, 'text'])
                # SHAP uses development data only; the winner is frozen before test predictions.
                development = training_rows(frame, valid_end, horizon, embargo)
                model = estimator(winner, chosen[winner, 'text'], config['seed'])
                scale = development.y.std()
                model.fit(development[features_text], development.y / scale)
                import shap
                sample = development[features_text].tail(100)
                if winner == 'EN':
                    transformed = model[0].transform(sample)
                    background = model[0].transform(development[features_text].head(100))
                    values = shap.LinearExplainer(model[1], background)(transformed).values * scale
                else:
                    values = shap.TreeExplainer(model)(sample).values * scale
                for feature, value in zip(features_text, np.mean(abs(values), axis=0)):
                    importance.append(dict(asset=asset, target=target, horizon=horizon, model=winner,
                                           feature=feature, mean_abs_shap=value, sample='development'))
                for name in grids:
                    paired = {}
                    for version, features in versions:
                        refits = []
                        pred, baseline = expanding(frame, test, features, name, chosen[name, version], config['seed'],
                                                   refit_days, horizon, embargo, audit=refits)
                        audit.extend(dict(asset=asset, target=target, model=name, version=version, phase='test', **row) for row in refits)
                        if target == 'rv':
                            pred = np.maximum(pred, 1e-12)
                        paired[version] = pred
                        comparisons.append(dict(asset=asset, target=target, horizon=horizon, model=name,
                                                version=version, nobs=len(test), **metrics(test.y, pred, baseline, target)))
                        for date, target_date, actual, prediction, mean in zip(test.date, test.target_date, test.y, pred, baseline):
                            forecasts.append(dict(asset=asset, target=target, horizon=horizon, model=name, version=version,
                                                  date=date, target_date=target_date, actual=actual, prediction=prediction, baseline=mean))
                        if target == 'ret' and horizon == 1:
                            if test.target_date.diff().dropna().eq(pd.Timedelta(days=1)).all():
                                economic.append(dict(asset=asset, model=name, version=version, **strategy(test.y, pred)))
                            else:
                                status.append(dict(asset=asset, target=target, horizon=horizon, status='strategy skipped: calendar gaps'))
                    # Serial tests use the longest contiguous test segment, never compress gaps.
                    groups = test.date.diff().ne(pd.Timedelta(days=1)).cumsum()
                    contiguous = max((part for _, part in test.groupby(groups)), key=len)
                    positions = test.index.get_indexer(contiguous.index)
                    if len(positions) > horizon+1:
                        for restricted in ['market', 'attention']:
                            comparison = {**diebold_mariano(contiguous.y.to_numpy(), paired[restricted][positions], paired['text'][positions], horizon),
                                          **clark_west(contiguous.y.to_numpy(), paired[restricted][positions], paired['text'][positions], horizon)}
                            comparisons[-1].update({f'{restricted}_{k}': v for k, v in comparison.items()})
                            if restricted == 'market':
                                comparisons[-1].update(comparison)
                        comparisons[-1].update(inference_nobs=len(positions), inference_start=contiguous.date.min(),
                                               inference_end=contiguous.date.max(), cw_scope='exploratory: tuned regularized/nonlinear models')
                    # GW requires bounded estimation windows; do not apply its asymptotics to expanding fits.
                    rolling = test.loc[test.date.map(lambda date: len(training_rows(frame, date, horizon, embargo)) >= 500)]
                    if len(rolling) >= 10:
                        predictions = {}
                        for version in ['market', 'text']:
                            features = dict(versions)[version]
                            refits = []
                            pred, _ = expanding(frame, rolling, features, name, chosen[name, version], config['seed'],
                                                refit_days, horizon, embargo, window=500, audit=refits)
                            audit.extend(dict(asset=asset, target=target, model=name, version=version, phase='GW', **row) for row in refits)
                            predictions[version] = np.maximum(pred, 1e-12) if target == 'rv' else pred
                        groups = rolling.date.diff().ne(pd.Timedelta(days=1)).cumsum()
                        segment = max((part for _, part in rolling.groupby(groups)), key=len)
                        pos = rolling.index.get_indexer(segment.index)
                        if len(pos) > horizon+2:
                            gw.append(dict(asset=asset, target=target, horizon=horizon, model=name, window=500,
                                           nobs=len(pos), sample_start=segment.date.min(), sample_end=segment.date.max(),
                                           **giacomini_white(segment.y, predictions['market'][pos], predictions['text'][pos], segment.ret, horizon)))
                    else:
                        status.append(dict(asset=asset, target=target, horizon=horizon, model=name, status='GW pending: needs 500 training rows'))
    forecast_table = pd.DataFrame(forecasts)
    if not forecast_table.empty:
        for keys, group in forecast_table.groupby(['asset', 'target', 'horizon', 'version']):
            wide = group.pivot(index='date', columns='model', values='prediction').dropna()
            actual = group.drop_duplicates('date').set_index('date').actual.reindex(wide.index)
            groups = wide.index.to_series().diff().ne(pd.Timedelta(days=1)).cumsum()
            segment = max((part for _, part in wide.groupby(groups)), key=len)
            if len(segment) >= 10:
                losses = segment.sub(actual.reindex(segment.index), axis=0).pow(2)
                result = model_confidence_set(losses, config['seed'], block_length=min(len(segment), max(10, keys[2])))
                mcs.extend(dict(asset=keys[0], target=keys[1], horizon=keys[2], version=keys[3],
                                nobs=len(segment), sample_start=segment.index.min(), sample_end=segment.index.max(), **row)
                           for row in result.to_dict('records'))
    return {'oos': pd.DataFrame(comparisons), 'forecasts': pd.DataFrame(forecasts),
            'strategy': pd.DataFrame(economic), 'shap': pd.DataFrame(importance), 'tuning': pd.DataFrame(tuning),
            'refit_audit': pd.DataFrame(audit), 'ml_status': pd.DataFrame(status),
            'gw': pd.DataFrame(gw), 'mcs': pd.DataFrame(mcs)}
