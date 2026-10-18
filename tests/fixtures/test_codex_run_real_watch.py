"""Rebuild handshake must reject stale, mismatched, and moving inputs."""
from datetime import datetime, timedelta, timezone
import json
import os
import subprocess

import pytest

from src.models import run_real


def files(tmp_path, *, days=4, total=4):
    text = tmp_path/'text_daily.parquet'
    docs = tmp_path/'documents.parquet'
    sentinel = tmp_path/'REBUILD_DONE.json'
    done = tmp_path/'RUN_DONE.json'
    text.write_bytes(b'text snapshot')
    docs.write_bytes(b'document snapshot')
    record = {'finished_utc': datetime.now(timezone.utc).isoformat(), 'gkg_days': days,
              'gkg_total': total, 'text_daily_sha256': run_real.sha256(text),
              'documents_sha256': run_real.sha256(docs)}
    sentinel.write_text(json.dumps(record), encoding='utf-8')
    return sentinel, text, docs, done


def test_rebuild_rejects_old_sentinel(tmp_path):
    sentinel, text, docs, done = files(tmp_path)
    done.write_text(json.dumps({'finished_utc': (datetime.now(timezone.utc) +
                                                  timedelta(minutes=1)).isoformat()}), encoding='utf-8')
    assert run_real.stable_snapshot(sentinel, text, docs, done)[0] is None


def test_rebuild_rejects_wrong_hash_and_partial(tmp_path):
    sentinel, text, docs, done = files(tmp_path, days=3)
    assert run_real.stable_snapshot(sentinel, text, docs, done)[0] is None
    candidate, _ = run_real.stable_snapshot(sentinel, text, docs, done, allow_partial=True)
    assert candidate['gkg_days'] == 3
    text.write_bytes(b'changed')
    candidate, reason = run_real.stable_snapshot(sentinel, text, docs, done, allow_partial=True)
    assert candidate is None and 'SHA-256' in reason


def test_rebuild_rejects_file_moving_during_poll(tmp_path, monkeypatch):
    sentinel, text, docs, done = files(tmp_path)
    original = run_real.sha256

    def moving(path):
        digest = original(path)
        if path == text:
            text.write_bytes(b'changed during hashing')
        return digest

    monkeypatch.setattr(run_real, 'sha256', moving)
    candidate, reason = run_real.stable_snapshot(sentinel, text, docs, done)
    assert candidate is None and 'changed during poll' in reason


def test_watch_waits_for_two_identical_polls(tmp_path, monkeypatch):
    sentinel, text, docs, done = files(tmp_path)
    monkeypatch.setattr(run_real, 'ROOT', tmp_path)
    (tmp_path/'data/processed').mkdir(parents=True)
    (tmp_path/'data/interim').mkdir(parents=True)
    (tmp_path/'outputs/tables/real').mkdir(parents=True)
    for source, destination in [(sentinel, tmp_path/'data/processed/REBUILD_DONE.json'),
                                (text, tmp_path/'data/processed/text_daily.parquet'),
                                (docs, tmp_path/'data/interim/documents.parquet')]:
        destination.write_bytes(source.read_bytes())
    calls = []
    monkeypatch.setattr(run_real, 'run_cycle', lambda candidate, output: calls.append(candidate))

    def stop_after_second_poll(_):
        if calls:
            raise RuntimeError('test stopped watcher')

    monkeypatch.setattr(run_real.time, 'sleep', stop_after_second_poll)
    try:
        run_real.watch(poll_seconds=1)
    except RuntimeError as error:
        assert str(error) == 'test stopped watcher'
    assert len(calls) == 1


def test_publish_fast_forward_with_other_agent_work(tmp_path, monkeypatch):
    output = tmp_path/'outputs/tables/real'
    output.mkdir(parents=True)
    (tmp_path/'docs').mkdir()
    (output/'RUN_DONE.json').write_text(json.dumps({'status': 'ok', 'input_sha256': 'abc',
                                                     'coverage_pct': 100}), encoding='utf-8')
    monkeypatch.setattr(run_real, 'ROOT', tmp_path)
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        if 'pull' in command:
            raise subprocess.CalledProcessError(1, command)

    def check_output(command, **kwargs):
        return '?? outputs/tables/real/RUN_DONE.json\n' if 'status' in command else '1\t0\n'

    monkeypatch.setattr(run_real.subprocess, 'run', run)
    monkeypatch.setattr(run_real.subprocess, 'check_output', check_output)
    run_real.publish_results(output)
    assert any('fetch' in command for command in commands)
    assert any('push' in command for command in commands)
    assert (output/'PUBLISH_DONE.json').exists()
    assert 'real/ chạy lại trên 100.00%' in (tmp_path/'docs/PROGRESS.md').read_text(encoding='utf-8')


@pytest.mark.skipif(os.name != 'nt', reason='Windows execution state only')
def test_sleep_inhibition_is_released_after_run():
    flags = []
    run_real.hold_awake(True, setter=lambda value: flags.append(value) or 1)
    run_real.hold_awake(False, setter=lambda value: flags.append(value) or 1)
    assert flags == [0x80000001, 0x80000000]
