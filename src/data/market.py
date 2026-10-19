"""Binance completed UTC candles; quote volume is approximated by close * base volume."""
import argparse
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from src.utils.common import CFG, ROOT


def fetch_bars(exchange, symbol, timeframe, start, end, cache):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    cache = Path(cache)
    cached = cache.exists()
    if cached:
        frame = pd.read_parquet(cache)
    else:
        cursor, stop = int(start.timestamp() * 1000), int(end.timestamp() * 1000)
        step = exchange.parse_timeframe(timeframe) * 1000
        rows = []
        while cursor < stop:
            batch = exchange.fetch_ohlcv(symbol, timeframe, since=cursor, limit=1000)
            if not batch:
                raise ValueError(f"Missing candles for {symbol} at {cursor}")
            if batch[-1][0] < cursor:
                raise ValueError("Exchange pagination did not advance")
            rows.extend(batch)
            cursor = batch[-1][0] + step
        frame = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        frame['date'] = pd.to_datetime(frame.pop('timestamp'), unit='ms', utc=True)
        frame = frame.drop_duplicates('date').sort_values('date')
    frame = frame.loc[(frame.date >= start) & (frame.date < end)].copy()
    expected = pd.date_range(start, end, freq=timeframe.replace('1d', '1D'), inclusive='left')
    if list(frame.date) != list(expected):
        if timeframe != '1h' or not frame.date.isin(expected).all() or frame.empty:
            raise ValueError(f"Incomplete {timeframe} candles for {symbol}")
        warnings.warn(f'{symbol}: {len(expected)-len(frame)} missing hourly candles; affected RV stays missing', stacklevel=2)
    if not np.isfinite(frame[['open', 'high', 'low', 'close', 'volume']]).all().all() or (frame[['open', 'high', 'low', 'close']] <= 0).any().any() or (frame.volume < 0).any():
        raise ValueError("Invalid OHLCV")
    if not cached:
        cache.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(cache, index=False)
    return frame


def daily_market(daily, hourly, asset):
    daily, hourly = daily.sort_values('date').copy(), hourly.sort_values('date').copy()
    if daily.date.duplicated().any() or hourly.date.duplicated().any():
        raise ValueError("Duplicate candles")
    hourly['squared_return'] = np.log(hourly.close).diff().pow(2).where(hourly.date.diff() == pd.Timedelta(hours=1))
    groups = hourly.groupby(hourly.date.dt.floor('D'))
    rv = groups.squared_return.sum(min_count=24)
    rv = rv.where(groups.size() == 24)
    daily['asset'] = asset
    daily['ret'] = np.log(daily.close).diff()
    daily['rv'] = daily.date.map(rv)
    daily['volume_usd'] = daily.close * daily.volume
    daily['logvol'] = np.log1p(daily.volume_usd)
    for lag in range(1, 8):
        daily[f'ret_lag{lag}'] = daily.ret.shift(lag)
    return daily[['date', 'asset', 'close', 'ret', 'rv', 'volume_usd', 'logvol', *[f'ret_lag{i}' for i in range(1, 8)]]]


def main():
    import ccxt
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(ROOT / 'data/processed/market_daily.parquet'))
    args = parser.parse_args()
    exchange = ccxt.binance({'enableRateLimit': True})
    start = pd.Timestamp(CFG['sample']['start'], tz='UTC')
    end = pd.Timestamp(CFG['sample']['end'], tz='UTC') + pd.Timedelta(days=1)
    if end > pd.Timestamp.now(tz='UTC').floor('D'):
        raise ValueError('Sample includes an unfinished day')
    frames = []
    # Warm-up supplies returns and all seven lags for the requested first day.
    warmup = start - pd.Timedelta(days=9)
    for asset in CFG['sample']['assets']:
        bars = [fetch_bars(exchange, f'{asset}/USDT', tf, warmup, end,
                           ROOT / f'data/raw/{asset}_{tf}_{warmup:%Y%m%d}_{end:%Y%m%d}.parquet')
                for tf in ['1d', '1h']]
        frame = daily_market(*bars, asset)
        frames.append(frame.loc[frame.date >= start])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(frames, ignore_index=True).to_parquet(output, index=False)


if __name__ == '__main__':
    main()
