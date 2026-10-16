# ADOPT.md — đưa phát hiện vào kế hoạch (R3)

Nguồn: `docs/research/REPOS.md` (R#…) và `docs/research/PAPERS.md` (P#…). Ngày 2026-10-16.
Quy tắc: mỗi agent chỉ làm mục thuộc vùng của mình (`docs/PLAN.md`). Chép code từ repo MIT/Apache/BSD/CC0 thì ghi nguồn vào `CREDITS.md`. Không có mục nào được đổi `src/` của agent kia.

## P1 — làm trước giai đoạn kế

| # | Thay đổi | File / hàm | Owner | Nguồn | Vì sao |
|---|---|---|---|---|---|
| 1 | Báo **Clark–West** cạnh Diebold–Mariano khi so market-only với market+text | `src/evaluation/oos.py::clark_west` (mới), gọi trong `src/models/ml.py` | Codex | R#1 | market-only lồng trong market+text. DM khi đó nghiêng về mô hình nhỏ, nên kết luận "text không giúp" có thể sai. |
| 2 | Test bất biến purge/embargo: `max(train_target_date) + h + embargo < min(test_origin)` cho mọi refit | `tests/fixtures/test_pipeline.py` | Codex | R#1 | PR #1 ghi đã purge theo target date; cần test khóa lại. |
| 3 | Thêm bậc **market + attention thô** (log n_docs) giữa market-only và market+text | `src/models/ml.py`, `src/models/econometrics.py` | Codex | P#3 (Liu & Tsyvinski) | Sentiment/narrative chỉ có giá trị gia tăng nếu vượt được momentum và độ chú ý thô. |
| 4 | Nguồn phụ **CryptoPanic CC0** (2023-01 → 2025-12-03). Đối chiếu múi giờ `newsDatetime` bằng URL trùng GDELT trước khi dùng. | `src/data/news_cryptopanic_ds.py` (mới), `src/data/build_documents.py` | Claude | R#5 | Bù phần tin crypto chuyên ngành mà GKG lấy mẫu 25% bỏ sót. CryptoPanic API thì phải trả phí. |
| 5 | Phiếu positive/negative của CryptoPanic làm **nhãn yếu thứ hai** cho RQ1 | `src/features/validation.py` | Claude | R#5, P#5 (Ider & Lessmann: weak supervision) | 300 nhãn tay ít; nhãn yếu cho thêm hàng nghìn tiêu đề để so LM/HV/FinBERT. |

## P2

| # | Thay đổi | File / hàm | Owner | Nguồn |
|---|---|---|---|---|
| 6 | Cột `cryptobert_sentiment` (ElKulako/cryptobert, MIT), chỉ ở bảng validation | `src/features/finbert.py`, `validation.py` | Claude | R#4, P#5 |
| 7 | Validation báo thêm AUC (FinBERT/CryptoBERT dùng xác suất) và tỷ lệ lớp | `src/features/validation.py` | Claude | P#6 (Loginova et al.) |
| 8 | Hướng tác động của narrative regulation: `restrictive` (cấm, kiện) vs `framework` (luật rõ, cấp phép). Lưu ở `doc_scores.regulation_dir`, không đổi 8 cột attention. | `src/features/narrative.py`, DATA_CONTRACT §2 | Claude | P#10 (Auer & Claessens) |
| 9 | Hình "topic prevalence" bằng `BERTopic.topics_over_time` (chỉ hiển thị, không làm feature) | `dashboard/` | Claude | R#2 |
| 10 | Hiệu chỉnh Harvey–Leybourne–Newbold cho DM; test số đối chiếu `dm_test` | `src/evaluation/oos.py` | Codex | R#6 |
| 11 | R² ngoài mẫu đệ quy (Campbell–Thompson) cạnh RMSE | `src/evaluation/oos.py::metrics` | Codex | P#4 |
| 12 | Quy tắc LLM: chỉ dùng cho validation. Không làm feature dự báo trên test nếu knowledge cutoff của model sau `split.valid_end`. | `src/utils/llm_client.py` (docstring), paper §Phương pháp | Claude | R#12 |

## P3
| # | Thay đổi | Owner | Nguồn |
|---|---|---|---|
| 13 | Giacomini–White và Model Confidence Set cho EN/XGB/LGBM | Codex | R#7 |
| 14 | Sentiment theo narrative (`sent_<k>`): aspect-based, cần đổi schema text_daily | Claude ↔ Codex | P#6 |
| 15 | UCRY Policy/Price (Lucey et al.) làm biến kiểm soát, nếu tải được chuỗi | Codex | P#11 |

## Đề xuất chỉnh tài liệu chung
- `docs/DATA_CONTRACT.md` §1: thêm `source = cryptopanic_ds` khi làm mục 4. `ts_source = dataset` (chưa rõ múi giờ → ghi kết quả đối chiếu vào `timestamp_accuracy.csv`).
- `docs/DATA_CONTRACT.md` §2: thêm `regulation_dir` (mục 8) khi làm.
- `docs/PLAN.md` giai đoạn 2: thêm dòng "Clark–West + bậc attention thô" vào điều kiện xong của X3; thêm "nhãn yếu CryptoPanic" vào điều kiện xong của C2.
- Không đổi `text_daily`: `log(n_docs)` tự tính từ `n_docs`.

## Đã có, không cần làm
- Fit vectorizer/LDA/BERTopic chỉ trên train; chọn K trên valid (`src/features/narrative.py`). Đây là bẫy #4 trong REPOS.
- Holm + BH cho các bảng DM (`src/models/robustness.py`, `src/models/run.py`).
- Cắt ngày sau khi đổi UTC, dedup giữ bản sớm nhất (`src/features/daily_index.py`, `src/data/build_documents.py`).
