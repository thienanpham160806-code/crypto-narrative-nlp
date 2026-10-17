# Data contract (Claude ↔ Codex làm song song dựa trên file này)

Mọi timestamp là **UTC**. Ngày `t` = [t 00:00, t+1 00:00) UTC. File đổi schema → sửa file này TRƯỚC, ghi vào `docs/PROGRESS.md`.

## 1. `data/interim/documents.parquet` — owner: Claude
| cột | kiểu | ghi chú |
|---|---|---|
| doc_id | str | sha1(source + url) |
| source | str | gdelt / rss:<tên> / sec / vn:gdelt / vn:<tên> |
| url | str | |
| lang | str | `en` (nhánh chính) / `vi` (nhánh phụ) |
| title | str | |
| body | str \| null | có thì dùng, không có thì chỉ title |
| published_at_utc | timestamp[UTC] | **thời điểm ra công chúng** do nguồn công bố |
| first_seen_utc | timestamp[UTC] | lần đầu pipeline/GDELT thấy tin |
| ts_source | str | api / rss_pubdate / html_meta / gdelt_seendate / crawl |
| public_ts_utc | timestamp[UTC] | = min(published_at_utc, first_seen_utc) hợp lệ — **cột DUY NHẤT dùng để gán ngày**. published hợp lệ ⇔ có, nằm trong [first_seen − 48h, first_seen] **và cùng ngày UTC với first_seen** (hoặc không có first_seen). Chữ là bản thấy lúc first_seen, có thể đã sửa sau giờ đăng → không lùi qua nửa đêm. `published_at_utc` giữ nguyên cho event study trong ngày |
| asset_tags | list[str] | BTC, ETH, … ; rỗng = tin chung thị trường |
| dup_group | str | nhóm tin trùng |
| is_canonical | bool | bản công bố sớm nhất trong dup_group |

## 2. `data/interim/doc_scores.parquet` — owner: Claude
`doc_id, lm_pos, lm_neg, lm_net, hv_net, finvn_net (chỉ vi), finbert_sentiment, positive_prob, negative_prob, neutral_prob, narrative, narrative_prob, narrative_method (lda|bertopic|zeroshot|llm), nprob_<narrative>… (8 cột)`
- `nprob_k`: xác suất zero-shot (softmax trên 8 narrative, tổng = 1), luôn từ zero-shot kể cả khi `narrative_method = llm`.
- Chỉ tin canonical. `narrative` ∈ 8 narrative của config hoặc `other`; mặc định `zeroshot` (embedding đa ngữ), `llm` khi bật.
- So sánh phương pháp ở `data/interim/narratives.parquet`: `doc_id, period (train|valid|test), zs_narr, zs_prob, lda_topic, lda_prob, lda_narr, bt_topic, bt_prob, bt_narr` (LDA/BERTopic chỉ tin en; fit chỉ trên train).

## 3. `data/processed/text_daily.parquet` — owner: Claude
`date, asset ('ALL' hoặc mã), n_docs, sent_finbert, sent_lm, sent_hv, pos_sent, neg_sent, attention_<narrative>… (8 cột), neg_accel, disagreement_af, disagreement_std, soft_attention_<narrative>… (8 cột)`
- Quy tắc cắt: tin vào ngày `t` ⇔ `public_ts_utc ∈ [t, t+1)`. Chỉ `is_canonical = True`.
- `pos_sent = mean(max(sent,0))`, `neg_sent = mean(max(-sent,0))`; `attention_k = N_k,t / N_t`.
- Chỉ tin `lang = en` (nhánh chính), không gồm `sec` (văn bản pháp lý dài; SEC dùng cho event study); w_d = 1. `date` = datetime UTC 00:00 (cùng kiểu market_daily).
- `ALL`: đủ mọi ngày của mẫu (ngày không tin: `n_docs = 0`, còn lại NaN). Từng mã: chỉ ngày có tin gắn mã.
- `neg_accel_t = neg_sent_t − neg_sent_{t−1}` (ngày lịch liền trước; trống → NaN).
- `disagreement_af_t = √(1 − A_t²)`, `A_t = (N⁺ − N⁻)/(N⁺ + N⁻)` theo nhãn FinBERT (lớp xác suất lớn nhất) – Antweiler & Frank (2004); 0 = đồng thuận, 1 = chia đôi; N⁺ + N⁻ = 0 → NaN.
- `disagreement_std_t` = độ lệch chuẩn (ddof=1) sentiment FinBERT các tin trong ngày (độ phân tán kiểu Khaksar et al., 2026); < 2 tin → NaN.
- Mọi tin canonical của `text_daily` phải có `doc_scores` (merge one_to_one; thiếu → build báo lỗi).
- `soft_attention_k,t = mean_d nprob_k` (attention mềm, không ép nhãn cứng; tổng 8 cột = 1). `attention_k` (cứng) giữ nguyên.

