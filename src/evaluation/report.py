"""Offline paper figures, coverage audit, and economic interpretation of each table."""
from pathlib import Path

import numpy as np
import pandas as pd

from src.models.panel import make_panel, MARKET, TEXT_CORE


MEANING = {
    'coverage': 'Coverage distinguishes collected-index news days, FinBERT-scored days and complete model rows; it does not prove absence of real-world news. Sparse dates can select an unrepresentative sample.',
    'regressions': 'RQ1/RQ3: coefficients measure conditional predictive associations with returns, RV and volume. Compare market, raw attention and text on the same sample; they do not validate sentiment labels or identify causal effects.',
    'wald': 'RQ2: rejection means negative and positive sentiment have different conditional RV slopes. It does not prove that negative news causes volatility.',
    'granger': 'RQ4: text-to-market significance indicates a predictive lead, while the reverse direction suggests price feedback. Missing/short contiguous samples cannot support this inference.',
    'oos': 'RQ5: positive Campbell–Thompson R² beats the recursive historical mean; lower forecast loss is better. Positive DM/CW favors text; CW with tuned/shrunk nonlinear models remains exploratory.',
    'forecasts': 'RQ5: dated paired forecasts let reviewers audit when information and targets were available. They are research predictions, not executable trade instructions.',
    'strategy': 'RQ5 economic-value test only: net return includes 10 bps turnover fees and final liquidation. Zero processing latency and omitted extra slippage make it optimistic.',
    'shap': 'RQ1/RQ3: development-only SHAP shows inputs used by the validation-selected model. Importance is neither a causal effect nor proof of out-of-sample value.',
    'tuning': 'RQ5: validation losses choose model settings before the frozen test pass. Test results never revise these settings.',
    'stationarity': 'RQ4: ADF tests a unit-root null and KPSS tests a level-stationarity null. Conflicting outcomes call for specification review; KPSS p-values are lookup-table bounds.',
    'robustness': 'RQ1–RQ3: compare pre/post January 2025 and horizon sensitivity with momentum and raw document count. A break dummy cannot repair changing news coverage.',
    'robustness_status': 'Document-weighted and price-excluded sensitivity requires reaggregation from canonical articles. Pending means no economic conclusion from that variant.',
    'quantiles': 'RQ2: negative/positive RV slopes at tau 0.1/0.5/0.9 expose tail asymmetry hidden by mean regressions. Reported heteroskedastic-robust p-values do not correct serial dependence.',
    'rolling_quantiles': 'RQ2: 500-calendar-day, 20-day-step coefficients show temporal stability. Overlapping windows are dependent and cannot be counted as independent replications.',
    'quantile_status': 'Short samples cannot estimate the requested rolling window. An unavailable window provides no evidence of stable tail effects.',
    'refit_audit': 'RQ5: every recorded refit satisfies max(train_target_date) + horizon + embargo < origin. This conservative purge also applies to fixed-window GW fits.',
    'ml_status': 'RQ5: pending or skipped cases lack enough honest validation/test observations or contiguous strategy dates. Missing results are not zero effects.',
    'gw': 'RQ5: GW uses fixed 500-observation training windows and origin-known return as its conditioning instrument. Rejection indicates conditional forecast differences, not which model dominates every state.',
    'mcs': 'RQ5: the 90% Model Confidence Set retains models not rejected by Tmax block-bootstrap elimination. Membership does not establish superiority or select a trading model on test data.',
    'ucry_regressions': 'RQ3: UCRY-controlled regressions use only dates with released weekly observations, in a separate common sample. Retrospective indices lack vintages and cannot justify live forecast claims.',
    'ucry_wald': 'RQ2/RQ3: the asymmetry test conditions on weekly uncertainty where available. Its sample differs from the main table; unavailable post-2024 UCRY is never extrapolated.',
    'event_observations': 'Each row is a canonical English article and tagged asset, or BTC for untagged market news. CAR uses an hourly BTC market model for altcoins and a past-hour mean for BTC; overlapping articles share market shocks.',
    'event_tests': 'Hourly reactions are tested on event-day means, so multiple articles on one day form one cluster. BMP-style CAR is estimation-error standardized and day clustered. The −24h placebo omits [0,24], whose inclusive endpoint would overlap T0.',
    'event_asymmetry': 'Negative-minus-positive compares same-day FinBERT and LM terciles on days where both occur. Its paired day test asks whether bad-news reaction differs from good-news reaction.',
    'event_timing_pairs': 'The same GDELT article is aligned once to published time and once to first-seen time. Pairwise CAR changes quantify timestamp sensitivity without changing the article sample.',
    'event_timing': 'A changed significance flag shows the timing choice can alter a nominal conclusion. This small audited subset cannot calibrate the full corpus.',
    'event_coverage': 'Article count, scored count, usable event days and training-only tercile cutoffs limit the scope of hourly inference.',
}


