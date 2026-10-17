# REAL (partial corpus; provenance audit required)

Daily forecast horizon is the single outcome at t+h, not a cumulative h-day return.
Missing news/scores remain missing. No interpolation, fabricated labels or split changes.
Rows with identified=False have rank-deficient design: coefficients are not unique and p-values/standard errors are withheld.
Holm/BH uses each unique comparison table as one family. MCS is evaluation, not test-set model selection.

## Actual coverage

- BNB: 180/1369 days with indexed news (13.15%); FinBERT coverage 13.15%; news 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00 (138 rows); train/valid/test=101/10/27.
- BTC: 180/1369 days with indexed news (13.15%); FinBERT coverage 13.15%; news 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00 (176 rows); train/valid/test=130/12/34.
- ETH: 180/1369 days with indexed news (13.15%); FinBERT coverage 13.15%; news 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00 (169 rows); train/valid/test=127/12/30.
- SOL: 180/1369 days with indexed news (13.15%); FinBERT coverage 13.15%; news 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00 (144 rows); train/valid/test=111/9/24.
- XRP: 180/1369 days with indexed news (13.15%); FinBERT coverage 13.15%; news 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-23 00:00:00+00:00 (151 rows); train/valid/test=110/12/29.

## Table interpretation

### regressions.csv (4815 rows)

RQ1/RQ3: coefficients measure conditional predictive associations with returns, RV and volume. Compare market, raw attention and text on the same sample; they do not validate sentiment labels or identify causal effects.

### wald.csv (15 rows)

RQ2: rejection means negative and positive sentiment have different conditional RV slopes. It does not prove that negative news causes volatility.

### granger.csv (10 rows)

RQ4: text-to-market significance indicates a predictive lead, while the reverse direction suggests price feedback. Missing/short contiguous samples cannot support this inference.

### stationarity.csv (40 rows)

RQ4: ADF tests a unit-root null and KPSS tests a level-stationarity null. Conflicting outcomes call for specification review; KPSS p-values are lookup-table bounds.

### robustness.csv (1800 rows)

RQ1–RQ3: compare pre/post January 2025 and horizon sensitivity with momentum and raw document count. A break dummy cannot repair changing news coverage.

### robustness_status.csv (2 rows)

Document-weighted and price-excluded sensitivity requires reaggregation from canonical articles. Pending means no economic conclusion from that variant.

### quantiles.csv (45 rows)

RQ2: negative/positive RV slopes at tau 0.1/0.5/0.9 expose tail asymmetry hidden by mean regressions. Reported heteroskedastic-robust p-values do not correct serial dependence.

### rolling_quantiles.csv (1260 rows)

RQ2: 500-calendar-day, 20-day-step coefficients show temporal stability. Overlapping windows are dependent and cannot be counted as independent replications.

### quantile_status.csv (15 rows)

Short samples cannot estimate the requested rolling window. An unavailable window provides no evidence of stable tail effects.

### oos.csv (216 rows)

RQ5: positive Campbell–Thompson R² beats the recursive historical mean; lower forecast loss is better. Positive DM/CW favors text; CW with tuned/shrunk nonlinear models remains exploratory.

### forecasts.csv (6480 rows)

RQ5: dated paired forecasts let reviewers audit when information and targets were available. They are research predictions, not executable trade instructions.

### strategy.csv (0 rows)

RQ5 economic-value test only: net return includes 10 bps turnover fees and final liquidation. Zero processing latency and omitted extra slippage make it optimistic.

Unavailable for this input sample; no inference reported.

### shap.csv (816 rows)

RQ1/RQ3: development-only SHAP shows inputs used by the validation-selected model. Importance is neither a causal effect nor proof of out-of-sample value.

### tuning.csv (432 rows)

RQ5: validation losses choose model settings before the frozen test pass. Test results never revise these settings.

### refit_audit.csv (4320 rows)

RQ5: every recorded refit satisfies max(train_target_date) + horizon + embargo < origin. This conservative purge also applies to fixed-window GW fits.

### ml_status.csv (144 rows)

RQ5: pending or skipped cases lack enough honest validation/test observations or contiguous strategy dates. Missing results are not zero effects.

### gw.csv (0 rows)

RQ5: GW uses fixed 500-observation training windows and origin-known return as its conditioning instrument. Rejection indicates conditional forecast differences, not which model dominates every state.

Unavailable for this input sample; no inference reported.

### mcs.csv (0 rows)

