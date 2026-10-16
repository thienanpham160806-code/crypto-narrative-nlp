# Offline analysis notebook

Open `main.ipynb` in a Python kernel with `requirements.txt` installed. The notebook performs no downloads or source ingestion. It reads local `data/processed`; absent real text, it explicitly generates seeded synthetic inputs in memory and writes only to the synthetic output directory.

All analysis is recomputed, including development-only OLS/VAR, diagnostics, quantiles, three ML feature tiers, fixed-window GW, MCS, SHAP and paper figures. Full five-asset analysis can take several minutes. Quantile windows use exact pinball-loss linear programming; full-sample quantile standard errors are heteroskedastic-robust and do not correct serial dependence.

The current machine has plotting/Jupyter in the host Python and research dependencies in `.venv`; the notebook reuses that environment without installing packages. For a clean machine, prepare a kernel once with `python -m pip install -r notebooks/requirements.txt` before offline use.

For unattended real inputs:

```powershell
python -m src.models.run_real --watch --poll-seconds 1800
```

Use a kernel/interpreter containing the listed packages. On this machine the background watcher uses the host Python with `.venv/Lib/site-packages` in `PYTHONPATH`. It retries failed/partially written inputs at the next poll, preserves research splits, and never substitutes synthetic text into a real run. Local watcher logs are not committed. The watcher does not commit or push files produced later.

`outputs/tables/<mode>/README.md` reports actual coverage, per-table economic interpretation and preliminary RQ1–RQ5 findings. `outputs/figures/<mode>/` contains SVG and PNG paper figures, explicitly labeled REAL or SYNTHETIC. Strategy plots are economic-value tests only.