def preliminary_findings(tables, real):
    lines = ['These are partial real-data associations.' if real else
             'Every result below is synthetic code validation; none establishes a real-market effect.']
    regression = tables.get('regressions', pd.DataFrame())
    if not regression.empty:
        if real and 'resid_df' in regression:
            lines.append(f'Regression samples contain {regression.nobs.min():g}–{regression.nobs.max():g} observations; '
                         f'minimum residual degrees of freedom={regression.resid_df.min():g}. '
                         'Tiny samples and many parameters make all significance findings exploratory.')
        selected = regression.loc[(regression.asset == 'BTC') & (regression.horizon == 1) &
                                  (regression.target == 'ret') & (regression.term == 'sent_finbert')]
        if not selected.empty:
            row = selected.iloc[0]
            lines.append(f'RQ1: BTC h=1 FinBERT return slope {row.coef:.6g}, Holm p={row.p_holm:.4g}; '
                         f'identified={getattr(row, "identified", True)}; this does not validate sentiment-label accuracy.')
        narrative = regression.loc[regression.term.str.startswith('attention_')]
        lines.append(f'RQ3: {int(narrative.p_holm.lt(.05).sum())}/{int(narrative.p_holm.notna().sum())} estimable hard-narrative coefficients '
                     'survive table-family Holm at 5%; evaluate against momentum and raw attention.')
    wald = tables.get('wald', pd.DataFrame())
    if not wald.empty:
        selected = wald.loc[(wald.asset == 'BTC') & (wald.horizon == 1)]
        if not selected.empty:
            row = selected.iloc[0]
            lines.append(f'RQ2: BTC h=1 mean RV slopes negative={row.beta_neg:.6g}, positive={row.beta_pos:.6g}; '
                         f'equality Holm p={row.p_holm:.4g}.')
    quantiles = tables.get('quantiles', pd.DataFrame())
    if not quantiles.empty:
        for row in quantiles.loc[(quantiles.asset == 'BTC') & (quantiles.horizon == 1)].itertuples():
            lines.append(f'RQ2 tail tau={row.tau:g}: negative={row.beta_neg:.6g}, positive={row.beta_pos:.6g}; '
                         f'converged={row.converged}, serial inference not corrected.')
    granger = tables.get('granger', pd.DataFrame())
    if not granger.empty and 'causing' in granger:
        for row in granger.loc[(granger.asset == 'BTC') & (granger.outcome == 'ret')].itertuples():
            lines.append(f'RQ4 BTC {row.causing} predicts {row.caused}: lag={row.lag}, Holm p={row.p_holm:.4g}; '
                         'predictive direction only.')
    oos = tables.get('oos', pd.DataFrame())
    if not oos.empty:
        selected = oos.loc[(oos.asset == 'BTC') & (oos.horizon == 1) & (oos.target == 'ret')]
        for model, group in selected.groupby('model'):
            group = group.set_index('version')
            if {'market', 'attention', 'text'}.issubset(group.index):
                row = group.loc['text']
                lines.append(f'RQ5 BTC {model}: RMSE market={group.loc["market", "rmse"]:.6g}, '
                             f'attention={group.loc["attention", "rmse"]:.6g}, text={row.rmse:.6g}; '
                             f'CT R²={row.r2_oos_ct:.4g}, DM Holm p={getattr(row, "dm_p_holm", np.nan):.4g}, '
                             f'CW Holm p={getattr(row, "cw_p_holm", np.nan):.4g} (CW exploratory).')
    else:
        lines.append('RQ5 pending: no honest validation/test forecast comparison is available for this sample.')
    return lines


