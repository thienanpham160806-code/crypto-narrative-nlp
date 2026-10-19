"""Synthetic data, never evidence of economic predictability. Signal at t affects return t+1."""
import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.utils.common import CFG


def make_fixtures(config=CFG):
    rng = np.random.default_rng(config['seed'])
    dates = pd.date_range(config['sample']['start'], config['sample']['end'], tz='UTC')
    markets, texts = [], []
    for asset in config['sample']['assets']:
        n = len(dates)
        sentiment = rng.uniform(-1, 1, n)
        returns = rng.normal(0, .012, n) + .006 * np.r_[0, sentiment[:-1]]
        close = 100 * np.exp(np.cumsum(returns))
        frame = pd.DataFrame({'date': dates, 'asset': asset, 'close': close, 'ret': returns,
                              'rv': np.exp(-8 + .3 * np.r_[0, np.maximum(-sentiment[:-1], 0)] + rng.normal(0, .2, n)),
                              'volume_usd': rng.lognormal(18, .3, n)})
        frame['logvol'] = np.log1p(frame.volume_usd)
        for lag in range(1, 8):
            frame[f'ret_lag{lag}'] = frame.ret.shift(lag)
        text = pd.DataFrame({'date': dates, 'asset': asset, 'n_docs': rng.integers(10, 100, n),
                             'sent_finbert': sentiment, 'sent_lm': np.clip(sentiment + rng.normal(0, .35, n), -1, 1),
                             'sent_hv': np.clip(sentiment + rng.normal(0, .6, n), -1, 1),
                             'pos_sent': np.maximum(sentiment, 0), 'neg_sent': np.maximum(-sentiment, 0)})
        attention = rng.dirichlet(np.ones(8), n)
        for i, narrative in enumerate(config['nlp']['narratives']):
            text[f'attention_{narrative}'] = attention[:, i]
        text['neg_accel'] = text.neg_sent.diff().fillna(0)
        markets.append(frame)
        texts.append(text)
    return pd.concat(markets, ignore_index=True), pd.concat(texts, ignore_index=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='tests/fixtures/generated')
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    market, text = make_fixtures()
    market.to_parquet(output / 'market_daily.parquet', index=False)
    text.to_parquet(output / 'text_daily.parquet', index=False)
