"""Run the real analysis once, or after a stable upstream rebuild sentinel."""
import argparse
import ctypes
from datetime import datetime, timezone
import gzip
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import pandas as pd
import yaml

from src.models.run import main as legacy_main, run_analysis
from src.evaluation.hourly_event import hourly_prices
from src.evaluation.report import write_results
from src.utils.common import ROOT


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def utc(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('finished_utc must include UTC timezone')
    return parsed.astimezone(timezone.utc)


def hold_awake(active, setter=None):
    """Temporarily inhibit Windows idle sleep until the full rebuild is analyzed."""
    if os.name != 'nt':
        return
    setter = setter or ctypes.windll.kernel32.SetThreadExecutionState
    if not setter(0x80000000 | (0x00000001 if active else 0)):
        logging.warning('Could not update Windows execution state')


def stable_snapshot(sentinel, text_path, documents_path, run_done, allow_partial=False):
    """Return a verified candidate and its file fingerprint, or a wait reason."""
    sentinel, text_path = Path(sentinel), Path(text_path)
    documents_path, run_done = Path(documents_path), Path(run_done)
    if not sentinel.is_file():
        return None, 'waiting for REBUILD_DONE.json'
    try:
        raw = sentinel.read_bytes()
        data = json.loads(raw)
        finished = utc(data['finished_utc'])
        if run_done.is_file():
            previous = utc(json.loads(run_done.read_text(encoding='utf-8'))['finished_utc'])
            if finished <= previous:
                return None, 'sentinel is not newer than last run'
        days, total = int(data['gkg_days']), int(data['gkg_total'])
        if not (0 <= days <= total and total > 0):
            return None, 'invalid GKG coverage'
        if days < total and not allow_partial:
            return None, f'GKG incomplete: {days}/{total}'
        paths = (sentinel, text_path, documents_path)
        before = tuple((p.stat().st_size, p.stat().st_mtime_ns) for p in paths)
        text_hash, documents_hash = sha256(text_path), sha256(documents_path)
        after = tuple((p.stat().st_size, p.stat().st_mtime_ns) for p in paths)
        if before != after or sentinel.read_bytes() != raw:
            return None, 'input changed during poll'
        if text_hash != data['text_daily_sha256'] or documents_hash != data['documents_sha256']:
            return None, 'sentinel SHA-256 does not match input'
        return {'finished_utc': data['finished_utc'], 'gkg_days': days, 'gkg_total': total,
                'text_sha256': text_hash, 'fingerprint': (hashlib.sha256(raw).hexdigest(), before,
                                                            text_hash, documents_hash)}, 'ready'
    except (OSError, ValueError, KeyError, TypeError) as error:
        return None, f'incomplete sentinel/input: {error}'


def write_done(path, snapshot, failed):
    result = {'finished_utc': datetime.now(timezone.utc).isoformat(),
              'input_sha256': snapshot['text_sha256'],
              'coverage_pct': round(100 * snapshot['gkg_days'] / snapshot['gkg_total'], 4),
              'status': 'failed' if 'analysis' in failed else 'partial' if failed else 'ok',
              'failed_steps': failed}
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def archive_event_observations(output):
    raw = Path(output)/'event_observations.csv'
    archive = raw.with_suffix('.csv.gz')
    if not raw.is_file() or (archive.is_file() and archive.stat().st_mtime_ns >= raw.stat().st_mtime_ns):
        return archive
    temporary = archive.with_suffix('.gz.tmp')
    with raw.open('rb') as source, temporary.open('wb') as target:
        with gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0) as compressed:
            shutil.copyfileobj(source, compressed, 4 * 1024 * 1024)
    temporary.replace(archive)
    return archive


