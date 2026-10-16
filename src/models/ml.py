"""Expanding forecasts; validation chooses settings and SHAP winner before test evaluation."""
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.models.panel import MARKET, TEXT, make_panel
from src.evaluation.oos import diebold_mariano, metrics, strategy


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


def expanding(frame, forecast_rows, features, name, setting, seed, refit_days=30):
    predictions, baselines, fitted = [], [], None
    last_fit = None
    for row in forecast_rows.itertuples():
        # A target dated t is observable at the end of t, exactly our forecast origin.
        train = frame.loc[frame.target_date <= row.date]
        if len(train) < 30:
            raise ValueError('Need at least 30 matured training labels')
        if fitted is None or (row.date-last_fit).days >= refit_days:
            fitted = estimator(name, setting, seed)
            scale = train.y.std()
            if not np.isfinite(scale) or scale <= 0:
                raise ValueError('Constant or invalid training target')
            fitted.fit(train[features], train.y / scale)
            last_fit = row.date
        predictions.append(float(fitted.predict(frame.loc[[row.Index], features])[0]) * scale)
        baselines.append(train.y.mean())
    return np.array(predictions), np.array(baselines)


def run_ml(market, text, config, refit_days=30):
    comparisons, forecasts, economic, importance, tuning = [], [], [], [], []
    train_end = pd.Timestamp(config['split']['train_end'], tz='UTC')
    valid_end = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    if train_end >= valid_end:
        raise ValueError('train_end must precede valid_end')
    grids = {'EN': [.01, .1], 'XGB': [2, 3], 'LGBM': [7, 15]}
    for horizon in config['model']['horizons']:
        panel = make_panel(market, text, horizon)
        features_text = [*MARKET, *TEXT, *[c for c in panel if c.startswith('attention_')]]
        for asset, asset_frame in panel.groupby('asset'):
            for target in ['ret', 'rv']:
                frame = asset_frame.rename(columns={f'y_{target}': 'y'}).dropna(subset=[*features_text, 'y', 'target_date']).copy()
                valid = frame.loc[(frame.target_date > train_end) & (frame.target_date <= valid_end) & (frame.date >= train_end)]
                test = frame.loc[(frame.target_date > valid_end) & (frame.date >= valid_end)]
                if len(valid) < 10 or len(test) < 10:
                    raise ValueError('Need at least ten validation and test forecasts')
                chosen, validation_scores = {}, {}
                for name, settings in grids.items():
                    for version, features in [('market', MARKET), ('text', features_text)]:
                        scores = []
                        for setting in settings:
                            pred, _ = expanding(frame.loc[frame.target_date <= valid_end], valid, features, name,
                                                setting, config['seed'], refit_days)
                            loss = np.mean((valid.y-pred)**2)
                            scores.append((loss, setting))
                            tuning.append(dict(asset=asset, target=target, horizon=horizon, model=name,
                                               version=version, setting=setting, validation_mse=loss))
                        loss, setting = min(scores)
                        chosen[name, version] = setting
                        validation_scores[name, version] = loss
                winner = min(grids, key=lambda name: validation_scores[name, 'text'])
                # SHAP uses development data only; the winner is frozen before test predictions.
                development = frame.loc[frame.target_date <= valid_end]
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
                    for version, features in [('market', MARKET), ('text', features_text)]:
                        pred, baseline = expanding(frame, test, features, name, chosen[name, version], config['seed'], refit_days)
                        if target == 'rv':
                            pred = np.maximum(pred, 1e-12)
                        paired[version] = pred
                        comparisons.append(dict(asset=asset, target=target, horizon=horizon, model=name,
                                                version=version, nobs=len(test), **metrics(test.y, pred, baseline, target)))
                        for date, target_date, actual, prediction, mean in zip(test.date, test.target_date, test.y, pred, baseline):
                            forecasts.append(dict(asset=asset, target=target, horizon=horizon, model=name, version=version,
                                                  date=date, target_date=target_date, actual=actual, prediction=prediction, baseline=mean))
                        if target == 'ret' and horizon == 1:
                            if not test.target_date.diff().dropna().eq(pd.Timedelta(days=1)).all():
                                raise ValueError('Strategy requires contiguous daily forecasts')
                            economic.append(dict(asset=asset, model=name, version=version, **strategy(test.y, pred)))
                    comparison = diebold_mariano(test.y.to_numpy(), paired['market'], paired['text'], horizon)
                    for record in comparisons[-2:]:
                        record.update(comparison)
    return {'oos': pd.DataFrame(comparisons), 'forecasts': pd.DataFrame(forecasts),
            'strategy': pd.DataFrame(economic), 'shap': pd.DataFrame(importance), 'tuning': pd.DataFrame(tuning)}