def coverage(market, text, config):
    panel = make_panel(market, text)
    rows = []
    for asset, frame in panel.groupby('asset'):
        news = frame.loc[frame.n_docs.gt(0)]
        scored = news.loc[news.sent_finbert.notna()]
        tagged = text.loc[text.asset.eq(asset) & text.n_docs.gt(0)]
        tagged_dates = pd.to_datetime(tagged.date, utc=True).drop_duplicates()
        asset_news_days = int(tagged_dates.isin(frame.date).sum())
        optional = [c for c in frame if c.startswith(('disagreement', 'soft_attention_', 'attention_soft_', 'ucry_'))]
        attention = [f'attention_{k}' for k in config['nlp']['narratives']]
        usable = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=[*MARKET, *TEXT_CORE, *attention, *optional, 'y_ret', 'y_rv'])
        fallback_model_days = int((~usable.date.isin(tagged_dates)).sum())
        cutoff = pd.Timestamp(config['split']['valid_end'], tz='UTC')
        rows.append(dict(asset=asset, calendar_days=len(frame), news_days=len(news),
                         pct_days_with_news=100*len(news)/len(frame),
                         asset_news_days=asset_news_days,
                         pct_days_with_asset_news=100*asset_news_days/len(frame),
                         usable_model_days=len(usable),
                         fallback_model_days=fallback_model_days,
                         finbert_days=len(scored), pct_days_with_finbert=100*len(scored)/len(frame),
                         model_development_days=int(usable.target_date.le(cutoff).sum()),
                         model_test_days=int((usable.target_date.gt(cutoff) & usable.date.ge(cutoff)).sum()),
                         model_train_days=int(usable.target_date.le(pd.Timestamp(config['split']['train_end'], tz='UTC')).sum()),
                         model_valid_days=int((usable.target_date.gt(pd.Timestamp(config['split']['train_end'], tz='UTC')) & usable.target_date.le(cutoff)).sum()),
                         news_start=news.date.min(), news_end=news.date.max(),
                         model_start=usable.date.min(), model_end=usable.date.max(),
                         configured_start=config['sample']['start'], configured_end=config['sample']['end']))
    return pd.DataFrame(rows)


