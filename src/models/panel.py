"""One place for calendar target alignment; forecasts are made at the end of day t."""
import pandas as pd
from src.utils.common import CFG

MARKET = ['ret', 'rv', 'logvol', *[f'ret_lag{i}' for i in range(1, 8)]]
TEXT = ['n_docs', 'sent_finbert', 'sent_lm', 'sent_hv', 'pos_sent', 'neg_sent', 'neg_accel']
TEXT_CORE = [name for name in TEXT if name != 'neg_accel']


def make_panel(market, text, horizon=1):
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError('horizon must be a positive integer')
    market, text = market.copy(), text.copy()
    for frame in [market, text]:
        frame['date'] = pd.to_datetime(frame.date, utc=True)
        if frame[['date', 'asset']].duplicated().any() or not (frame.date == frame.date.dt.floor('D')).all():
            raise ValueError('Expected unique UTC daily keys')
    attention = [f'attention_{name}' for name in CFG['nlp']['narratives']]
    if not set([*attention, *TEXT_CORE]).issubset(text):
        raise ValueError('text_daily does not match the contract')
    # ALL is a fallback only; never duplicate an asset-specific observation.
    keys = market[['date', 'asset']].reset_index(drop=True)
    specific = text.loc[text.asset != 'ALL']
    all_text = text.loc[text.asset == 'ALL'].drop(columns='asset')
    selected = keys.merge(specific, on=['date', 'asset'], how='left', validate='one_to_one', indicator=True)
    absent = selected.pop('_merge').eq('left_only')
    selected['missing_coin_text'] = False
    fallback = keys.loc[absent].merge(all_text, on='date', how='left', validate='many_to_one')
    fallback['missing_coin_text'] = True
    selected = pd.concat([selected.loc[~absent], fallback], ignore_index=True)
    panel = market.merge(selected, on=['date', 'asset'], validate='one_to_one')
    future = market[['date', 'asset', 'ret', 'rv', 'logvol']].rename(
        columns={c: f'y_{c}' for c in ['ret', 'rv', 'logvol']})
    future['target_date'] = future.date
    future['date'] = future.date - pd.Timedelta(days=horizon)
    return panel.merge(future, on=['date', 'asset'], how='left', validate='one_to_one').sort_values(['asset', 'date']).reset_index(drop=True)
