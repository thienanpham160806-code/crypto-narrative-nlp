import copy

import numpy as np
import pandas as pd

from src.evaluation.event_study import event_study, mm_fit
from src.models.robustness import adjust_pvalues, run_robustness
from src.utils.common import CFG
from test_pipeline import make_fixtures


def test_adjustments_and_development_only():
    corrected = adjust_pvalues(pd.DataFrame({'pvalue': [.01, .04, np.nan]}))
    np.testing.assert_allclose(corrected.p_holm[:2], [.02, .04])
    np.testing.assert_allclose(corrected.p_bh[:2], [.02, .04])
    config = copy.deepcopy(CFG)
    config['sample'].update(start='2024-06-01', end='2025-06-30', assets=['BTC'])
    config['split']['valid_end'] = '2025-04-30'
    config['model']['horizons'] = [1, 3]
    market, text = make_fixtures(config)
    first = run_robustness(market, text, config)
    cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
    market.loc[market.date > cutoff, ['ret', 'rv', 'logvol']] = 999
    text.loc[text.date > cutoff, 'sent_finbert'] = 999
    second = run_robustness(market, text, config)
    for name in first:
        pd.testing.assert_frame_equal(first[name], second[name])
    assert set(first['stationarity'].test) == {'ADF', 'KPSS'}
    assert 'dummy_2025_01' in set(first['robustness'].term)
    assert set(first['robustness'].period) == {'full', 'pre_2025', 'post_2025'}
    assert first['robustness_status'].status.str.startswith('pending').all()
    supplied = run_robustness(market, text, config, {'exclude_price_speculation': text})
    assert 'exclude_price_speculation' in set(supplied['robustness'].variant)
    assert supplied['robustness_status'].iloc[1].status == 'provided'


def test_weekend_strict_bar_and_missing_calendar():
    rng = np.random.default_rng(42)
    grid = pd.date_range('2025-01-01', periods=600, freq='h', tz='UTC')
    market = rng.normal(0, .002, len(grid))
    asset = .0001 + .7 * market + rng.normal(0, .001, len(grid))
    prices = pd.concat([pd.DataFrame({'date': grid, 'asset': name, 'close': 100*np.exp(np.cumsum(r))})
                        for name, r in [('BTC', market), ('ETH', asset)]])
    timestamp = pd.Timestamp('2025-01-18 12:00', tz='UTC')
    docs = pd.DataFrame({'doc_id': ['exact', 'between'], 'asset': 'ETH',
                         'public_ts_utc': [timestamp, timestamp + pd.Timedelta(minutes=30)]})
    result = event_study(docs, prices)
    assert (result['events'].day0 == timestamp + pd.Timedelta(hours=1)).all()
    assert len(result['events']) == 2
    missing = prices.loc[prices.date != timestamp + pd.Timedelta(hours=1)]
    result = event_study(docs, missing)
    assert 'car_0_1' not in result['events']
    x = pd.Series(rng.normal(size=100))
    fit = mm_fit(pd.Series(np.zeros(100)), x)
    assert fit is not None
