"""Run X2-X3 against explicit parquet paths, or reproducible synthetic fixtures."""
import argparse
import hashlib
from importlib import metadata
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


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(4*1024*1024), b''):
            digest.update(chunk)
    return digest.digest()


def analysis_key(paths, config, root=ROOT):
    """Content key for inputs, canonical config, source tree and model libraries."""
    versions = {}
    for package in ('numpy', 'pandas', 'scipy', 'statsmodels', 'scikit-learn',
                    'xgboost', 'lightgbm', 'transformers', 'torch'):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    digest = hashlib.sha256(json.dumps({'config': config, 'versions': versions},
                                      sort_keys=True, ensure_ascii=False, default=str).encode('utf-8'))
    for path in [*sorted(map(Path, paths)), *sorted((root/'src').rglob('*.py'))]:
        name = path.relative_to(root) if path.is_relative_to(root) else path
        digest.update(str(name).encode('utf-8'))
        digest.update(file_sha256(path))
    return digest.hexdigest()


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
                 event_inputs=None, failed_steps=None):
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
        try:
            for name, table in call().items():
                table = correct_tests(table)
                tables[name] = table
                table.to_csv(output/f'{name}.csv', index=False, encoding='utf-8')
        except Exception:
            if failed_steps is None:
                raise
            import logging
            logging.exception('Analysis step failed: %s', label)
            failed_steps.append(label)
    if ucry is not None:
        try:
            controlled = run_econometrics(market, attach_ucry(text, ucry), config)
            for name in ['regressions', 'wald']:
                tables[f'ucry_{name}'] = correct_tests(controlled[name])
        except Exception:
            if failed_steps is None:
                raise
            import logging
            logging.exception('Analysis step failed: ucry')
            failed_steps.append('ucry')
    if real and event_inputs is not None:
        print('Running hourly events', flush=True)
        documents, scores, prices = event_inputs
        try:
            tables.update(run_real_events(documents, scores, prices, config['split']['train_end'], output, figures))
        except Exception:
            if failed_steps is None:
                raise
            import logging
            logging.exception('Analysis step failed: hourly events')
            failed_steps.append('hourly events')
    try:
        write_report(market, text, config, tables, output, figures, real)
    except Exception:
        if failed_steps is None:
            raise
        import logging
        logging.exception('Analysis step failed: report/figures')
        failed_steps.append('report/figures')
    if real:
        from src.evaluation.report import write_results
        try:
            write_results(tables, output)
        except Exception:
            if failed_steps is None:
                raise
            import logging
            logging.exception('Analysis step failed: RESULTS')
            failed_steps.append('RESULTS')
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
    while True:
        try:
            missing = [str(path) for path in (args.market, args.text) if not Path(path).is_file()]
            for path in (args.source_weighted_text, args.exclude_price_text):
                if path and not Path(path).is_file():
                    missing.append(path)
            event_paths = []
            if real:
                for path in (ROOT/'data/interim/documents.parquet', ROOT/'data/interim/doc_scores.parquet'):
                    if path.is_file():
                        event_paths.append(path)
                    else:
                        missing.append(str(path))
                for asset in ('BTC', 'ETH', 'SOL', 'BNB', 'XRP'):
                    matches = list((ROOT/'data/raw').glob(f'{asset}_1h_*.parquet'))
                    if len(matches) == 1:
                        event_paths.extend(matches)
                    else:
                        missing.append(f'{asset} hourly candles (expected 1, found {len(matches)})')
            if missing:
                raise FileNotFoundError('Missing mandatory input: ' + ', '.join(missing))
            else:
                inputs = [Path(args.market), Path(args.text)]
                optional_inputs = [Path(p) for p in [args.ucry, args.source_weighted_text, args.exclude_price_text] if p and Path(p).is_file()]
                all_inputs = [*inputs, *optional_inputs, *event_paths]
                current = tuple((str(p), file_sha256(p).hex()) for p in all_inputs)
                key = analysis_key(all_inputs, config)
                metadata_path = Path(args.output)/'run_metadata.json'
                try:
                    previous = json.loads(metadata_path.read_text(encoding='utf-8'))
                except (OSError, ValueError):
                    previous = {}
                if previous.get('run_key') != key:
                    print(f'Text SHA256 {dict(current)[str(Path(args.text))]}', flush=True)
                    market, text = (pd.read_parquet(p) for p in inputs)
                    variants = {name: pd.read_parquet(path) for name, path in [
                        ('source_weighted', args.source_weighted_text), ('exclude_price_speculation', args.exclude_price_text)] if path}
                    figures = args.figures or str(ROOT/'outputs/figures'/('real' if real else 'synthetic'))
                    ucry = pd.read_parquet(args.ucry) if args.ucry and Path(args.ucry).is_file() else None
                    event_inputs = (pd.read_parquet(event_paths[0]), pd.read_parquet(event_paths[1]), hourly_prices()) if real else None
                    tables = run_analysis(market, text, config, args.output, figures, real, args.refit_days,
                                          variants, ucry, event_inputs)
                    if real:
                        for row in tables['coverage'].itertuples():
                            print(f'Coverage {row.asset}: {row.news_days}/{row.calendar_days} corpus news days; '
                                  f'{row.asset_news_days} asset-tagged news days; '
                                  f'train={row.model_train_days}, valid={row.model_valid_days}, test={row.model_test_days}', flush=True)
                    metadata = dict(result_source='real' if real else 'synthetic', config=config, refit_days=args.refit_days,
                                    sha256=dict(current),
                                    run_key=key,
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
