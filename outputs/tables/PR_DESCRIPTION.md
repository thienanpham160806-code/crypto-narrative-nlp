# Implement X1–X3 market data, econometrics and walk-forward ML

Adds Binance ccxt daily/hourly ingestion and UTC market features; seeded contract-compatible fixtures; predictive HAC regressions, Wald asymmetry and AIC-selected bidirectional VAR/Granger; expanding Elastic Net/XGBoost/LightGBM market-only versus text comparisons with DM, SHAP and fee-adjusted long/flat diagnostics.

## Validation

- `python -m pytest -q`: 15 passed, offline, including calendar gaps, future perturbations, test-set poisoning and batch-versus-daily equivalence for all three models.
- Real Binance coverage: 6,845 daily rows, five assets, 2023-01-01 through 2026-09-30; all return, lag7 and hourly RV recomputations pass.
- One missing hourly candle at 2023-03-24 13:00 UTC per asset; affected daily RV stays missing.
- Synthetic results and economic interpretations: `outputs/tables/README.md`; exact dependency versions: `environment.txt`.

## Timing

`make_panel()` alone aligns calendar targets. Splits use target dates and purge origins before their cutoff. Each refit uses matured labels only. Hyperparameters and the SHAP winner are selected on development data before test predictions. Later frozen test refits may use earlier matured test labels without retuning. VAR retains the longest continuous daily development segment and reports its bounds and excluded observations. Batch predictions preserve the original refit schedule and results.

## Limits

Synthetic results test plumbing and planted-signal recovery, not economic predictability. Real text timestamp accuracy, canonical dedup and train-only topic/vectorizer fitting remain upstream checks. USDT volume approximates close times base volume. Strategies assume zero execution latency and omit spread/slippage beyond 10 bps per entry/exit; final liquidation is charged. VAR stationarity and multiple-testing robustness remain X4. X4 is outside this PR.

No Claude-owned source paths changed. Raw candles, generated parquet and credentials are excluded from commits.

Full fixture run completed: 180 metric rows and 48,660 forecasts. BTC h=1 text RMSE is lower for all three models, but all DM p-values exceed 0.05; this does not establish significant OOS improvement. Artifacts include economic interpretations, SHAP CSV/SVG, configuration/input hashes and dependency versions.

PR creation blocker: GitHub connector returns 403; no browser session is available. Automatic approval review rejected extracting a local Git credential without specific authorization; credentials were not read.
