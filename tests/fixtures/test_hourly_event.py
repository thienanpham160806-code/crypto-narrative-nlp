"""Offline timing and clustering checks for real hourly event analysis."""
import numpy as np
import pandas as pd

from src.evaluation.hourly_event import event_documents, event_observations, clustered_tests, timing_comparison


def test_hourly_t0_placebo_and_train_only_terciles():
    hours = pd.date_range('2023-01-01', periods=550, freq='h', tz='UTC')
    ret = np.full(len(hours), .001)
    prices = {'BTC': pd.DataFrame({'close': 100*np.exp(np.cumsum(ret)), 'volume': 10.}, index=hours),
              'ETH': pd.DataFrame({'close': 80*np.exp(np.cumsum(ret)), 'volume': 20.}, index=hours)}
    docs = pd.DataFrame({'doc_id': ['train1', 'train2', 'train3', 'test'], 'source': 'gdelt',
                         'lang': 'en', 'is_canonical': True,
                         'asset_tags': [[], ['ETH'], [], []],
                         'public_ts_utc': [hours[200], hours[210], hours[220], hours[300]+pd.Timedelta(minutes=30, nanoseconds=123)],
                         'published_at_utc': [pd.NaT, pd.NaT, pd.NaT, hours[299]],
                         'first_seen_utc': [hours[200], hours[210], hours[220], hours[300]+pd.Timedelta(minutes=30, nanoseconds=123)]})
    scores = pd.DataFrame({'doc_id': docs.doc_id, 'finbert_sentiment': [-.8, 0., .8, 999.],
                           'lm_net': [-.5, 0., .5, 999.], 'narrative': ['regulation']*4})
    articles, cuts = event_documents(docs, scores, '2023-01-10')
    assert cuts[1] < 1
    assert articles.loc[articles.doc_id.eq('train1'), 'asset'].iloc[0] == 'BTC'
    assert articles.loc[articles.doc_id.eq('train2'), 'lm_tone'].iloc[0] == 'neutral'
    events = event_observations(articles, prices)
    event = events.loc[events.doc_id.eq('test')].iloc[0]
    assert event.t0 == hours[301]
    assert np.isnan(event.get('placebo_car_0_24', np.nan))
    pairs, timing = timing_comparison(articles, prices)
    assert len(pairs) == 1 and pairs.t0_published.iloc[0] == hours[300]
    assert timing.n_unique_articles.iloc[0] == 1


def test_event_tests_use_day_clusters():
    days = pd.date_range('2023-01-01', periods=6, tz='UTC')
    events = pd.DataFrame({'event_day': np.repeat(days, 2), 'source': ['gdelt']*12,
                           'finbert_tercile': ['negative']*12,
                           'lm_tone': ['negative']*12, 'narrative': ['security_hacks']*12,
                           'car_0_1': np.repeat(np.arange(1, 7)*.01, 2),
                           'scar_0_1': np.repeat(np.arange(1, 7)*.1, 2)})
    result = clustered_tests(events)
    overall = result.loc[(result.grouping == 'all') & (result.metric == 'car')].iloc[0]
    assert overall.n_events == 12 and overall.n_days == 6
    assert overall.p_t < .05 and overall.p_bmp < .05
