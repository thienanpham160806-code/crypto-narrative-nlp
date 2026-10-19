# SYNTHETIC (code validation only)

Daily forecast horizon is the single outcome at t+h, not a cumulative h-day return.
Missing news/scores remain missing. No interpolation, fabricated labels or split changes.
Rows with identified=False have rank-deficient design: coefficients are not unique and p-values/standard errors are withheld.
Holm/BH uses each unique comparison table as one family. MCS is evaluation, not test-set model selection.

## Actual coverage

- BNB: 1369/1369 days with indexed news (100.00%); FinBERT coverage 100.00%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-08 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1361 rows).
- BTC: 1369/1369 days with indexed news (100.00%); FinBERT coverage 100.00%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-08 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1361 rows).
- ETH: 1369/1369 days with indexed news (100.00%); FinBERT coverage 100.00%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-08 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1361 rows).
- SOL: 1369/1369 days with indexed news (100.00%); FinBERT coverage 100.00%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-08 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1361 rows).
- XRP: 1369/1369 days with indexed news (100.00%); FinBERT coverage 100.00%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-08 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1361 rows).

## Table interpretation

### regressions.csv (3735 rows)

RQ1/RQ3: coefficients measure conditional predictive associations with returns, RV and volume. Compare market, raw attention and text on the same sample; they do not validate sentiment labels or identify causal effects.

### wald.csv (15 rows)

RQ2: rejection means negative and positive sentiment have different conditional RV slopes. It does not prove that negative news causes volatility.

### granger.csv (20 rows)

RQ4: text-to-market significance indicates a predictive lead, while the reverse direction suggests price feedback. Missing/short contiguous samples cannot support this inference.

### stationarity.csv (50 rows)

RQ4: ADF tests a unit-root null and KPSS tests a level-stationarity null. Conflicting outcomes call for specification review; KPSS p-values are lookup-table bounds.

### robustness.csv (1800 rows)

RQ1–RQ3: compare pre/post January 2025 and horizon sensitivity with momentum and raw document count. A break dummy cannot repair changing news coverage.

### robustness_status.csv (2 rows)

Document-weighted and price-excluded sensitivity requires reaggregation from canonical articles. Pending means no economic conclusion from that variant.

### quantiles.csv (45 rows)

RQ2: negative/positive RV slopes at tau 0.1/0.5/0.9 expose tail asymmetry hidden by mean regressions. Reported heteroskedastic-robust p-values do not correct serial dependence.

### rolling_quantiles.csv (1350 rows)

RQ2: 500-calendar-day, 20-day-step coefficients show temporal stability. Overlapping windows are dependent and cannot be counted as independent replications.

### quantile_status.csv (15 rows)

Short samples cannot estimate the requested rolling window. An unavailable window provides no evidence of stable tail effects.

### oos.csv (270 rows)

RQ5: positive Campbell–Thompson R² beats the recursive historical mean; lower forecast loss is better. Positive DM/CW favors text; CW with tuned/shrunk nonlinear models remains exploratory.

### forecasts.csv (72990 rows)

RQ5: dated paired forecasts let reviewers audit when information and targets were available. They are research predictions, not executable trade instructions.

### strategy.csv (45 rows)

RQ5 economic-value test only: net return includes 10 bps turnover fees and final liquidation. Zero processing latency and omitted extra slippage make it optimistic.

### shap.csv (780 rows)

RQ1/RQ3: development-only SHAP shows inputs used by the validation-selected model. Importance is neither a causal effect nor proof of out-of-sample value.

### tuning.csv (540 rows)

RQ5: validation losses choose model settings before the frozen test pass. Test results never revise these settings.

### refit_audit.csv (7950 rows)

RQ5: every recorded refit satisfies max(train_target_date) + horizon + embargo < origin. This conservative purge also applies to fixed-window GW fits.

### ml_status.csv (0 rows)

RQ5: pending or skipped cases lack enough honest validation/test observations or contiguous strategy dates. Missing results are not zero effects.

Unavailable for this input sample; no inference reported.

### gw.csv (90 rows)

RQ5: GW uses fixed 500-observation training windows and origin-known return as its conditioning instrument. Rejection indicates conditional forecast differences, not which model dominates every state.

### mcs.csv (270 rows)

RQ5: the 90% Model Confidence Set retains models not rejected by Tmax block-bootstrap elimination. Membership does not establish superiority or select a trading model on test data.

### coverage.csv (5 rows)

Coverage distinguishes collected-index news days, FinBERT-scored days and complete model rows; it does not prove absence of real-world news. Sparse dates can select an unrepresentative sample.

## Figures

- sentiment_btc.svg
- oos_loss.svg
- cumulative_strategy.svg
- quantile_coefficients.svg
- shap_btc.svg

## Preliminary RQ1–RQ5

RQ1: predictive coefficients cannot rank sentiment accuracy without independent labeled validation.
RQ2: use mean Wald and tail slopes together; quantile serial inference remains a limitation.
RQ3: compare text against raw attention and momentum before attributing value to narrative composition.
RQ4: Granger establishes predictive direction only, conditional on stationarity and contiguous coverage.
RQ5: paired losses, corrected inference and economic-value tests assess incremental value; never choose models on test.

Every result below is synthetic code validation; none establishes a real-market effect.
RQ1: BTC h=1 FinBERT return slope 0.00631235, Holm p=9.576e-18; identified=True; this does not validate sentiment-label accuracy.
RQ3: 0/945 estimable hard-narrative coefficients survive table-family Holm at 5%; evaluate against momentum and raw attention.
RQ2: BTC h=1 mean RV slopes negative=0.000131713, positive=6.61973e-07; equality Holm p=1.13e-55.
RQ2 tail tau=0.1: negative=9.39559e-05, positive=5.80267e-06; converged=True, serial inference not corrected.
RQ2 tail tau=0.5: negative=0.000129662, positive=6.9905e-06; converged=True, serial inference not corrected.
RQ2 tail tau=0.9: negative=0.000190144, positive=-8.09847e-06; converged=True, serial inference not corrected.
RQ4 BTC sent_finbert predicts ret: lag=1, Holm p=9.434e-22; predictive direction only.
RQ4 BTC ret predicts sent_finbert: lag=1, Holm p=1; predictive direction only.
RQ5 BTC EN: RMSE market=0.0123408, attention=0.0123255, text=0.0120923; CT R²=0.0348, DM Holm p=1, CW Holm p=0.01093 (CW exploratory).
RQ5 BTC LGBM: RMSE market=0.0125021, attention=0.0124356, text=0.0121786; CT R²=0.02096, DM Holm p=1, CW Holm p=0.00993 (CW exploratory).
RQ5 BTC XGB: RMSE market=0.0123467, attention=0.0123027, text=0.0121683; CT R²=0.02263, DM Holm p=1, CW Holm p=0.04605 (CW exploratory).

## Methods sources

- Clark & West (2007): https://users.ssc.wisc.edu/~cengel/IMF/ClarkWest2007.pdf
- DM-HLN reference arithmetic: https://github.com/johntwk/Diebold-Mariano-Test/blob/master/dm_test.py
- Giacomini & White (2006): https://doi.org/10.1111/j.1468-0262.2006.00718.x
- Hansen, Lunde & Nason (2011): https://www.kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Hansen_Lunde_Nason.pdf
