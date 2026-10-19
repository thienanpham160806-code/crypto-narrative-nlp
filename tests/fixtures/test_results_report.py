import pandas as pd

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