## 4. `data/processed/market_daily.parquet` — owner: Codex
`date, asset, close, ret (log), rv (tổng bình phương log-return giờ), volume_usd, logvol, ret_lag1..7`

## 6. `data/processed/ucry_daily.parquet` — owner: Claude (`src/data/news_ucry.py`)
`date, ucry_policy, ucry_price, week_end`
- UCRY Policy/Price (Lucey et al. 2022), chỉ số tuần (thứ Hai–Chủ nhật) từ tin LexisNexis; nguồn hiện có đến tuần kết thúc 2024-12-29.
- Point-in-time: giá trị tuần kết thúc `week_end` chỉ dùng từ `week_end + 1 ngày`; ngày t lấy tuần gần nhất đã công bố, tối đa 7 ngày; sau đó NaN (không kéo dài).
- Biến kiểm soát cho RQ3/RQ5 (bất định chung). Chỉ phủ train + đầu valid → mô hình có UCRY chạy riêng trên đoạn có dữ liệu. Chuỗi hồi cứu, không có vintage.

## 5. Ghép & mục tiêu (owner: Codex)
`panel = text_daily(t) ⨝ market_daily(t)`; target `y_{t+h}` lấy từ market_daily dịch **−h**. Feature ngày t không bao giờ chứa thông tin sau `t+1 00:00 UTC`.

Trước khi có dữ liệu thật, Codex dùng `tests/fixtures/make_fixtures.py` sinh `text_daily` giả đúng schema.

## 6. X4 và event study — owner: Codex
- Bảng fixture ở `outputs/tables/synthetic/`; bảng nghiên cứu thật ở `outputs/tables/real/`. `market_coverage.csv` là audit giá thật, giữ ở thư mục cha.
- X4 chỉ dùng ngày feature và target không sau `split.valid_end`. Horizon là outcome một ngày tại t+h, không phải tổng h ngày.
- `--source-weighted-text` và `--exclude-price-text` nhận parquet cùng schema `text_daily`, được upstream tổng hợp lại từ bài canonical theo `public_ts_utc`. Không thể suy ra trọng số hoặc sentiment sau khi bỏ narrative từ daily means.
- Event input: `doc_id, asset, public_ts_utc` (UTC có timezone), mỗi hàng là một bài–asset. Prices: `date, asset, close`; `date` là thời điểm bắt đầu bar UTC, lịch liên tục theo `--frequency` (mặc định `1h`).
- T0 là bar bắt đầu đầu tiên **sau** `public_ts_utc`; lợi suất đơn từ close bar đó đến close bar kế tiếp. Các cửa sổ config đo bằng số bar; thiếu bar giữ NaN, không nối qua khoảng trống. Asset trùng benchmark bị bỏ vì không có lợi suất tương đối độc lập.
- Holm/BH dùng một bảng export làm một family; p-value thiếu không được kiểm định. ADF có H0 unit root; KPSS có H0 level stationarity.
