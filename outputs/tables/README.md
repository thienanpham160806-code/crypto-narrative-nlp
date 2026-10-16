# X1–X3 reproducible research outputs

All checked-in result tables are **synthetic fixtures**, seed 42. They test whether the pipeline recovers an injected small predictive signal; they provide no evidence about crypto markets or the quality of real FinBERT labels.

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
