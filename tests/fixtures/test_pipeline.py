import copy
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.data.market import daily_market, fetch_bars
from src.models.panel import make_panel, MARKET
from src.models.econometrics import run_econometrics
from src.models.ml import expanding, run_ml
from src.evaluation.oos import diebold_mariano, strategy, metrics
from src.utils.common import CFG

spec = importlib.util.spec_from_file_location('make_fixtures', Path(__file__).with_name('make_fixtures.py'))
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
make_fixtures = fixture_module.make_fixtures


@pytest.fixture
def config():
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2023-01-01', end='2023-12-31', assets=['BTC'])
    config['split'].update(train_end='2023-08-31', valid_end='2023-10-31')
    config['model'].update(horizons=[1], var_maxlags=3)
    return config


def test_fixture_signal_and_contract(config):
    market, text = make_fixtures(config)
    other_market, other_text = make_fixtures(config)
    pd.testing.assert_frame_equal(text, other_text)
    assert len([c for c in text if c.startswith('attention_')]) == 8
    assert np.allclose(text.filter(like='attention_').sum(axis=1), 1)
    panel = make_panel(market, text)
    assert panel.sent_finbert.corr(panel.y_ret) > .15


def test_calendar_target_and_all_fallback(config):
    market, text = make_fixtures(config)
    market = market.drop(index=10)
    panel = make_panel(market, text, 3)
    assert pd.isna(panel.loc[panel.date == pd.Timestamp('2023-01-08', tz='UTC'), 'y_ret']).all()
    specific = text.iloc[[0]].copy()
    all_text = text.copy()
    all_text.asset = 'ALL'
    all_text.sent_finbert = 0
    panel = make_panel(market, pd.concat([all_text, specific]))
    assert panel.iloc[0].sent_finbert == specific.iloc[0].sent_finbert
    assert panel.iloc[1].sent_finbert == 0
    with pytest.raises(ValueError, match='unique'):
        make_panel(market, pd.concat([text, text]))


def test_future_features_do_not_change_past_panel(config):
    market, text = make_fixtures(config)
    cutoff = pd.Timestamp('2023-06-01', tz='UTC')
    original = make_panel(market, text, 7)
    market.loc[market.date > cutoff, ['ret', 'rv', 'close']] *= 100
    text.loc[text.date > cutoff, 'sent_finbert'] = 999
    changed = make_panel(market, text, 7)
    columns = [c for c in original if not c.startswith('y_') and c != 'target_date']
    pd.testing.assert_frame_equal(original.loc[original.date <= cutoff, columns], changed.loc[changed.date <= cutoff, columns])
    row = original.iloc[40]
    assert row.target_date == row.date + pd.Timedelta(days=7)


def test_market_returns_rv_lags():
    dates = pd.date_range('2023-01-01', periods=73, freq='h', tz='UTC')
    hourly = pd.DataFrame({'date': dates, 'close': np.exp(np.arange(73)*.001)})
    daily = pd.DataFrame({'date': dates[::24], 'close': np.exp(np.arange(4)*.024), 'volume': 100})
    result = daily_market(daily, hourly, 'BTC')
    assert np.isnan(result.rv.iloc[0])
    assert np.isclose(result.rv.iloc[1], 24*.001**2)
    assert np.isnan(result.rv.iloc[-1])
    assert np.isclose(result.ret.iloc[1], .024)
    assert np.isclose(result.ret_lag1.iloc[2], result.ret.iloc[1])
    missing = hourly.drop(index=24)
    assert np.isnan(daily_market(daily, missing, 'BTC').rv.iloc[1])