def publish_results(output):
    """Publish only owned generated files once the shared tracked tree is clear."""
    output = Path(output)
    done = json.loads((output/'RUN_DONE.json').read_text(encoding='utf-8'))
    marker = output/'PUBLISH_DONE.json'
    if done['status'] != 'ok':
        return
    if marker.is_file() and json.loads(marker.read_text(encoding='utf-8')).get('input_sha256') == done['input_sha256']:
        return
    archive = archive_event_observations(output)
    paths = [*(path for path in output.glob('*.csv') if path.name != 'event_observations.csv'),
             archive, output/'README.md', output/'RESULTS.md',
             output/'run_metadata.json', output/'RUN_DONE.json', ROOT/'notebooks/main.ipynb',
             *(ROOT/'outputs/figures/real').glob('*.png'),
             *(ROOT/'outputs/figures/real').glob('*.svg')]
    paths = [str(path.relative_to(ROOT)) for path in paths if path.is_file()]
    if not paths:
        return
    changed = subprocess.check_output(['git', 'status', '--porcelain', '--', *paths],
                                      cwd=ROOT, text=True)
    if changed:
        progress = ROOT/'docs/PROGRESS.md'
        line = (f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} | Codex | real rebuild | "
                f"real/ chạy lại trên {done['coverage_pct']:.2f}% ngày GKG; "
                f"RUN_DONE ok, pytest offline qua.\n")
        with progress.open('a', encoding='utf-8', newline='\n') as stream:
            stream.write(line)
        subprocess.run(['git', 'add', '--', *paths, 'docs/PROGRESS.md'], cwd=ROOT, check=True)
        subprocess.run(['git', 'commit', '-m', 'chore: refresh real research outputs', '--',
                        *paths, 'docs/PROGRESS.md'], cwd=ROOT, check=True)
    try:
        subprocess.run(['git', '-c', 'rebase.autoStash=false', 'pull', '--rebase', 'origin', 'dev'],
                       cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        # Shared unstaged Claude files prohibit rebase. A fresh fetch still proves
        # whether this commit can be pushed without rewriting remote history.
        subprocess.run(['git', 'fetch', 'origin', 'dev'], cwd=ROOT, check=True)
        ahead, behind = map(int, subprocess.check_output(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...origin/dev'],
            cwd=ROOT, text=True).split())
        if behind:
            logging.info('Git publication waiting: origin/dev is %s commits ahead', behind)
            return
        if not ahead:
            logging.info('Real outputs already on origin/dev')
    subprocess.run(['git', 'push', 'origin', 'dev'], cwd=ROOT, check=True)
    marker.write_text(json.dumps({'input_sha256': done['input_sha256'],
                                  'published_utc': datetime.now(timezone.utc).isoformat()}) + '\n',
                      encoding='utf-8')
    logging.info('Published real outputs for %s', done['input_sha256'][:12])


def replay_notebook():
    host_python = getattr(sys, '_base_executable', sys.executable)
    code = ("import nbformat; from nbclient import NotebookClient; from pathlib import Path; "
            "p=Path('notebooks/main.ipynb'); n=nbformat.read(p, as_version=4); "
            "NotebookClient(n, timeout=None, kernel_name='python3', "
            "resources={'metadata': {'path': str(Path.cwd())}}).execute(); "
            "nbformat.write(n, p)")
    subprocess.run([host_python, '-c', code], cwd=ROOT, check=True)


def run_cycle(snapshot, output=ROOT/'outputs/tables/real'):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    figures = ROOT/'outputs/figures/real'
    failed = []
    tables = {}
    try:
        config = yaml.safe_load((ROOT/'config/config.yaml').read_text(encoding='utf-8'))
        market = pd.read_parquet(ROOT/'data/processed/market_daily.parquet')
        text = pd.read_parquet(ROOT/'data/processed/text_daily.parquet')
        ucry_path = ROOT/'data/processed/ucry_daily.parquet'
        ucry = pd.read_parquet(ucry_path) if ucry_path.is_file() else None
        variants = {}
        for name, filename in [('source_weighted', 'text_daily_source_weighted.parquet'),
                               ('exclude_price_speculation', 'text_daily_exclude_price.parquet')]:
            path = ROOT/'data/processed'/filename
            if path.is_file():
                variants[name] = pd.read_parquet(path)
        event_inputs = None
        try:
            interim = ROOT/'data/interim'
            event_inputs = (pd.read_parquet(interim/'documents.parquet'),
                            pd.read_parquet(interim/'doc_scores.parquet'), hourly_prices())
        except Exception:
            logging.exception('Hourly event inputs unavailable')
            failed.append('hourly events')
        tables = run_analysis(market, text, config, output, figures, real=True,
                              variants=variants, ucry=ucry, event_inputs=event_inputs,
                              failed_steps=failed)
    except Exception:
        logging.exception('Main analysis failed')
        failed.append('analysis')
    try:
        replay_notebook()
    except Exception:
        logging.exception('Offline notebook failed')
        failed.append('notebook')
    if tables:
        try:
            write_results(tables, output)
        except Exception:
            logging.exception('RESULTS.md failed')
            failed.append('RESULTS')
    try:
        with (output/'pytest.log').open('w', encoding='utf-8') as stream:
            temp = tempfile.mkdtemp(prefix='pytest-watch-', dir=output)
            subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                            '--basetemp', temp], cwd=ROOT, check=True,
                           stdout=stream, stderr=subprocess.STDOUT)
    except Exception:
        logging.exception('Offline pytest failed')
        failed.append('pytest')
    result = write_done(output/'RUN_DONE.json', snapshot, failed)
    logging.info('RUN_DONE status=%s coverage=%.2f%% failed=%s', result['status'],
                 result['coverage_pct'], failed)
    try:
        publish_results(output)
    except Exception:
        logging.exception('Git publication deferred; model results remain available')
    return result


