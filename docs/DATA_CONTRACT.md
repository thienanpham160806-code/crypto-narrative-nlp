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
| public_ts_utc | timestamp[UTC] | = min(published_at_utc, first_seen_utc) hợp lệ — **cột DUY NHẤT dùng để gán ngày**. published hợp lệ ⇔ có và nằm trong [first_seen − 48h, first_seen] (hoặc không có first_seen) |
| asset_tags | list[str] | BTC, ETH, … ; rỗng = tin chung thị trường |
| dup_group | str | nhóm tin trùng |
| is_canonical | bool | bản công bố sớm nhất trong dup_group |

## 2. `data/interim/doc_scores.parquet` — owner: Claude
`doc_id, lm_pos, lm_neg, lm_net, hv_net, finvn_net (chỉ vi), finbert_sentiment, positive_prob, negative_prob, neutral_prob, narrative, narrative_prob, narrative_method (lda|bertopic|zeroshot|llm)`
- Chỉ tin canonical. `narrative` ∈ 8 narrative của config hoặc `other`; mặc định `zeroshot` (embedding đa ngữ), `llm` khi bật.
- So sánh phương pháp ở `data/interim/narratives.parquet`: `doc_id, period (train|valid|test), zs_narr, zs_prob, lda_topic, lda_prob, lda_narr, bt_topic, bt_prob, bt_narr` (LDA/BERTopic chỉ tin en; fit chỉ trên train).

## 3. `data/processed/text_daily.parquet` — owner: Claude
`date, asset ('ALL' hoặc mã), n_docs, sent_finbert, sent_lm, sent_hv, pos_sent, neg_sent, attention_<narrative>… (8 cột), neg_accel`
- Quy tắc cắt: tin vào ngày `t` ⇔ `public_ts_utc ∈ [t, t+1)`. Chỉ `is_canonical = True`.
- `pos_sent = mean(max(sent,0))`, `neg_sent = mean(max(-sent,0))`; `attention_k = N_k,t / N_t`.
- Chỉ tin `lang = en` (nhánh chính), không gồm `sec` (văn bản pháp lý dài; SEC dùng cho event study); w_d = 1. `date` = datetime UTC 00:00 (cùng kiểu market_daily).
- `ALL`: đủ mọi ngày của mẫu (ngày không tin: `n_docs = 0`, còn lại NaN). Từng mã: chỉ ngày có tin gắn mã.
- `neg_accel_t = neg_sent_t − neg_sent_{t−1}` (ngày lịch liền trước; trống → NaN).

## 4. `data/processed/market_daily.parquet` — owner: Codex
`date, asset, close, ret (log), rv (tổng bình phương log-return giờ), volume_usd, logvol, ret_lag1..7`

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
