# Crypto Narrative & NLP Sentiment Intelligence

**Blueprint 10 – Công nghệ ứng dụng trong Tài chính (UEL).** Xây chỉ số sentiment, attention và narrative intensity từ tin tức crypto, kiểm định xem chúng có thông tin gia tăng (incremental) cho return, volatility, volume của BTC/ETH và vài coin lớn hay không. Thiết kế đầy đủ: [`docs/blueprint.md`](docs/blueprint.md).

> Nghiên cứu học thuật, không phải khuyến nghị đầu tư.

## Câu hỏi nghiên cứu
| | Câu hỏi | Kiểm định |
|---|---|---|
| RQ1 | Transformer (FinBERT) có tốt hơn từ điển (LM, Harvard IV-4)? | validation gán tay + hồi quy so sánh |
| RQ2 | Tin xấu tác động mạnh hơn tin tốt? | Wald β⁻ = β⁺ trên RV |
| RQ3 | Narrative nào liên hệ mạnh nhất với return/RV/volume? | attention_k trong hồi quy HAC |
| RQ4 | Text dẫn giá hay phản ứng theo giá? | VAR/Granger hai chiều |
| RQ5 | Text cải thiện dự báo out-of-sample? | market-only vs market+text, Diebold–Mariano |

## Nguyên tắc dữ liệu (rút từ góp ý Đề án 05)
- Nhánh chính: **tin tiếng Anh gốc + thư viện chuẩn quốc tế**; không dịch Việt→Anh để chấm.
- Nhánh phụ tiếng Việt: chấm bằng **từ điển tài chính tiếng Việt** (`dict/fin_vn.csv`, `dict/crypto_vn.csv`).
- Gán ngày theo **thời điểm ra công chúng** `public_ts_utc`; báo cáo độ chính xác timestamp.
- Nguồn có sẵn text (GDELT, RSS, SEC EDGAR) thì lấy text, không OCR.
Chi tiết: [`docs/PORTED.md`](docs/PORTED.md).

## Pipeline
```
GDELT / RSS / SEC / tin VN → dedup + UTC + asset tag → documents
  → LM · Harvard · FinBERT · VietScorer · LDA/BERTopic/zero-shot → doc_scores
  → text_daily (sentiment, attention_k) ⨝ market_daily (Binance) → HAC · VAR/Granger · EN/XGB/LGBM walk-forward
  → outputs/ (tables, figures) → dashboard/ + paper/
```

## Chạy
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=src                                 # Windows: set PYTHONPATH=src
pytest -q
```
Tải **Loughran–McDonald Master Dictionary** (https://sraf.nd.edu/loughranmcdonald-master-dictionary/) vào `dict/`. Email liên hệ và API key đặt ở `config/config.local.yaml` / `.env` (không commit).

## Làm việc với 2 agent
**Bắt đầu: [`docs/prompts/START.md`](docs/prompts/START.md)** (clone → 2 prompt). Claude Code và Codex chạy song song trên 2 worktree: [`docs/PLAN.md`](docs/PLAN.md) (phân công), [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md) (schema), [`docs/prompts/`](docs/prompts) (prompt từng phiên), [`docs/PROGRESS.md`](docs/PROGRESS.md) (nhật ký).

## Cấu trúc
```
config/ dict/ data/{raw,interim,processed}/ src/{data,features,models,evaluation,utils}/
notebooks/ dashboard/ tests/ outputs/{tables,figures}/ paper/ docs/
```
Nguồn code tái dùng và giấy phép: [`CREDITS.md`](CREDITS.md).