def watch(poll_seconds=120, allow_partial=False):
    if poll_seconds < 1:
        raise ValueError('poll-seconds must be positive')
    output = ROOT/'outputs/tables/real'
    output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=output/'watch.log', level=logging.INFO, encoding='utf-8',
                        format='%(asctime)s %(levelname)s %(message)s', force=True)
    logging.info('Watcher started pid=%s poll=%ss allow_partial=%s', os.getpid(),
                 poll_seconds, allow_partial)
    if not (output/'RUN_DONE.json').is_file():
        hold_awake(True)
    previous = None
    while True:
        candidate, reason = stable_snapshot(ROOT/'data/processed/REBUILD_DONE.json',
                                            ROOT/'data/processed/text_daily.parquet',
                                            ROOT/'data/interim/documents.parquet',
                                            output/'RUN_DONE.json', allow_partial)
        if candidate is None:
            previous = None
            logging.info('%s', reason)
        elif previous == candidate['fingerprint']:
            logging.info('Stable rebuild detected: %s', candidate['finished_utc'])
            try:
                run_cycle(candidate, output)
            except Exception:
                logging.exception('Run cycle failed before RUN_DONE; retrying next poll')
            if (output/'RUN_DONE.json').is_file():
                hold_awake(False)
            previous = None
        else:
            logging.info('First stable poll: %s; checking again', candidate['finished_utc'])
            previous = candidate['fingerprint']
        try:
            if (output/'RUN_DONE.json').is_file():
                publish_results(output)
        except Exception:
            logging.exception('Git publication retry failed')
        time.sleep(poll_seconds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--poll-seconds', type=int, default=120)
    parser.add_argument('--allow-partial', action='store_true')
    args, extra = parser.parse_known_args()
    if args.watch:
        if extra:
            parser.error(f'unknown watch arguments: {extra}')
        watch(args.poll_seconds, args.allow_partial)
    else:
        if args.allow_partial:
            parser.error('--allow-partial requires --watch')
        sys.argv = [sys.argv[0], *extra]
        legacy_main(real=True)


if __name__ == '__main__':
    main()
