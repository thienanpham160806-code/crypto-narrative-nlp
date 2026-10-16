# X1–X3 reproducible research outputs

Econometric and ML result tables use **synthetic fixtures**, seed 42. `market_coverage.csv` audits real Binance candles. They test whether the pipeline recovers an injected small predictive signal; they provide no evidence about crypto markets or the quality of real FinBERT labels.

Run from the repository root in the shared virtual environment:

```powershell
& "$HOME/.venv/Scripts/Activate.ps1"
python -m pytest -q
python tests/fixtures/make_fixtures.py
python -m src.models.run --market tests/fixtures/generated/market_daily.parquet --text tests/fixtures/generated/text_daily.parquet
```

For real data, run `python -m src.data.market`, then pass `--market data/processed/market_daily.parquet --text data/processed/text_daily.parquet --output outputs/tables/real` to the same research runner. Never combine a real-market table and synthetic text to claim real predictive evidence. Raw candles and generated parquet are ignored by Git. `--config` can select a separate YAML configuration; `--refit-days 1` gives daily refits (default 30 calendar days).

## Table interpretation

| File | Economic meaning |
|---|---|
| `market_coverage.csv` | Real market coverage only: 1,369 daily rows per asset, 2023-01-01 through 2026-09-30, with one missing RV day per asset because the 2023-03-24 13:00 UTC candle is absent. Missing RV is preserved rather than understating volatility. |
| `regressions.csv` | Development-only predictive OLS with Newey–West HAC. Sentiment coefficients describe next-h-day return or RV associations conditional on market controls; shares are relative to omitted price/speculation attention. Differences across sentiment regressions are not a labeled sentiment validation. |
| `wald.csv` | Tests equality of negative and positive sentiment coefficients for future RV. A rejection indicates asymmetric conditional associations, not proof that news causes volatility. |
| `granger.csv` | AIC-selected bivariate VAR, both directions, on the longest contiguous development segment (sample boundaries and discarded count reported). A significant text→market test indicates a predictive lead; market→text suggests feedback. AIC zero lags yields an explicit untested result. |
| `oos.csv` | Paired market-only and text-augmented expanding forecasts. Positive OOS R² beats the expanding historical mean; lower RMSE/MAE/QLIKE is better. Positive DM favors text; p-values are unadjusted exploratory tests. |
| `forecasts.csv` | Auditable forecast origins, target dates, observations, predictions and historical mean. This is the basis for economic-value comparisons, not an executable trading feed. |
| `tuning.csv` | Validation losses and candidate settings. Settings and the SHAP winner are selected here before the test pass; these numbers are not final performance claims. |
| `shap.csv` | Mean absolute development-sample SHAP for the validation-selected text model, in target units. Importance explains a model's dependence on inputs, not economic causation. |
| `strategy.csv` | One-day long/flat at prediction > 0, 10 bps per entry/exit, final liquidation included, versus buy-and-hold with matching fees. Returns compound simple daily returns; Sharpe uses 365 days. No leverage or multi-horizon overlap. |

## Timing and known limits

- Day t means UTC [t, t+1). Forecast origin is its closing boundary; target is a **single daily outcome at t+h**, not a cumulative h-day return. Boundary-straddling labels are purged from validation and test so their origins are not before the respective cutoff.
- `make_panel()` alone aligns future outcomes by calendar date, preserving missing dates rather than compressing them. Asset-specific text takes priority over `ALL`; missing text stays missing and unusable model rows are dropped.
- Tuning uses targets through `valid_end` only. During the frozen test pass, a later refit may use earlier test labels that have matured by its forecast origin, as in live expanding forecasting. Neither candidate settings nor model choice is revisited on test outcomes.
- Standardization and target scale are fit on matured training labels only. SHAP selects and explains a development-only model. Real text upstream must still prove timestamp accuracy, canonical dedup and train-only topic/vectorizer fitting; aggregate daily input alone cannot prove those properties.
- Daily candles must cover the full requested grid; all candles must be completed, positive-price and nonnegative-volume. Missing hourly coverage emits a warning and produces missing RV, with no return bridged across gaps. Nine warm-up days supply the first requested day's RV and return lags. RV sums 24 hourly close-to-close squared log returns including the first hour's return from the previous day.
- `volume_usd` is **close × base volume**, a USDT notional approximation, not exact traded quote volume or USD conversion. Universe selection may introduce survivorship bias. See [CCXT candle and pagination documentation](https://github.com/ccxt/ccxt/wiki/manual) and [statsmodels VAR documentation](https://www.statsmodels.org/stable/vector_ar.html).
- End-of-day execution assumes zero processing latency and ignores spread/slippage beyond the stated fee; strategy results are an optimistic economic-value diagnostic. VAR stationarity and multiple-testing robustness remain X4 work. Future sample configuration must end on a completed day.

Synthetic fixture generation: sentiment at t enters return t+1 with coefficient 0.006 and idiosyncratic return standard deviation 0.012; negative sentiment also enters next-day log RV. This deliberately verifies recovery without embedding future market returns in text features.

Reproducibility: `environment.txt` records exact installed versions; `run_metadata.json` records configuration, input SHA-256 values and pipeline commit. `PR_DESCRIPTION.md` is the prepared review description. Offline verification: **15 tests pass**, including all three models, SHAP, future-data perturbation, test-set poisoning and batched prediction equivalence. All 6,845 real-market rows pass independent return, lag7 and RV recomputation checks.

## Synthetic BTC, one-day forecasts

| Model | RMSE market | RMSE text | DM p | Text OOS R² |
|---|---:|---:|---:|---:|
| EN | 0.012340 | 0.012115 | 0.3166 | 0.0313 |
| LGBM | 0.012574 | 0.012158 | 0.1444 | 0.0244 |
| XGB | 0.012321 | 0.012146 | 0.4831 | 0.0263 |

The planted one-day sentiment signal is recovered when text reduces forecast loss; this validates implementation rather than real-world trading value. Horizons 3 and 7 are also reported without selecting them on test performance. Positive DM favors text; unadjusted p-values are exploratory.

Synthetic BTC h=1 HAC sentiment coefficient: 0.006294 (p=1.85e-21); Wald RV asymmetry p=4.37e-56. Granger text→return p=6.29e-23 versus return→text p=0.458; the direction matches the injected signal and establishes no real-market causal claim.

Full outputs contain 180 metric rows and 48660 paired forecast rows across five assets, horizons 1/3/7, two targets, three models and two feature versions.

For synthetic BTC h=1, all three DM p-values exceed 0.05. Lower point-estimate RMSE therefore does **not** establish statistically significant incremental OOS value at 5%. The strong development-sample HAC/Granger findings must not be conflated with the weaker held-out forecast comparison.

X4 runner now exports ADF/KPSS, table-family Holm/BH, momentum + raw n_docs controls, January 2025 level dummy, and pre/post sensitivity. Document-weighted and price-excluded variants require separately rebuilt text_daily inputs; daily means cannot recover them. Existing tables predate X4; new X4 tables are generated separately.