RQ5: the 90% Model Confidence Set retains models not rejected by Tmax block-bootstrap elimination. Membership does not establish superiority or select a trading model on test data.

Unavailable for this input sample; no inference reported.

### ucry_regressions.csv (5265 rows)

RQ3: UCRY-controlled regressions use only dates with released weekly observations, in a separate common sample. Retrospective indices lack vintages and cannot justify live forecast claims.

### ucry_wald.csv (15 rows)

RQ2/RQ3: the asymmetry test conditions on weekly uncertainty where available. Its sample differs from the main table; unavailable post-2024 UCRY is never extrapolated.

### event_observations.csv (39003 rows)

Each row is a canonical English article and tagged asset, or BTC for untagged market news. CAR uses an hourly BTC market model for altcoins and a past-hour mean for BTC; overlapping articles share market shocks.

### event_tests.csv (342 rows)

Hourly reactions are tested on event-day means, so multiple articles on one day form one cluster. BMP-style CAR is estimation-error standardized and day clustered. The −24h placebo omits [0,24], whose inclusive endpoint would overlap T0.

### event_asymmetry.csv (24 rows)

Negative-minus-positive compares same-day FinBERT and LM terciles on days where both occur. Its paired day test asks whether bad-news reaction differs from good-news reaction.

### event_timing_pairs.csv (39 rows)

The same GDELT article is aligned once to published time and once to first-seen time. Pairwise CAR changes quantify timestamp sensitivity without changing the article sample.

### event_timing.csv (3 rows)

A changed significance flag shows the timing choice can alter a nominal conclusion. This small audited subset cannot calibrate the full corpus.

### event_coverage.csv (1 rows)

Article count, scored count, usable event days and training-only tercile cutoffs limit the scope of hourly inference.

### coverage.csv (5 rows)

Coverage distinguishes collected-index news days, FinBERT-scored days and complete model rows; it does not prove absence of real-world news. Sparse dates can select an unrepresentative sample.

## Figures

- sentiment_btc.svg
- oos_loss.svg
- quantile_coefficients.svg
- shap_btc.svg

## Preliminary RQ1–RQ5

RQ1: predictive coefficients cannot rank sentiment accuracy without independent labeled validation.
RQ2: use mean Wald and tail slopes together; quantile serial inference remains a limitation.
RQ3: compare text against raw attention and momentum before attributing value to narrative composition.
RQ4: Granger establishes predictive direction only, conditional on stationarity and contiguous coverage.
RQ5: paired losses, corrected inference and economic-value tests assess incremental value; never choose models on test.

These are partial real-data associations.
Regression samples contain 110–143 observations; minimum residual degrees of freedom=82. Tiny samples and many parameters make all significance findings exploratory.
RQ1: BTC h=1 FinBERT return slope 0.00837095, Holm p=1; identified=True; this does not validate sentiment-label accuracy.
RQ3: 20/945 estimable hard-narrative coefficients survive table-family Holm at 5%; evaluate against momentum and raw attention.
RQ2: BTC h=1 mean RV slopes negative=0.00173992, positive=0.00103779; equality Holm p=1.
RQ2 tail tau=0.1: negative=0.000309909, positive=0.000179655; converged=True, serial inference not corrected.
RQ2 tail tau=0.5: negative=0.000523504, positive=0.000432723; converged=True, serial inference not corrected.
RQ2 tail tau=0.9: negative=0.00330361, positive=0.00123152; converged=True, serial inference not corrected.
RQ5 BTC EN: RMSE market=0.0152536, attention=0.0153612, text=0.0156517; CT R²=-0.00395, DM Holm p=nan, CW Holm p=nan (CW exploratory).
RQ5 BTC LGBM: RMSE market=0.01659, attention=0.0161372, text=0.0163572; CT R²=-0.0965, DM Holm p=nan, CW Holm p=nan (CW exploratory).
RQ5 BTC XGB: RMSE market=0.0169663, attention=0.0164312, text=0.017268; CT R²=-0.222, DM Holm p=nan, CW Holm p=nan (CW exploratory).

## Methods sources

- Clark & West (2007): https://users.ssc.wisc.edu/~cengel/IMF/ClarkWest2007.pdf
- DM-HLN reference arithmetic: https://github.com/johntwk/Diebold-Mariano-Test/blob/master/dm_test.py
- Giacomini & White (2006): https://doi.org/10.1111/j.1468-0262.2006.00718.x
- Hansen, Lunde & Nason (2011): https://www.kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Hansen_Lunde_Nason.pdf
