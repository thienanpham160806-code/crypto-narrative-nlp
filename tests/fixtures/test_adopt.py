"""Offline numerical and timing checks for ADOPT P1–P3."""
import copy

import numpy as np
import pandas as pd
import pytest

from src.evaluation.oos import clark_west, diebold_mariano, giacomini_white, model_confidence_set, metrics
from src.models.ml import expanding, training_rows
from src.models.run import run_analysis
from src.models.panel import MARKET, make_panel
from src.models.quantile import run_quantiles
from src.models.econometrics import attach_ucry, run_econometrics
from src.evaluation.report import write_report
from src.utils.common import CFG
from test_pipeline import make_fixtures


@pytest.mark.parametrize('h,statistic,pvalue', [
    (1, .5881979787732637, .5597904728437016),
    (3, .5328275376469148, .5971761989144784),
    (7, .44735510983286686, .6570935465233603)])
def test_dm_hln_reference(h, statistic, pvalue):
    # Reference arithmetic: johntwk/Diebold-Mariano-Test dm_test.py lines 140–155.
    # Constants evaluated locally from the published formula; no downloaded code.
    rng = np.random.default_rng(17)
    y, first, second = [rng.normal(size=40).round(6) for _ in range(3)]
    result = diebold_mariano(y, first, second, h)
    assert result['dm'] == pytest.approx(statistic, abs=1e-12)
    assert result['dm_pvalue'] == pytest.approx(pvalue, abs=1e-12)
    assert result['dm'] == pytest.approx(result['dm_uncorrected']*result['dm_hln_factor'])


def test_cw_gw_mcs_and_ct():
    rng = np.random.default_rng(42)
    signal = rng.normal(size=300)
    y = signal + rng.normal(scale=.1, size=300)
    cw = clark_west(y, np.zeros(300), signal, 3)
    assert cw['cw'] > 0 and cw['cw_pvalue'] < .001
    gw = giacomini_white(y, np.zeros(300), signal, signal, 3)
    assert gw['gw_df'] == 2 and gw['gw_pvalue'] < .001
    losses = pd.DataFrame({'EN': (y-signal)**2, 'XGB': y**2, 'LGBM': (y+signal)**2})
    mcs = model_confidence_set(losses, 42, bootstrap=199)
    pd.testing.assert_frame_equal(mcs, model_confidence_set(losses, 42, bootstrap=199))
    assert mcs.set_index('model').included.to_dict() == {'EN': True, 'XGB': False, 'LGBM': False}
    equal = model_confidence_set(pd.DataFrame({'a': y**2, 'b': y**2}), 42, bootstrap=99)
    assert equal.included.all()
    with pytest.raises(ValueError, match='bootstrap'):
        model_confidence_set(losses.head(10), 42, block_length=10)
    baseline = np.array([0., .5, 1.])
    result = metrics([1, 2, 3], [1, 1, 2], baseline, 'ret')
    assert result['r2_oos_ct'] == pytest.approx(1-2/7.25)
    with pytest.raises(ValueError, match='finite'):
        clark_west([1, np.nan], [0, 0], [0, 0])


def test_every_refit_has_strict_purge_embargo():
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2023-01-01', end='2024-12-31', assets=['BTC'])
    market, text = make_fixtures(config)
    for horizon in [1, 3, 7]:
        frame = make_panel(market, text, horizon).rename(columns={'y_ret': 'y'}).dropna()
        for embargo in [0, 2]:
            audit = []
            rows = frame.tail(35)
            expanding(frame, rows, MARKET, 'EN', .01, 42, refit_days=10,
                      horizon=horizon, embargo=embargo, window=500, audit=audit)
            for refit in audit:
                assert refit['train_target_max']+pd.Timedelta(days=horizon+embargo) < refit['origin']
                assert refit['n_train'] == 500
                eligible = training_rows(frame, refit['origin'], horizon, embargo, 500)
                assert eligible.target_date.max() == refit['train_target_max']


def test_quantiles_calendar_windows_and_test_poisoning():
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2023-01-01', end='2024-09-30', assets=['BTC'])
    config['split']['valid_end'] = '2024-06-30'
    config['model']['horizons'] = [1]
    market, text = make_fixtures(config)
    original = run_quantiles(market, text, config)
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    market.loc[market.date > cutoff, 'rv'] = 999
    text.loc[text.date > cutoff, ['neg_sent', 'pos_sent']] = 999
    changed = run_quantiles(market, text, config)
    for key in original:
        pd.testing.assert_frame_equal(original[key], changed[key])
    assert set(original['quantiles'].tau) == {.1, .5, .9}
    rolling = original['rolling_quantiles']
    assert not rolling.empty
    assert ((rolling.window_end-rolling.window_start).dt.days == 499).all()
    assert (rolling.target_max <= cutoff).all()
    ends = rolling.window_end.drop_duplicates().sort_values()
    assert ends.diff().dropna().dt.days.eq(20).all()


def test_optional_features_ucry_release_and_report(tmp_path, monkeypatch):
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2023-01-01', end='2023-03-31', assets=['BTC'])
    market, text = make_fixtures(config)
    text['disagreement'] = .5
    for name in config['nlp']['narratives']:
        text[f'soft_attention_{name}'] = text[f'attention_{name}']
    ucry = pd.DataFrame({'date': [pd.Timestamp('2023-01-02', tz='UTC')],
                         'week_end': [pd.Timestamp('2023-01-01', tz='UTC')],
                         'ucry_policy': [100.], 'ucry_price': [101.]})
    controlled = attach_ucry(text, ucry)
    panel = make_panel(market, controlled)
    assert 'disagreement' in panel and 'soft_attention_regulation' in panel
    assert panel.ucry_policy.notna().sum() == 1
    ucry['date'] = pd.Timestamp('2023-01-01', tz='UTC')
    with pytest.raises(ValueError, match='release'):
        attach_ucry(text, ucry)
    monkeypatch.setattr('src.evaluation.report.paper_figures', lambda *args: [])
    tables = {'oos': pd.DataFrame()}
    write_report(market, text, config, tables, tmp_path, tmp_path/'figures')
    report = (tmp_path/'README.md').read_text(encoding='utf-8')
    assert 'SYNTHETIC' in report and '100.00%' in report
    assert 'Unavailable' in report and 'RQ5' in report


def test_partial_real_sample_produces_pending_tables(tmp_path, monkeypatch):
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2024-03-01', end='2024-04-15', assets=['BTC'])
    config['model']['horizons'] = [1]
    market, text = make_fixtures(config)
    monkeypatch.setattr('src.evaluation.report.paper_figures', lambda *args: [])
    tables = run_analysis(market, text, config, tmp_path, tmp_path/'figures', real=True)
    assert tables['oos'].empty
    assert tables['ml_status'].status.str.contains('insufficient').all()
    assert 'REAL' in (tmp_path/'README.md').read_text(encoding='utf-8')
    assert (tmp_path/'regressions.csv').exists()
    assert pd.read_csv(tmp_path/'oos.csv').empty


def test_unidentified_regressions_withhold_significance():
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2023-01-01', end='2023-12-31', assets=['BTC'])
    config['model']['horizons'] = [1]
    market, text = make_fixtures(config)
    text['n_docs'] = 1
    tables = run_econometrics(market, text, config)
    unidentifiable = tables['regressions'].loc[~tables['regressions'].identified]
    assert not unidentifiable.empty
    assert unidentifiable.pvalue.isna().all() and unidentifiable.se.isna().all()
    assert tables['wald'].pvalue.isna().all()
