# REPOS.md — mã nguồn GitHub đáng học (R1)

Tra ngày 2026-10-16 bằng `gh search repos` + `gh api` (đọc file thật, không clone). Sao/ngày cập nhật lấy từ GitHub API hôm nay.
Giấy phép: MIT/Apache/BSD/CC0 → được chép code (ghi nguồn vào `CREDITS.md`); GPL hoặc không giấy phép → chỉ học ý tưởng, tự viết lại.
Owner theo `docs/PLAN.md`: Claude = text/NLP/dashboard/paper; Codex = market/models/evaluation.

Lọc: bỏ repo chỉ có notebook rời (vd `paulcodrea/crypto_price_prediction`, 7 notebook) và bot giao dịch không có đánh giá.
Giữ 3 repo yếu (#10–#12) vì chúng minh họa đúng các bẫy đề tài phải tránh.

## 1. ITheClixs/crypto-return-predictability — ★3, cập nhật 2026-09-26, **MIT**
- Paper kèm repo: kiểm định martingale cho lợi suất BTC/ETH/SOL ngày, h = 1 và 7, 2020-07 → 2026-07. Có CI, 154 test.
- Làm tốt:
  - `src/cryptoforecast/splits.py::walk_forward_splits`: walk-forward có purge h dòng + embargo, bất biến `max(train) + horizon + embargo < min(test)` được test.
  - `evaluate/stats.py::clark_west`: Clark–West cho mô hình lồng nhau. Repo cho thấy DM nghiêng về mô hình nhỏ khi benchmark lồng trong mô hình lớn.
  - `stats.py::holm_adjusted`, `benjamini_hochberg_adjusted`, `deflated_sharpe_ratio`, `block_bootstrap_ci`.
- Điểm yếu: chỉ dùng biến giá, không có text. Không dùng được trực tiếp cho RQ1–RQ4.
- Áp dụng: `src/evaluation/oos.py` (Codex). "market-only" lồng trong "market+text" → báo Clark–West bên cạnh DM. Thêm purge/embargo vào `src/models/ml.py`.
- Ưu tiên: **P1**.

## 2. MaartenGr/BERTopic — ★7.9k, cập nhật 2026-10-16, **MIT**
- Làm tốt: `BERTopic(zeroshot_topic_list=…, zeroshot_min_similarity=…)` gán chủ đề zero-shot theo tên narrative cho trước; `seed_topic_list` (guided); `topics_over_time()`.
  - Đã kiểm trong `.venv/Lib/site-packages/bertopic/_bertopic.py`: dòng 154–156 và 797.
- Điểm yếu (về point-in-time): `fit_transform` trên toàn corpus là mặc định trong mọi tutorial. Nếu làm vậy, c-TF-IDF và UMAP đều nhìn thấy test.
- Áp dụng: `src/features/narrative.py` (Claude). Đã fit chỉ trên train và transform phần còn lại. Có thể thay ánh xạ topic→narrative tự viết bằng `zeroshot_topic_list` để có bản đối chứng. `topics_over_time` dùng cho hình "topic prevalence" của dashboard.
- Ưu tiên: **P2** (đã có bản tương đương).

## 3. ProsusAI/finBERT — ★2.25k, cập nhật 2026-10-15, **Apache-2.0**
- Làm tốt: model `ProsusAI/finbert` (3 lớp, train trên Financial PhraseBank). `src/features/finbert.py` của mình dùng đúng model này qua `transformers`.
- Điểm yếu: train trên tin tài chính chung, không phải tin crypto. Không có kiểm định trên tiêu đề crypto.
- Áp dụng: giữ làm transformer chính (RQ1). Cần 300 nhãn tay để biết độ chính xác trên miền crypto.
- Ưu tiên: đã dùng.

## 4. ElKulako/cryptobert (Hugging Face, không phải GitHub) — 439,6k lượt tải, cập nhật 2025-05-26, **MIT**
- Làm tốt: BERTweet fine-tune trên bài đăng crypto, nhãn Bearish/Neutral/Bullish. Đây là transformer **theo miền crypto**.
- Điểm yếu: train trên bài mạng xã hội, không phải tiêu đề tin. Model card không công bố cách chia mẫu theo thời gian, nên có thể đã "thấy" giai đoạn 2023–2025.
- Áp dụng: `src/features/finbert.py` (Claude), thêm cột `cryptobert_sentiment` để RQ1 so FinBERT (tài chính chung) với CryptoBERT (miền crypto). Chỉ báo cáo trên mẫu validation; không đưa vào text_daily trước khi biết model đã train đến ngày nào.
- Ưu tiên: **P2**.

## 5. soheilrahsaz/cryptoNewsDataset — ★77, cập nhật 2026-10-08, **CC0-1.0**
- Dữ liệu 248k tin CryptoPanic, 2017-09 → 2025-12-03. Có `newsDatetime`, mã coin và phiếu người dùng (positive/negative/important…). Gói `.rar` khoảng 20 MB.
  - Đếm theo mã: BTC 31.162, ETH 21.721, SOL 12.289, XRP 9.539, BNB 3.904.
- Làm tốt: lịch sử CryptoPanic mà API miễn phí không cho (docs/SOURCES.md: CryptoPanic chỉ có gói trả phí).
- Điểm yếu:
  - README không nói múi giờ của `newsDatetime`.
  - Hết 2025-12-03, không phủ 9 tháng của test set.
  - Nội dung gốc thuộc CryptoPanic. CC0 là của người tổng hợp, không chắc bao trùm tiêu đề bên thứ ba.
- Áp dụng (Claude):
  - (a) Nguồn phụ `src/data/news_cryptopanic_ds.py` cho 2023–2025, sau khi đối chiếu múi giờ bằng các URL trùng với GDELT seendate.
  - (b) Phiếu positive/negative làm **nhãn yếu thứ hai** cho RQ1, bên cạnh 300 nhãn tay.
- Ưu tiên: **P1**.

## 6. johntwk/Diebold-Mariano-Test — ★128, cập nhật 2026-09-28, **MIT**
- Làm tốt: `dm_test.py::dm_test` có hiệu chỉnh mẫu nhỏ Harvey–Leybourne–Newbold (dòng 154: `harvey_adj`), tra phân phối t. Phương sai dài hạn dùng h−1 tự hiệp phương sai.
- Điểm yếu: vòng lặp Python thuần, chỉ 1 file, không test. Phương sai dài hạn có thể âm khi h lớn (không chặn).
- Áp dụng: đối chiếu `src/evaluation/oos.py::diebold_mariano` (Codex) với hiệu chỉnh HLN. Viết test so số với repo này.
- Ưu tiên: **P2**.

## 7. ogrnz/feval — ★8, cập nhật 2024-08-28, **MIT**
- Làm tốt: `feval/core.py::gw` (Giacomini–White, có HAC) và `cmcs` (Model Confidence Set). Có test và fixture.
- Điểm yếu: ít người dùng, không cập nhật từ 2024.
- Áp dụng (Codex):
  - Giacomini–White cho ước lượng cửa sổ trượt: nó kiểm định khả năng dự báo có điều kiện, hợp với refit theo thời gian.
  - MCS để chọn tập mô hình EN/XGB/LGBM tốt nhất mà không phải so cặp nhiều lần.
- Ưu tiên: **P3**.

## 8. alex9smith/gdelt-doc-api — ★232, cập nhật 2026-10-14, **MIT**
- Làm tốt: `gdeltdoc/filters.py` dựng truy vấn DOC 2.0 (keyword, domain, `timespan`, `sourcelang`). Trả `seendate`, không có giờ đăng.
- Điểm yếu: `api_client.py::_query` không có retry/backoff. Với mức 429 đo được (docs/SOURCES.md), client này sẽ hỏng. Cắt 250 bài/lệnh.
- Áp dụng: không dùng. Xác nhận lựa chọn GKG file tĩnh của `src/data/news_gdelt.py`.
- Ưu tiên: —.

## 9. linwoodc3/gdeltPyR — ★259, cập nhật 2026-10-02, **GPL-3.0** (chỉ học ý tưởng)
- Làm tốt: tải song song file GKG/Events 15 phút theo khoảng ngày.
- Điểm yếu: GPL. Tải toàn bộ cột rồi mới lọc, tốn RAM.
- Áp dụng: ý tưởng "lọc khi đang đọc dòng" đã có trong `news_gdelt.parse`. Không chép code.
- Ưu tiên: —.

## 10. HarsimratBhundar/Cryptocurrency-Price-Prediction-Sentiment-Analysis — ★15, cập nhật 2024-04-05, **không giấy phép** (bẫy)
- `CryptoPrediction/engine.py` có 3 lỗi:
  - `train_test_split(..., test_size=0.05, random_state=0)` xáo trộn chuỗi thời gian.
  - Nhãn `y_t = price_t > price_{t−1}` ghép với sentiment cùng ngày t, nên tin sau khi giá chạy cũng được dùng để "dự báo".
  - Chọn mô hình theo accuracy trên chính tập test.
- `news_senti.py`:
  - `sort_by='relevancy'` của NewsAPI nên mẫu tin mỗi ngày bị cắt theo độ liên quan, không theo thời gian.
  - Ngày lấy bằng `strftime` trên chuỗi `publishedAt`; không đổi về UTC trước khi cắt ngày.
  - Không dedup.
- Ưu tiên: dùng làm ví dụ "bẫy" trong paper.

## 11. CyberPunkMetalHead/cryptocurrency-news-analysis — ★215, cập nhật 2026-10-05, **không giấy phép** (bẫy)
- Một file `news-analysis.py`: lấy tin theo từ khóa, chấm điểm từ điển tổng quát, gộp thành điểm theo coin để ra quyết định.
- Điểm yếu: không có đánh giá ngoài mẫu, không dedup, không ghi giờ đăng. Bản bot (`Binance-News-Sentiment-Bot`, ★1.6k, MIT) cũng không có backtest.
- Áp dụng: không dùng. Minh họa "từ điển tổng quát + không kiểm định" cho phần mở đầu RQ1.
- Ưu tiên: —.

## 12. AI4Finance-Foundation/FinGPT — ★21.4k, cập nhật 2026-10-16, **MIT**
- Làm tốt: bộ đánh giá sentiment tài chính (FPB, FiQA, TFNS, NWGI) và LLM gán nhãn sentiment zero-shot/fine-tune.
- Điểm yếu: model fine-tune trên dữ liệu có thể chồng giai đoạn test. LLM "biết" sự kiện sau ngày tin (look-ahead của LLM).
- Áp dụng: `src/utils/llm_client.py::classify_narrative` (Claude) đã dùng prompt "chỉ dựa vào tiêu đề, không dùng hiểu biết về chuyện xảy ra sau". Chỉ dùng LLM cho đo validation (RQ1); không dùng làm feature dự báo trên test, trừ khi model có knowledge cutoff trước test.
- Ưu tiên: **P2** (quy tắc dùng LLM).

---

## Top 5 nên áp dụng ngay
| # | Thay đổi | File | Owner | Nguồn |
|---|---|---|---|---|
| 1 | Clark–West cạnh DM (market-only lồng trong market+text) + Holm/BH đã có | `src/evaluation/oos.py`, `src/models/ml.py` | Codex | #1 |
| 2 | Purge h ngày + embargo trong walk-forward; test bất biến `max(train)+h+embargo < min(test)` | `src/models/ml.py` | Codex | #1 |
| 3 | Dữ liệu CryptoPanic CC0 làm nguồn phụ 2023–2025 + nhãn yếu (phiếu người dùng) cho RQ1 | `src/data/news_cryptopanic_ds.py`, `src/features/validation.py` | Claude | #5 |
| 4 | CryptoBERT cạnh FinBERT trong bảng validation RQ1 | `src/features/finbert.py`, `src/features/validation.py` | Claude | #4 |
| 5 | Hiệu chỉnh HLN cho DM, test số với `dm_test` | `src/evaluation/oos.py` | Codex | #6 |

## Bẫy họ mắc mà mình phải tránh
1. **Xáo trộn chuỗi thời gian** khi chia train/test (#10). Mình: chia theo `split.train_end/valid_end`, walk-forward.
2. **Sentiment cùng ngày với biến động giá cùng ngày** (#10). Mình: feature ngày t chỉ dùng tin `public_ts_utc < t+1 00:00 UTC`, target `y_{t+h}` với h ≥ 1.
3. **Cắt ngày trên chuỗi giờ địa phương** (#10). Mình: mọi timestamp → UTC trước `floor("D")` (`features/daily_index.py`).
4. **Fit topic model/vectorizer trên toàn corpus** (mặc định của BERTopic, #2). Mình: fit trên train, chọn K bằng valid (`features/narrative.py`).
5. **Không dedup tin đăng lại** (#10, #11). Mình: dedup URL + tiêu đề, giữ bản công bố sớm nhất (`data/build_documents.py`).
6. **DM với mô hình lồng nhau** (#1). Mình: báo thêm Clark–West.
7. **LLM biết tương lai** (#12). Mình: LLM chỉ để đo validation; dự báo dùng FinBERT/từ điển (đóng băng, không học từ test).
