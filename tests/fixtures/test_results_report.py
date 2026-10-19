import pandas as pd

from src.evaluation import report
from src.evaluation.report import write_results


def test_results_uses_independent_labels_and_current_coverage(tmp_path):
    output = tmp_path / 'real'
    output.mkdir()
    pd.DataFrame([
        {'task': 'sentiment', 'method': method, 'n': 300, 'auc': auc}
        for method, auc in [('FinBERT', .894), ('LM', .718), ('Harvard IV-4', .726)]
    ]).to_csv(tmp_path / 'sentiment_validation.csv', index=False)

    write_results({}, output)
    report = (output / 'RESULTS.md').read_text(encoding='utf-8')

    assert '300 tiêu đề gán nhãn độc lập' in report
    assert 'AUC FinBERT=0.894, LM=0.718, Harvard IV-4=0.726' in report
    assert 'GDELT đang thu tiếp' not in report
    assert 'cần nhãn kiểm định độc lập' not in report
    assert 'GW có 0 kết quả và MCS có 0 hàng mô hình' in report


def test_results_does_not_claim_labels_without_validation_table(tmp_path):
    output = tmp_path / 'real'
    output.mkdir()

    write_results({}, output)
    report = (output / 'RESULTS.md').read_text(encoding='utf-8')

    assert 'bảng kiểm định nhãn độc lập chưa có' in report
    assert 'FinBERT phân biệt sắc thái tốt hơn' not in report


def test_paper_oos_loss_date_labels_do_not_overlap(tmp_path, monkeypatch):
    import matplotlib.pyplot as plt

    days = pd.date_range('2026-01-01', periods=270, freq='D', tz='UTC')
    forecasts = pd.DataFrame([
        {'asset': 'BTC', 'target': 'ret', 'horizon': 1, 'model': model,
         'version': version, 'date': day, 'target_date': day,
         'actual': .01, 'prediction': .009}
        for model in ('EN', 'LGBM', 'XGB')
        for version in ('market', 'attention', 'text')
        for day in days
    ])
    monkeypatch.setattr(report, 'make_panel',
                        lambda market, text: pd.DataFrame(columns=['asset', 'date']))
    figures = []
    close = plt.close
    monkeypatch.setattr(plt, 'close', figures.append)

    report.paper_figures(pd.DataFrame(), pd.DataFrame(), {'forecasts': forecasts}, tmp_path, 'REAL')
    figure = next(fig for fig in figures if fig.axes[0].get_ylabel() == '30-observation MSE')
    assert [axis.texts[0].get_text() for axis in figure.axes] == ['EN', 'LGBM', 'XGB']
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    labels = [label for label in figure.axes[-1].get_xticklabels()
              if label.get_visible() and label.get_text()]
    bounds = sorted((label.get_window_extent(renderer) for label in labels),
                    key=lambda box: box.x0)
    assert 3 <= len(bounds) <= 5
    assert all(left.x1 + 2 < right.x0 for left, right in zip(bounds, bounds[1:]))
    for fig in figures:
        close(fig)
