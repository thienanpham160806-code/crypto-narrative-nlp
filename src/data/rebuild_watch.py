"""Canh bộ thu GKG → rebuild text → cờ REBUILD_DONE (DATA_CONTRACT §7) → chờ RUN_DONE của Codex → điền paper + redeploy.

Chạy nền từ gốc repo:  PYTHONPATH=src python -m data.rebuild_watch
Giai đoạn 1: đủ 1369/1369 ngày thì rebuild; log thu dừng > 30 phút mà còn ngày thiếu thì khởi động lại bộ thu
(bộ thu chỉ tải các ngày chưa có cache). Bước nào lỗi → không ghi cờ, dừng.
Giai đoạn 2: RUN_DONE.json status ok, input_sha256 khớp text_daily vừa build → fill_results, build_docx,
export dashboard, Vercel deploy. Văn xuôi phần 4 do khuôn token/điều kiện tự cập nhật; tác giả rà lại sau.
"""
from __future__ import annotations
import datetime as dt, hashlib, json, os, subprocess, sys, time
from pathlib import Path

import pandas as pd

from data.news_gdelt import cache_dir
from utils.common import CFG

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
LOG = ROOT / "data" / "processed" / "rebuild_watch.log"
FLAG = ROOT / "data" / "processed" / "REBUILD_DONE.json"
RUN = ROOT / "outputs" / "tables" / "real" / "RUN_DONE.json"
GKG_LOG = ROOT / "data" / "raw" / "gkg" / "progress.log"
STALE_MIN, POLL_S = 30, 300
STEPS = ["data.build_documents", "features.narrative", "features.doc_scores", "features.daily_index"]


def log(msg: str) -> None:
    line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def days() -> pd.DatetimeIndex:
    return pd.date_range(CFG["sample"]["start"], CFG["sample"]["end"])


def missing() -> list:
    return [d for d in days() if not (cache_dir("en") / f"{d:%Y%m%d}_00.jsonl").exists()]


def log_age_min() -> float:
    return (time.time() - GKG_LOG.stat().st_mtime) / 60 if GKG_LOG.exists() else float("inf")


def collector_pids() -> list[int]:
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -like '*data.news_gdelt*' } | ForEach-Object { $_.ProcessId }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout
    return [int(x) for x in out.split()]


def restart_collector() -> None:
    for pid in collector_pids():
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    out = (ROOT / "data" / "raw" / "gkg" / "en.out").open("a")
    subprocess.Popen([PY, "-m", "data.news_gdelt", "--lang", "en", "--workers", "4"], cwd=ROOT, env=env(),
                     stdout=out, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))


def env() -> dict:
    return {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    log("chạy " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd, env=env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
                       shell=cmd[0] in ("npm", "npx"))
    if r.returncode:
        raise RuntimeError(f"{' '.join(cmd)} lỗi {r.returncode}: {(r.stderr or r.stdout)[-800:]}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def progress(note: str) -> None:
    """PROGRESS chỉ append rồi commit + push ngay (AGENTS.md); lỗi git không chặn pipeline."""
    with (ROOT / "docs" / "PROGRESS.md").open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} | claude | rebuild_watch | {note}\n")
    for cmd in (["git", "add", "docs/PROGRESS.md"],
                ["git", "commit", "-m", f"docs(progress): {note[:60]}", "--", "docs/PROGRESS.md"],
                ["git", "push", "origin", "dev"]):
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            log(f"git bỏ qua: {' '.join(cmd)}: {r.stderr.strip()[-200:]}")
            return


def wait_gkg() -> None:
    while left := missing():
        age = log_age_min()
        if age > STALE_MIN or not collector_pids():
            log(f"còn {len(left)} ngày, log dừng {age:.0f} phút → khởi động lại bộ thu")
            restart_collector()
        time.sleep(POLL_S)
    while collector_pids():                    # bộ thu tự thoát khi đủ; chờ nó ghi xong
        time.sleep(30)


def rebuild() -> dict:
    for step in STEPS:
        run([PY, "-m", step])
    text, docs = ROOT / "data" / "processed" / "text_daily.parquet", ROOT / "data" / "interim" / "documents.parquet"
    for p in (text, docs, ROOT / "outputs" / "tables" / "corpus_stats.csv", ROOT / "outputs" / "tables" / "timestamp_accuracy.csv"):
        if not p.exists():
            raise RuntimeError(f"thiếu {p}")
    n = len(days()) - len(missing())
    flag = {"finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "gkg_days": n,
            "gkg_total": len(days()), "text_daily_sha256": sha256(text), "documents_sha256": sha256(docs)}
    tmp = FLAG.with_suffix(".tmp")
    tmp.write_text(json.dumps(flag, indent=2), encoding="utf-8")
    tmp.replace(FLAG)
    return flag


def wait_run(flag: dict) -> dict:
    while True:
        if RUN.exists():
            try:
                r = json.loads(RUN.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                r = {}
            if r.get("input_sha256") == flag["text_daily_sha256"] and r.get("finished_utc", "") > flag["finished_utc"]:
                return r
        time.sleep(POLL_S)


def publish() -> None:
    run([PY, "paper/fill_results.py", "--check"])
    run([PY, "paper/build_docx.py"])
    run([PY, "dashboard/export.py"])
    run([PY, "dashboard/paper.py"])
    (ROOT / "dashboard" / "web" / "public" / "paper.docx").write_bytes((ROOT / "paper" / "paper.docx").read_bytes())
    web = ROOT / "dashboard" / "web"
    run(["npm", "run", "build"], web)
    run(["npx", "--no-install", "vercel", "deploy", "--prod", "--yes"], web)


def main() -> None:
    log("bắt đầu canh GKG")
    wait_gkg()
    try:
        flag = rebuild()
    except Exception as e:  # không ghi cờ nếu bước nào lỗi
        log(f"rebuild LỖI, không ghi REBUILD_DONE: {e}")
        progress(f"rebuild lỗi, chưa ghi REBUILD_DONE: {str(e)[:200]}")
        raise
    log(f"REBUILD_DONE {flag}")
    progress(f"GKG {flag['gkg_days']}/{flag['gkg_total']} ngày; rebuild documents→narratives→doc_scores→text_daily + "
             f"corpus_stats/timestamp_accuracy xong; ghi REBUILD_DONE.json (text_daily {flag['text_daily_sha256'][:12]})")
    r = wait_run(flag)
    log(f"RUN_DONE {r}")
    if r.get("status") != "ok":
        progress(f"RUN_DONE status={r.get('status')} failed={r.get('failed_steps')}: chưa điền paper")
        return
    try:
        publish()
    except Exception as e:
        log(f"publish LỖI: {e}")
        progress(f"điền paper/redeploy lỗi: {str(e)[:200]}")
        raise
    progress("RUN_DONE ok → fill_results + build_docx + export dashboard + redeploy Vercel xong; chờ rà văn xuôi phần 4")


if __name__ == "__main__":
    main()
