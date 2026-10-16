"""Run X2-X3 against explicit parquet paths, or reproducible synthetic fixtures."""
import argparse
from pathlib import Path

import pandas as pd
import yaml

from src.models.econometrics import run_econometrics
from src.models.ml import run_ml
from src.models.robustness import run_robustness, adjust_pvalues
from src.utils.common import ROOT


def main(real=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--market', default=str(ROOT / 'data/processed/market_daily.parquet') if real else None, required=not real)
    parser.add_argument('--text', default=str(ROOT / 'data/processed/text_daily.parquet') if real else None, required=not real)
    parser.add_argument('--config', default=str(ROOT / 'config/config.yaml'))
    parser.add_argument('--output', default=str(ROOT / 'outputs/tables' / ('real' if real else 'synthetic')))
    parser.add_argument('--source-weighted-text')
    parser.add_argument('--exclude-price-text')
    parser.add_argument('--refit-days', type=int, default=30)
    args = parser.parse_args()
    if args.refit_days < 1:
        parser.error('--refit-days must be positive')
    config = yaml.safe_load(Path(args.config).read_text(encoding='utf-8'))
    if real and not Path(args.text).is_file():
        print(f'Waiting for real text_daily: {args.text}', flush=True)
        return
    market, text = pd.read_parquet(args.market), pd.read_parquet(args.text)
    variants = {name: pd.read_parquet(path) for name, path in [
        ('source_weighted', args.source_weighted_text), ('exclude_price_speculation', args.exclude_price_text)] if path}
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    print('Running econometrics', flush=True)
    for name, table in run_econometrics(market, text, config).items():
        adjust_pvalues(table).to_csv(output / f'{name}.csv', index=False, encoding='utf-8')
    for name, table in run_robustness(market, text, config, variants).items():
        table.to_csv(output / f'{name}.csv', index=False, encoding='utf-8')
    print('Running expanding forecasts', flush=True)
    for name, table in run_ml(market, text, config, args.refit_days).items():
        if 'dm_pvalue' in table:
            corrected = adjust_pvalues(table.rename(columns={'dm_pvalue': 'pvalue'}))
            table = corrected.rename(columns={'pvalue': 'dm_pvalue', 'p_holm': 'dm_p_holm', 'p_bh': 'dm_p_bh'})
        table.to_csv(output / f'{name}.csv', index=False, encoding='utf-8')
    (output / 'INTERPRETATION.md').write_text(
        ('Real inputs supplied; provenance and NLP validation require upstream audit.\n' if real else
         'Synthetic inputs: these tables validate code, not economic predictability.\n') +
        'Regression coefficients describe conditional predictive associations, not causal effects.\n'
        'ADF rejects a unit root; KPSS rejects level stationarity. Conflicting tests require caution.\n'
        'Holm controls family-wise error; BH controls false discoveries within each exported table.\n'
        'Robustness compares horizons and periods with momentum and raw document-count controls.\n'
        'Wald compares negative and positive effects; Granger tests predictive direction only.\n'
        'OOS and strategy tables measure incremental forecast value and returns after stated fees.\n'
        'SHAP explains fitted predictions; tuning tables record development-only choices.\n', encoding='utf-8')


if __name__ == '__main__':
    main()