def paper_figures(market, text, tables, directory, label):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    mode = 'REAL: partial corpus' if label.startswith('REAL') else 'SYNTHETIC: code validation'

    def save(fig, name):
        fig.tight_layout()
        path = directory/f'{name}.svg'
        fig.savefig(path, metadata={'Date': None})
        fig.savefig(directory/f'{name}.png', dpi=160)
        plt.close(fig)
        paths.append(path)

    panel = make_panel(market, text)
    btc = panel.loc[panel.asset.eq('BTC')].set_index('date')
    if not btc.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        btc.sent_finbert.plot(ax=ax, color='teal', label='FinBERT daily',
                             marker='o' if label.startswith('REAL') else None, markersize=3)
        ax.set_ylabel('Sentiment'); ax.legend(loc='upper left')
        other = ax.twinx()
        btc.close.plot(ax=other, color='grey', alpha=.6, label='BTC close')
        other.set_ylabel('BTC close'); other.legend(loc='upper right')
        ax.set_title(f'{mode}\nSentiment index and BTC price')
        save(fig, 'sentiment_btc')
    forecasts = tables.get('forecasts', pd.DataFrame())
    if not forecasts.empty:
        forecasts = forecasts.copy()
        forecasts['date'] = pd.to_datetime(forecasts.date, utc=True)
        chosen = forecasts.loc[(forecasts.asset == 'BTC') & (forecasts.target == 'ret') & (forecasts.horizon == 1)]
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        for ax, (model, group) in zip(axes, chosen.groupby('model')):
            for version, part in group.groupby('version'):
                part = part.sort_values('date').set_index('date')
                loss = (part.actual-part.prediction).pow(2).rolling(30, min_periods=10).mean()
                ax.plot(loss.index, loss, label=version)
            ax.set_title(model); ax.set_ylabel('30-observation MSE'); ax.legend()
        fig.suptitle(f'{mode}: BTC one-day OOS loss\nNo model selected on test')
        save(fig, 'oos_loss')
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        plotted = False
        for ax, (model, group) in zip(axes, chosen.groupby('model')):
            for version, part in group.groupby('version'):
                part = part.sort_values('target_date')
                dates = pd.to_datetime(part.target_date, utc=True)
                if not dates.diff().dropna().eq(pd.Timedelta(days=1)).all():
                    continue
                pos = part.prediction.gt(0).to_numpy(float)
                turnover = np.abs(np.diff(np.r_[0, pos])); turnover[-1] += pos[-1]
                net = pos*np.expm1(part.actual.to_numpy())-.001*turnover
                ax.plot(dates, np.cumprod(1+net), label=version)
                plotted = True
            ax.set_title(model); ax.set_ylabel('Net wealth (start=1)')
            if ax.lines:
                ax.legend()
        if plotted:
            fig.suptitle(f'{mode}: economic-value test only\n10 bps fees; no extra slippage')
            save(fig, 'cumulative_strategy')
        else:
            plt.close(fig)
            for extension in ('svg', 'png'):
                (directory/f'cumulative_strategy.{extension}').unlink(missing_ok=True)
    quantiles = tables.get('quantiles', pd.DataFrame())
    if not quantiles.empty:
        chosen = quantiles.loc[(quantiles.asset == 'BTC') & (quantiles.horizon == 1)].sort_values('tau')
        fig, ax = plt.subplots(figsize=(7, 4))
        for term in ['neg', 'pos']:
            ax.errorbar(chosen.tau, chosen[f'beta_{term}'], yerr=1.96*chosen[f'se_{term}'], marker='o', label=term)
        ax.axhline(0, color='grey', linewidth=.8); ax.legend(); ax.set_xlabel('RV quantile')
        ax.set_title(f'{mode}: BTC predictive RV slopes\nIntervals ignore serial dependence')
        save(fig, 'quantile_coefficients')
    shap = tables.get('shap', pd.DataFrame())
    if not shap.empty:
        chosen = shap.loc[(shap.asset == 'BTC') & (shap.target == 'ret') & (shap.horizon == 1)].nlargest(15, 'mean_abs_shap')
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(chosen.feature[::-1], chosen.mean_abs_shap[::-1], color='teal')
        ax.set_title(f'{mode}\nDevelopment-only SHAP: BTC one-day return')
        ax.set_xlabel('Mean absolute SHAP (return units)')
        save(fig, 'shap_btc')
    return paths


