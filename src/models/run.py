"""Run X2-X3 against explicit parquet paths, or reproducible synthetic fixtures."""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

import pandas as pd
import yaml

from src.models.econometrics import run_econometrics, attach_ucry
from src.models.ml import run_ml
from src.models.robustness import run_robustness, adjust_pvalues
from src.models.quantile import run_quantiles
from src.evaluation.report import write_report
from src.evaluation.hourly_event import run_real_events, hourly_prices
from src.utils.common import ROOT


def correct_tests(table):
    for column in list(table):
        if column == 'pvalue':
            table = adjust_pvalues(table)
        elif column.endswith('_pvalue'):
            prefix = column[:-7]
            adjusted = adjust_pvalues(pd.DataFrame({'pvalue': table[column]}))
            table[f'{prefix}_p_holm'] = adjusted.p_holm
            table[f'{prefix}_p_bh'] = adjusted.p_bh
    return table


def run_analysis(market, text, config, output, figures, real=False, refit_days=30, variants=None, ucry=None,
                 event_inputs=None):
    """Shared offline entry point for CLI and notebook; return all research tables."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    tables = {}
    for label, call in [
        ('econometrics', lambda: run_econometrics(market, text, config)),
        ('robustness', lambda: run_robustness(market, text, config, variants)),
        ('quantiles', lambda: run_quantiles(market, text, config)),
        ('expanding forecasts', lambda: run_ml(market, text, config, refit_days))]:
        print(f'Running {label}', flush=True)
        for name, table in call().items():
            table = correct_tests(table)
            tables[name] = table
            table.to_csv(output/f'{name}.csv', index=False, encoding='utf-8')
    if ucry is not None:
        controlled = run_econometrics(market, attach_ucry(text, ucry), config)
        for name in ['regressions', 'wald']:
            tables[f'ucry_{name}'] = correct_tests(controlled[name])
    if real and event_inputs is not None:
        print('Running hourly events', flush=True)
        documents, scores, prices = event_inputs
        tables.update(run_real_events(documents, scores, prices, config['split']['train_end'], output, figures))
    write_report(market, text, config, tables, output, figures, real)
    if real:
        from src.evaluation.report import write_results
        write_results(tables, output)
    return tables


def main(real=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--market', default=str(ROOT / 'data/processed/market_daily.parquet') if real else None, required=not real)
    parser.add_argument('--text', default=str(ROOT / 'data/processed/text_daily.parquet') if real else None, required=not real)
    parser.add_argument('--config', default=str(ROOT / 'config/config.yaml'))
    parser.add_argument('--output', default=str(ROOT / 'outputs/tables' / ('real' if real else 'synthetic')))
    parser.add_argument('--source-weighted-text')
    parser.add_argument('--exclude-price-text')
    parser.add_argument('--refit-days', type=int, default=30)
    parser.add_argument('--figures')
    parser.add_argument('--ucry', default=str(ROOT/'data/processed/ucry_daily.parquet') if real else None)
    parser.add_argument('--watch', action='store_true', help='Real runner: recheck input changes every 30 minutes')
    parser.add_argument('--poll-seconds', type=int, default=1800)
    args = parser.parse_args()
    if args.refit_days < 1:
        parser.error('--refit-days must be positive')
    if args.watch and (not real or args.poll_seconds < 1):
        parser.error('--watch requires real mode and a positive poll interval')
    config = yaml.safe_load(Path(args.config).read_text(encoding='utf-8'))
    code_paths = [Path(__file__), ROOT/'src/models/ml.py', ROOT/'src/evaluation/report.py',
                  ROOT/'src/evaluation/hourly_event.py']
    code_hash = hashlib.sha256(b''.join(path.read_bytes() for path in code_paths)).hexdigest()
    while True:
        try:
            if not Path(args.text).is_file():
                print(f'Waiting for real text_daily: {args.text}', flush=True)
            else:
                inputs = [Path(args.market), Path(args.text)]
                optional_inputs = [Path(p) for p in [args.ucry, args.source_weighted_text, args.exclude_price_text] if p and Path(p).is_file()]
                event_paths = [ROOT/'data/interim/documents.parquet', ROOT/'data/interim/doc_scores.parquet'] if real else []
                event_paths += sorted((ROOT/'data/raw').glob('*_1h_*.parquet')) if real else []
                event_paths = [path for path in event_paths if path.is_file()]
                all_inputs = [*inputs, *optional_inputs, *event_paths]
                current = tuple((str(p), hashlib.sha256(p.read_bytes()).hexdigest()) for p in all_inputs)
                metadata_path = Path(args.output)/'run_metadata.json'
                try:
                    previous = json.loads(metadata_path.read_text(encoding='utf-8'))
                except (OSError, ValueError):
                    previous = {}
                if previous.get('sha256') != dict(current) or previous.get('analysis_code_sha256') != code_hash:
                    print(f'Text SHA256 {dict(current)[str(Path(args.text))]}', flush=True)
                    market, text = (pd.read_parquet(p) for p in inputs)
                    variants = {name: pd.read_parquet(path) for name, path in [
                        ('source_weighted', args.source_weighted_text), ('exclude_price_speculation', args.exclude_price_text)] if path}
                    figures = args.figures or str(ROOT/'outputs/figures'/('real' if real else 'synthetic'))
                    ucry = pd.read_parquet(args.ucry) if args.ucry and Path(args.ucry).is_file() else None
                    event_inputs = (pd.read_parquet(event_paths[0]), pd.read_parquet(event_paths[1]), hourly_prices()) if real and len(event_paths) >= 7 else None
                    tables = run_analysis(market, text, config, args.output, figures, real, args.refit_days,
                                          variants, ucry, event_inputs)
                    if real:
                        for row in tables['coverage'].itertuples():
                            print(f'Coverage {row.asset}: {row.news_days}/{row.calendar_days} news days; '
                                  f'train={row.model_train_days}, valid={row.model_valid_days}, test={row.model_test_days}', flush=True)
                    metadata = dict(result_source='real' if real else 'synthetic', config=config, refit_days=args.refit_days,
                                    sha256=dict(current),
                                    analysis_code_sha256=code_hash,
                                    pipeline_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
                    metadata_path.write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
        except Exception:
            if not args.watch:
                raise
            import traceback
            traceback.print_exc()
            print('Input run failed; retrying at the next poll without replacing missing data', flush=True)
        if not args.watch:
            return
        print(f'Next input check in {args.poll_seconds} seconds', flush=True)
        # Short sleeps let process interruption remain responsive.
        remaining = args.poll_seconds
        while remaining:
            pause = min(30, remaining)
            time.sleep(pause)
            remaining -= pause


if __name__ == '__main__':
    main()
