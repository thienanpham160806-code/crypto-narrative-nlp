import hashlib, json

import pytest

from data import rebuild_watch as rw


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for p in ("data/processed", "data/interim", "outputs/tables"):
        (tmp_path / p).mkdir(parents=True)
    monkeypatch.setattr(rw, "ROOT", tmp_path)
    monkeypatch.setattr(rw, "FLAG", tmp_path / "data/processed/REBUILD_DONE.json")
    monkeypatch.setattr(rw, "LOG", tmp_path / "data/processed/rebuild_watch.log")
    monkeypatch.setattr(rw, "missing", lambda: [])
    return tmp_path


def fake_steps(root):
    def run(cmd, cwd=None):
        if cmd[-1] == rw.STEPS[-1]:
            (root / "data/processed/text_daily.parquet").write_bytes(b"text")
            (root / "data/interim/documents.parquet").write_bytes(b"docs")
            (root / "outputs/tables/corpus_stats.csv").write_text("a")
            (root / "outputs/tables/timestamp_accuracy.csv").write_text("a")
    return run


def test_rebuild_writes_contract_flag_with_hashes_of_final_files(repo, monkeypatch):
    monkeypatch.setattr(rw, "run", fake_steps(repo))
    flag = rw.rebuild()
    saved = json.loads(rw.FLAG.read_text(encoding="utf-8"))
    assert saved == flag
    assert set(saved) == {"finished_utc", "gkg_days", "gkg_total", "text_daily_sha256", "documents_sha256"}
    assert saved["text_daily_sha256"] == hashlib.sha256(b"text").hexdigest()
    assert saved["gkg_days"] == saved["gkg_total"] == 1369


def test_rebuild_failure_leaves_no_flag(repo, monkeypatch):
    def boom(cmd, cwd=None):
        raise RuntimeError("step failed")
    monkeypatch.setattr(rw, "run", boom)
    with pytest.raises(RuntimeError):
        rw.rebuild()
    assert not rw.FLAG.exists()


def test_wait_run_ignores_stale_or_mismatched_run_done(repo, monkeypatch):
    run_done = repo / "RUN_DONE.json"
    monkeypatch.setattr(rw, "RUN", run_done)
    flag = {"finished_utc": "2026-10-18T10:00:00+00:00", "text_daily_sha256": "abc"}
    states = iter([{"finished_utc": "2026-10-18T09:00:00+00:00", "input_sha256": "abc", "status": "ok"},
                   {"finished_utc": "2026-10-18T11:00:00+00:00", "input_sha256": "zzz", "status": "ok"},
                   {"finished_utc": "2026-10-18T11:00:00+00:00", "input_sha256": "abc", "status": "ok"}])
    monkeypatch.setattr(rw.time, "sleep", lambda s: run_done.write_text(json.dumps(next(states))))
    run_done.write_text("{}")
    assert rw.wait_run(flag)["input_sha256"] == "abc"