def write_report(market, text, config, tables, output, figures, real=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    tables['coverage'] = coverage(market, text, config)
    label = 'REAL (partial corpus; provenance audit required)' if real else 'SYNTHETIC (code validation only)'
    for name, table in tables.items():
        table.to_csv(output/f'{name}.csv', index=False, encoding='utf-8')
    paths = paper_figures(market, text, tables, figures, label)
    lines = [f'# {label}', '', 'Daily forecast horizon is the single outcome at t+h, not a cumulative h-day return.',
             'Missing news/scores remain missing. No interpolation, fabricated labels or split changes.',
             'Rows with identified=False have rank-deficient design: coefficients are not unique and p-values/standard errors are withheld.',
             'Holm/BH uses each unique comparison table as one family. MCS is evaluation, not test-set model selection.', '',
             '## Actual coverage', '']
    for row in tables['coverage'].itertuples():
        lines.append(f'- {row.asset}: {row.news_days}/{row.calendar_days} corpus news days '
                     f'({row.pct_days_with_news:.2f}%); {row.asset_news_days} asset-tagged news days '
                     f'({row.pct_days_with_asset_news:.2f}%); {row.fallback_model_days} model origins use corpus fallback; '
                     f'FinBERT panel coverage {row.pct_days_with_finbert:.2f}%; '
                     f'news {row.news_start} to {row.news_end}; '
                     f'usable one-day model origins {row.model_start} to {row.model_end} ({row.usable_model_days} rows); '
                     f'train/valid/test={row.model_train_days}/{row.model_valid_days}/{row.model_test_days}.')
    lines += ['', '## Table interpretation', '']
    for name, table in tables.items():
        lines += [f'### {name}.csv ({len(table)} rows)', '', MEANING.get(name, 'Research diagnostic; interpret conditional on sample coverage.'), '']
        if table.empty:
            lines += ['Unavailable for this input sample; no inference reported.', '']
    lines += ['## Figures', '', *[f'- {p.name}' for p in paths], '',
              '## Preliminary RQ1–RQ5', '',
              'RQ1: predictive coefficients cannot rank sentiment accuracy without independent labeled validation.',
              'RQ2: use mean Wald and tail slopes together; quantile serial inference remains a limitation.',
              'RQ3: compare text against raw attention and momentum before attributing value to narrative composition.',
              'RQ4: Granger establishes predictive direction only, conditional on stationarity and contiguous coverage.',
              'RQ5: paired losses, corrected inference and economic-value tests assess incremental value; never choose models on test.', '',
              *preliminary_findings(tables, real), '',
              '## Methods sources', '',
              '- Clark & West (2007): https://users.ssc.wisc.edu/~cengel/IMF/ClarkWest2007.pdf',
              '- DM-HLN reference arithmetic: https://github.com/johntwk/Diebold-Mariano-Test/blob/master/dm_test.py',
              '- Giacomini & White (2006): https://doi.org/10.1111/j.1468-0262.2006.00718.x',
              '- Hansen, Lunde & Nason (2011): https://www.kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Hansen_Lunde_Nason.pdf']
    (output/'README.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return paths


def write_results(tables, output):
    """Report only observed real-data evidence, with per-RQ gaps and economic meaning."""
    def number(value, digits=4):
        return f'{value:.{digits}g}' if pd.notna(value) else 'NA'

    coverage_rows = tables.get('coverage', pd.DataFrame())
    event = tables.get('event_coverage', pd.DataFrame())
    tests = tables.get('event_tests', pd.DataFrame())
    asymmetry = tables.get('event_asymmetry', pd.DataFrame())
    timing = tables.get('event_timing', pd.DataFrame())
    forecasts = tables.get('forecasts', pd.DataFrame())
    granger = tables.get('granger', pd.DataFrame())
    regression = tables.get('regressions', pd.DataFrame())
    lines = ['# Kết quả thật, bộ tin đang thu', '',
             'Bằng chứng dưới đây chỉ áp dụng cho dữ liệu đã thu. Tin cùng ngày được gom theo ngày khi kiểm định sự kiện.', '']
    if not coverage_rows.empty:
        row = coverage_rows.loc[coverage_rows.asset.eq('BTC')].iloc[0]
        lines += [f'Coverage: corpus chung có {row.news_days}/{row.calendar_days} ngày có tin '
                  f'({row.pct_days_with_news:.2f}%); riêng BTC có {row.asset_news_days} ngày tin gắn mã '
                  f'({row.pct_days_with_asset_news:.2f}%), {row.fallback_model_days} ngày mô hình dùng corpus chung; '
                  f'từ {row.news_start} đến {row.news_end}. Core spec dùng {row.usable_model_days} ngày BTC, '
                  f'train/valid/test={row.model_train_days}/{row.model_valid_days}/{row.model_test_days}.', '']
    if not event.empty:
        row = event.iloc[0]
        lines += [f'Sự kiện giờ: {row.canonical_en_articles} tin canonical tiếng Anh, '
                  f'{row.usable_event_rows} cặp tin–asset trên {row.usable_event_days} ngày; '
                  f'{row.scored_finbert_articles} tin có FinBERT. Mẫu {row.first_event} đến {row.last_event}.', '']
        lines += [f'Bản documents hiện phủ {row.gdelt_article_days} ngày GKG và {row.sec_article_days} ngày SEC; '
                  'text_daily có thể chưa được build lại trên cùng ảnh chụp dữ liệu.', '']
    if not tests.empty:
        for metric, unit in [('car', '%'), ('absret', '%'), ('volume', 'log điểm')]:
            row = tests.loc[(tests.grouping == 'all') & (tests.window == '[0,4]') & (tests.metric == metric)]
            if not row.empty:
                item = row.iloc[0]
                amount = item['mean']*100 if metric != 'volume' else item['mean']
                lines.append(f'Phản ứng chung [0,4]h {metric}: {number(amount)} {unit}, '
                             f'{item.n_days} ngày, p t Holm={number(item.p_t_holm)}.')
        lines.append('Abnormal volume là chênh log(1+USD volume) so với 144 giờ ước lượng trước tin; '
                     'abnormal |return| là chênh tổng độ lớn lợi suất log.\n')
    lines += ['## RQ1: FinBERT và từ điển', '']
    selected = regression.loc[(regression.asset == 'BTC') & (regression.target == 'ret') &
                              (regression.horizon == 1) & (regression.term.isin(['sent_finbert', 'sent_lm', 'sent_hv']))] if not regression.empty else pd.DataFrame()
    if not selected.empty:
        lines.append('Đã có: hệ số BTC h=1 ' + '; '.join(
            f'{row.sentiment}={number(row.coef)}, Holm p={number(row.p_holm)} (n={row.nobs:g})'
            for row in selected.itertuples()) + '.')
    else:
        lines.append('Đã có: chưa đủ hồi quy BTC h=1 để so các bộ chấm.')
    lines += ['Chưa đủ: cần nhãn kiểm định độc lập và mẫu tin dày hơn để xếp hạng độ chính xác.',
              'Nghĩa kinh tế: chênh hệ số dự báo không chứng minh FinBERT đọc tin đúng hơn từ điển.', '',
              '## RQ2: tin xấu và tin tốt', '']
    row = asymmetry.loc[(asymmetry.tone == 'finbert_tercile') & (asymmetry.window == '[0,4]') &
                        (asymmetry.metric == 'car')] if not asymmetry.empty else pd.DataFrame()
    if not row.empty:
        item = row.iloc[0]
        lines.append(f'Đã có: CAR [0,4]h FinBERT xấu trừ tốt = {number(item.negative_minus_positive*100)} điểm %, '
                     f'{item.n_days} ngày ghép cặp, p t={number(item.p_t)}, Holm={number(item.p_t_holm)}; xem event_asymmetry.csv.')
    else:
        lines.append('Đã có: chưa đủ ngày ghép cặp hai nhóm FinBERT.')
    short = asymmetry.loc[(asymmetry.tone == 'finbert_tercile') & (asymmetry.window == '[0,1]') &
                          (asymmetry.metric == 'absret')] if not asymmetry.empty else pd.DataFrame()
    if not short.empty:
        item = short.iloc[0]
        lines.append(f'Biến động tuyệt đối [0,1]h xấu trừ tốt = {number(item.negative_minus_positive*100)} điểm %, '
                     f'Holm t={number(item.p_t_holm)}, Holm Wilcoxon={number(item.p_wilcoxon_holm)}; '
                     'hai kiểm định chưa đồng thuận.')
    lines += ['Chưa đủ: nhiều giờ có tin chồng lấp; Wald và phân vị theo ngày vẫn phụ thuộc coverage thưa.',
              'Nghĩa kinh tế: CAR khác nhau là phản ứng giá có điều kiện, chưa xác định tác động nhân quả của sắc thái tin.', '',
              '## RQ3: narrative', '']
    for narrative in ('regulation', 'security_hacks', 'etf_institutional'):
        row = tests.loc[(tests.grouping == 'narrative') & (tests.group == narrative) &
                        (tests.window == '[0,4]') & (tests.metric == 'car')] if not tests.empty else pd.DataFrame()
        lines.append(f'Đã có: {narrative} CAR [0,4]h = {number(row.iloc[0]["mean"]*100)}%, '
                     f'{int(row.iloc[0].n_days)} ngày, p t={number(row.iloc[0].p_t)}, Holm={number(row.iloc[0].p_t_holm)}.' if not row.empty else
                     f'Đã có: {narrative} chưa đủ 5 ngày sự kiện dùng được.')
    lines += ['Chưa đủ: cần hiệu chỉnh nhiều kiểm định và kiểm soát tin trùng giờ để so thứ hạng narrative.',
              'Nghĩa kinh tế: nhóm có CAR lớn hơn chỉ là liên hệ trong mẫu tin đã thu.', '',
              '## RQ4: tin dẫn giá hay giá đi trước tin', '']
    pre = tests.loc[(tests.grouping == 'all') & (tests.window == '[-4,-2]') &
                    (tests.metric == 'car')] if not tests.empty else pd.DataFrame()
    if not pre.empty:
        item = pre.iloc[0]
        lines.append(f'Đã có: CAR trước tin nghiêm ngặt [-4,-2]h = {number(item["mean"]*100)}%, '
                     f'{item.n_days} ngày, p t={number(item.p_t)}, Holm={number(item.p_t_holm)}. '
                     '[-4,0]h có cả nến T0 nên không thuần trước tin.')
    if not timing.empty:
        for item in timing.itertuples():
            lines.append(f'Độ nhạy giờ [{item.window.replace("_", ",")}]: {item.n_unique_articles} tin, '
                         f'{item.n_pairs} cặp tin–asset trên {item.n_days} ngày, '
                         f'CAR published={number(item.mean_car_published*100)}%, '
                         f'seen={number(item.mean_car_seen*100)}%, '
                         f'p published/seen={number(item.p_public)}/{number(item.p_seen)}, '
                         f'đổi kết luận p<0,05={item.significance_changed}, '
                         f'sau Holm={getattr(item, "significance_changed_holm", np.nan)}; '
                         f'kiểm định chênh lệch ghép cặp Holm p={number(getattr(item, "p_paired_t_holm", np.nan))}.')
    available = granger.pvalue.notna().sum() if not granger.empty else 0
    lines += [f'Chưa đủ: {available} kiểm định Granger dùng được; VAR chỉ chạy trên đoạn ngày liên tục ≥30.',
              'Nghĩa kinh tế: CAR trước T0 gợi ý giá đã phản ánh thông tin sớm hoặc sai số giờ công bố; không chứng minh rò rỉ.', '',
              '## RQ5: dự báo ngoài mẫu', '']
    fan_input = forecasts.loc[(forecasts.asset == 'BTC') & (forecasts.target == 'rv') &
                              (forecasts.horizon == 1) & (forecasts.model == 'EN') &
                              (forecasts.version == 'text')] if not forecasts.empty else pd.DataFrame()
    lines.append(f'Đã có: {len(forecasts)} hàng dự báo ngoài mẫu; {len(fan_input)} '
                 'hàng BTC EN/text RV h=1 đúng schema dashboard/export.py.')
    if not fan_input.empty:
        latest = fan_input.loc[fan_input.date.idxmax()]
        matured = int((pd.to_datetime(fan_input.target_date, utc=True) < pd.Timestamp(latest.date)).sum())
        lines.append(f'As-of {latest.date}: RV dự báo={number(latest.prediction)}, '
                     f'{matured} sai số quá khứ đã biết; fan chart đủ ngưỡng 30.' if matured >= 30 else
                     f'As-of {latest.date}: RV dự báo={number(latest.prediction)}, '
                     f'{matured} sai số quá khứ đã biết; fan chart chưa đủ ngưỡng 30.')
    oos = tables.get('oos', pd.DataFrame())
    row = oos.loc[(oos.asset == 'BTC') & (oos.target == 'rv') & (oos.horizon == 1) &
                  (oos.model == 'EN') & (oos.version == 'text')] if not oos.empty else pd.DataFrame()
    if not row.empty:
        item = row.iloc[0]
        lines.append(f'EN/text BTC RV h=1: R² CT={number(item.r2_oos_ct)}, RMSE={number(item.rmse)}; '
                     f'DM Holm p={number(getattr(item, "dm_p_holm", np.nan))}.')
    lines += ['Chưa đủ: ngày test có tin rời rạc; DM/GW/MCS cần đoạn liên tục. Dải fan theo sai số có thể xuống dưới RV=0.',
              'Nghĩa kinh tế: dự báo thật có thể xuất cho dashboard; lợi ích của text chỉ đáng tin nếu kiểm định ghép cặp có đủ đoạn liên tục.', '']
    audit_path = Path(output).parent/'timestamp_accuracy.csv'
    audit = pd.read_csv(audit_path) if audit_path.is_file() else pd.DataFrame()
    gdelt = audit.loc[audit.source.eq('gdelt')] if not audit.empty else pd.DataFrame()
    if not gdelt.empty:
        item = gdelt.iloc[0]
        lines.append(f'Giới hạn thời điểm: GDELT seendate trễ tuyệt đối trung vị '
                     f'{number(item.median_abs_lag_min)} phút trong {int(item.n_pairs)} cặp audit.')
    lines += ['GDELT đang thu tiếp; các p-value chưa giải quyết lựa chọn mẫu tin và nhiều sự kiện trùng ngày.', '']
    (Path(output)/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
