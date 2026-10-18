# Offline analysis notebook

Open `main.ipynb` in a Python kernel with `requirements.txt` installed. The notebook performs no downloads or source ingestion. It reads local `data/processed`; absent real text, it explicitly generates seeded synthetic inputs in memory and writes only to the synthetic output directory.

All analysis is recomputed, including development-only OLS/VAR, diagnostics, quantiles, three ML feature tiers, fixed-window GW, MCS, SHAP and paper figures. Full five-asset analysis can take several minutes. Quantile windows use exact pinball-loss linear programming; full-sample quantile standard errors are heteroskedastic-robust and do not correct serial dependence.

The current machine has plotting/Jupyter in the host Python and research dependencies in `.venv`; the notebook reuses that environment without installing packages. For a clean machine, prepare a kernel once with `python -m pip install -r notebooks/requirements.txt` before offline use.

For unattended real inputs:

```powershell
python -m src.models.run_real --watch --poll-seconds 120
```

The watcher uses the project `.venv` and waits for `data/processed/REBUILD_DONE.json`. It verifies both parquet hashes and two unchanged consecutive polls; incomplete GKG requires `--allow-partial`. On trigger it runs the real pipeline, executes this notebook offline with the host kernel, runs pytest and writes `outputs/tables/real/RUN_DONE.json`. Step failures appear in `failed_steps` and `watch.log` without stopping later steps. When tests pass and other tracked work in the shared folder is clean, it stages only Codex outputs, appends PROGRESS, commits, pulls with rebase and pushes `dev`; otherwise it retries publication at later polls.

`outputs/tables/<mode>/README.md` reports actual coverage, per-table economic interpretation and preliminary RQ1–RQ5 findings. `outputs/figures/<mode>/` contains SVG and PNG paper figures, explicitly labeled REAL or SYNTHETIC. Strategy plots are economic-value tests only.
