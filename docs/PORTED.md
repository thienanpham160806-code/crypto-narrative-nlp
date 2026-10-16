# Tái dùng từ `disclosure-tone-car` (Đề án 05)

| File mới | Gốc | Trạng thái | Việc còn lại |
|---|---|---|---|
| `src/utils/common.py` | `src/common.py` | ✅ chạy | — (thêm `to_utc`) |
| `src/utils/http.py` | `src/us/edgar_client.py` + `src/vn/http.py` | ✅ chạy | — |
| `src/features/lexicon/tokenize.py` | `us_clean.tokenize` (MIT, lm2011-replication) | ✅ chạy | — |
| `src/features/lexicon/scoring.py` | `src/textkit/scoring.py` | ✅ test pass | — |
| `src/features/lexicon/dictionaries.py` | `src/textkit/dictionaries.py` | ✅ | tải LM Master Dictionary vào `dict/` |
| `dict/fin_vn.csv` | `dict/fin_vn.csv` (201 từ Việt hóa LM) | ✅ | **thêm `dict/crypto_vn.csv`** (sàn, rút thảm, lừa đảo, hack, phá giá, niêm yết, ETF, tiền mã hóa…) |
| `src/features/finbert.py` | `src/analysis/a05_finbert.py` | ✅ tổng quát hóa | chạy trên documents |
| `src/utils/llm_client.py` | `src/textkit/llm_client.py` | 🟡 copy nguyên | bỏ phần OCR, thêm `classify_narrative()` |
| `src/evaluation/event_study.py` | `src/analysis/a02_event.py` | 🟡 copy nguyên | viết lại `main()` cho 24/7, T0 = bar sau `public_ts_utc` |
| `tests/test_lexicon.py` | `tests/test_core.py` | ✅ 5 pass | — |

Không port: OCR/Tesseract, crawl BCTN CafeF, EDGAR 10-K, a03 regress (cross-section CAR — khác bài toán time-series; chỉ học cách in bảng có sao).
Có thể học ý tưởng: `v05_news.py` (API tin CafeF theo mã, quy tắc giờ đăng VN, cờ tháng hổng dữ liệu) → nhánh tin tiếng Việt; dashboard React cũ (`dashboard/frontend`) → bố cục trang, nhưng UI mới dựng lại bằng impeccable.

## Bài học từ góp ý của thầy (Đề án 05) áp vào đây
1. **Không dịch Việt→Anh rồi chấm.** Nhánh chính là tin tiếng Anh gốc + công cụ chuẩn quốc tế (LM, Harvard IV-4, FinBERT). Tin về crypto ở VN có bản tiếng Anh (vd VnExpress International, VIR) → dùng bản Anh.
2. **Văn bản tiếng Việt (tin, PDF văn bản pháp lý về tài sản số) → từ điển tài chính tiếng Việt** (`fin_vn.csv` + `crypto_vn.csv`), khớp cụm dài nhất + phủ định (`VietScorer`), đối chứng VietSentiWordNet. Không đưa tiếng Việt qua FinBERT.
3. **Ngày ra công chúng là biến then chốt.** Lưu `published_at_utc`, `first_seen_utc`, `ts_source`; gán ngày bằng `public_ts_utc`. Báo cáo bảng *độ chính xác timestamp* (chênh lệch published vs first_seen, % tin có giờ, % lệch > 1 giờ) và event study giá quanh `public_ts_utc` để kiểm chứng.
4. **Có sẵn text thì lấy text** (giống Mỹ có file .txt EDGAR): GDELT/RSS/API trả text; văn bản SEC liên quan ETF crypto lấy dạng .txt/.htm từ EDGAR — không OCR PDF khi đã có text.
