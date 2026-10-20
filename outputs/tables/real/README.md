# REAL (observed corpus; provenance audit required)

Daily forecast horizon is the single outcome at t+h, not a cumulative h-day return.
Missing news/scores remain missing. No interpolation, fabricated labels or split changes.
Rows with identified=False have rank-deficient design: coefficients are not unique and p-values/standard errors are withheld.
Holm/BH uses each unique comparison table as one family. MCS is evaluation, not test-set model selection.

## Actual coverage

- BNB: 1352/1369 corpus news days (98.76%); 801 asset-tagged news days (58.51%); 551 model origins use corpus fallback; FinBERT panel coverage 98.76%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (866 rows); train/valid/test=556/121/189.
- BTC: 1352/1369 corpus news days (98.76%); 1351 asset-tagged news days (98.69%); 1 model origins use corpus fallback; FinBERT panel coverage 98.76%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1344 rows); train/valid/test=890/182/272.
- ETH: 1352/1369 corpus news days (98.76%); 1321 asset-tagged news days (96.49%); 31 model origins use corpus fallback; FinBERT panel coverage 98.76%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1253 rows); train/valid/test=838/173/242.
- SOL: 1352/1369 corpus news days (98.76%); 1212 asset-tagged news days (88.53%); 140 model origins use corpus fallback; FinBERT panel coverage 98.76%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1035 rows); train/valid/test=716/148/171.
- XRP: 1352/1369 corpus news days (98.76%); 1272 asset-tagged news days (92.91%); 79 model origins use corpus fallback; FinBERT panel coverage 98.76%; news 2023-01-01 00:00:00+00:00 to 2026-09-30 00:00:00+00:00; usable one-day model origins 2023-01-01 00:00:00+00:00 to 2026-09-29 00:00:00+00:00 (1179 rows); train/valid/test=784/177/218.

## Table interpretation

### regressions.csv (4950 rows)

RQ1/RQ3: coefficients measure conditional predictive associations with returns, RV and volume. Compare market, raw attention and text on the same sample; they do not validate sentiment labels or identify causal effects.

### wald.csv (15 rows)

RQ2: rejection means negative and positive sentiment have different conditional RV slopes. It does not prove that negative news causes volatility.

### granger.csv (20 rows)

RQ4: text-to-market significance indicates a predictive lead, while the reverse direction suggests price feedback. Missing/short contiguous samples cannot support this inference.

### forecasts.csv (58284 rows)

RQ5: dated paired forecasts let reviewers audit when information and targets were available. They are research predictions, not executable trade instructions.

### gw.csv (90 rows)

RQ5: GW uses fixed 500-observation training windows and origin-known return as its conditioning instrument. Rejection indicates conditional forecast differences, not which model dominates every state.

### mcs.csv (108 rows)

RQ5: the 90% Model Confidence Set retains models not rejected by Tmax block-bootstrap elimination. Membership does not establish superiority or select a trading model on test data.

### oos.csv (270 rows)

RQ5: positive Campbell–Thompson R² beats the recursive historical mean; lower forecast loss is better. Positive DM/CW favors text; CW with tuned/shrunk nonlinear models remains exploratory.

### quantiles.csv (45 rows)

RQ2: negative/positive RV slopes at tau 0.1/0.5/0.9 expose tail asymmetry hidden by mean regressions. Reported heteroskedastic-robust p-values do not correct serial dependence.

### robustness.csv (5400 rows)

RQ1–RQ3: compare pre/post January 2025 and horizon sensitivity with momentum and raw document count. A break dummy cannot repair changing news coverage.

### shap.csv (1050 rows)

RQ1/RQ3: development-only SHAP shows inputs used by the validation-selected model. Importance is neither a causal effect nor proof of out-of-sample value.

### strategy.csv (0 rows)

RQ5 economic-value test only: net return includes 10 bps turnover fees and final liquidation. Zero processing latency and omitted extra slippage make it optimistic.

Unavailable for this input sample; no inference reported.

### event_observations.csv (150160 rows)

Each row is a canonical English article and tagged asset, or BTC for untagged market news. CAR uses an hourly BTC market model for altcoins and a past-hour mean for BTC; overlapping articles share market shocks.

### event_tests.csv (288 rows)

Hourly reactions use calendar-lag Bartlett HAC(7) on event-day means, with seven-day block bootstrap for nine preregistered tests. BMP-style CAR and Wilcoxon are supplementary. A shifted placebo window ends before T0.

### event_asymmetry.csv (24 rows)

Negative-minus-positive compares same-day FinBERT and LM terciles on days where both occur. Its paired day test asks whether bad-news reaction differs from good-news reaction.

### event_timing_pairs.csv (38 rows)

The same GDELT article is aligned once to published time and once to first-seen time. Pairwise CAR changes quantify timestamp sensitivity without changing the article sample.

### event_timing.csv (3 rows)

A changed significance flag shows the timing choice can alter a nominal conclusion. This small audited subset cannot calibrate the full corpus.

### event_coverage.csv (1 rows)

Article count, scored count, usable event days and training-only tercile cutoffs limit the scope of hourly inference.

### event_text_scope.csv (5 rows)

Market-wide untagged news falls back to BTC; coin-specific tagged news is counted separately. Fallback percentages refer to usable event rows, not calendar days.

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
Regression samples contain 673–1073 observations; minimum residual degrees of freedom=644. Tiny samples and many parameters make all significance findings exploratory.
RQ1: BTC h=1 FinBERT return slope 0.00327939, Holm p=1; identified=True; this does not validate sentiment-label accuracy.
RQ3: 0/945 estimable hard-narrative coefficients survive table-family Holm at 5%; evaluate against momentum and raw attention.
RQ2: BTC h=1 mean RV slopes negative=-0.00125623, positive=-0.00108407; equality Holm p=1.
RQ2 tail tau=0.1: negative=-0.000197448, positive=1.64827e-05; converged=True, serial inference not corrected.
RQ2 tail tau=0.5: negative=-0.000409451, positive=-0.000110817; converged=True, serial inference not corrected.
RQ2 tail tau=0.9: negative=-0.00126666, positive=-0.0010949; converged=True, serial inference not corrected.
RQ4 BTC sent_finbert predicts ret: lag=7, Holm p=1; predictive direction only.
RQ4 BTC ret predicts sent_finbert: lag=7, Holm p=4.595e-45; predictive direction only.
RQ5 BTC EN: RMSE market=0.0241618, attention=0.0241618, text=0.0241599; CT R²=-0.0004886, DM Holm p=1, CW Holm p=1 (CW exploratory).
RQ5 BTC LGBM: RMSE market=0.0244134, attention=0.0244508, text=0.0243005; CT R²=-0.01216, DM Holm p=1, CW Holm p=1 (CW exploratory).
RQ5 BTC XGB: RMSE market=0.0243238, attention=0.0242997, text=0.0244231; CT R²=-0.02241, DM Holm p=1, CW Holm p=1 (CW exploratory).

## Methods sources

- Clark & West (2007): https://users.ssc.wisc.edu/~cengel/IMF/ClarkWest2007.pdf
- DM-HLN reference arithmetic: https://github.com/johntwk/Diebold-Mariano-Test/blob/master/dm_test.py
- Giacomini & White (2006): https://doi.org/10.1111/j.1468-0262.2006.00718.x
- Hansen, Lunde & Nason (2011): https://www.kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Hansen_Lunde_Nason.pdf
