"""Run X2-X3 against explicit parquet paths, or reproducible synthetic fixtures."""
import argparse
from pathlib import Path

import pandas as pd
import yaml

from src.models.econometrics import run_econometrics
from src.models.ml import run_ml
from src.utils.common import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--market', required=True)
    parser.add_argument('--text', required=True)
    parser.add_argument('--config', default=str(ROOT / 'config/config.yaml'))
    parser.add_argument('--output', default=str(ROOT / 'outputs/tables'))
    parser.add_argument('--refit-days', type=int, default=30)
    args = parser.parse_args()
    if args.refit_days < 1:
        parser.error('--refit-days must be positive')
    config = yaml.safe_load(Path(args.config).read_text(encoding='utf-8'))
    market, text = pd.read_parquet(args.market), pd.read_parquet(args.text)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    for name, table in {**run_econometrics(market, text, config), **run_ml(market, text, config, args.refit_days)}.items():
        table.to_csv(output / f'{name}.csv', index=False)


if __name__ == '__main__':
    main()