def test_fetch_pagination_cache_and_gap(tmp_path):
    class Exchange:
        calls = 0
        def parse_timeframe(self, timeframe):
            return 3600
        def fetch_ohlcv(self, symbol, timeframe, since, limit):
            self.calls += 1
            return [[since+i*3600000, 1, 2, 1, 2, 10] for i in range(2)]
    exchange = Exchange()
    args = (exchange, 'BTC/USDT', '1h', pd.Timestamp('2023-01-01', tz='UTC'), pd.Timestamp('2023-01-01 04:00', tz='UTC'), tmp_path/'cache.parquet')
    frame = fetch_bars(*args)
    assert len(frame) == 4 and exchange.calls == 2
    pd.testing.assert_frame_equal(frame.reset_index(drop=True), fetch_bars(*args).reset_index(drop=True))
    assert exchange.calls == 2
    frame.drop(index=1).to_parquet(args[-1])
    with pytest.warns(UserWarning, match='missing hourly'):
        assert len(fetch_bars(*args)) == 3
    frame.loc[0, 'close'] = np.nan
    frame.to_parquet(args[-1])
    with pytest.raises(ValueError, match='Invalid OHLCV'):
        fetch_bars(*args)


def test_econometrics_ignores_test_labels(config):
    market, text = make_fixtures(config)
    original = run_econometrics(market, text, config)
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    market.loc[market.date > cutoff, ['ret', 'rv']] = 999
    text.loc[text.date > cutoff, 'sent_finbert'] = 999
    changed = run_econometrics(market, text, config)
    for key in original:
        pd.testing.assert_frame_equal(original[key], changed[key])
    assert len(original['wald']) == 1
    assert len(original['granger']) == 4
    coef = original['regressions'].query("term == 'sent_finbert' and target == 'ret'").coef.iloc[0]
    assert coef > 0
    market.loc[market.date == pd.Timestamp('2023-03-24', tz='UTC'), 'rv'] = np.nan
    with_gap = run_econometrics(market, text, config)['granger']
    rv_tests = with_gap.loc[with_gap.outcome == 'rv']
    assert (rv_tests.sample_start == pd.Timestamp('2023-03-25', tz='UTC')).all()
    assert (rv_tests.discarded_observations > 0).all()


def test_expanding_uses_only_matured_labels(config):
    market, text = make_fixtures(config)
    frame = make_panel(market, text, 7).rename(columns={'y_ret': 'y'}).dropna()
    origin = pd.Timestamp('2023-09-01', tz='UTC')
    rows = frame.loc[frame.date == origin]
    first, _ = expanding(frame, rows, MARKET, 'EN', .01, config['seed'])
    frame.loc[frame.target_date > origin, 'y'] = 999
    second, _ = expanding(frame, rows, MARKET, 'EN', .01, config['seed'])
    np.testing.assert_array_equal(first, second)


def test_ml_all_models_and_outputs(config):
    market, text = make_fixtures(config)
    result = run_ml(market, text, config)
    assert len(result['oos']) == 12
    assert set(result['oos'].model) == {'EN', 'XGB', 'LGBM'}
    assert set(result['shap']['sample']) == {'development'}
    assert result['oos'].rmse.notna().all()
    assert (result['forecasts'].target_date > pd.Timestamp(config['split']['valid_end'], tz='UTC')).all()
    assert len(result['strategy']) == 6
    assert (result['strategy'].fee_bps == 10).all()
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    market.loc[market.date > cutoff, ['ret', 'rv']] *= 2
    text.loc[text.date > cutoff, 'sent_finbert'] *= -1
    changed = run_ml(market, text, config)
    pd.testing.assert_frame_equal(result['tuning'], changed['tuning'])
    pd.testing.assert_frame_equal(result['shap'], changed['shap'])


def test_dm_metrics_and_costs():
    actual = np.linspace(-.01, .01, 100)
    result = diebold_mariano(actual, np.zeros(100), actual*.9)
    assert result['dm'] > 0 and result['dm_pvalue'] < .05
    assert np.isnan(diebold_mariano(actual, actual, actual)['dm'])
    assert metrics(actual, actual, np.zeros(100), 'ret')['r2_oos'] == 1
    costs = strategy(np.zeros(3), [1, -1, 1])
    assert costs['turnover'] == 4
    assert costs['net_return'] < 0
