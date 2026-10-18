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

## 3. `data/processed/text_daily.parquet` — owner: Claude
`date, asset ('ALL' hoặc mã), n_docs, sent_finbert, sent_lm, sent_hv, pos_sent, neg_sent, attention_<narrative>… (8 cột), neg_accel`
- Quy tắc cắt: tin vào ngày `t` ⇔ `public_ts_utc ∈ [t, t+1)`. Chỉ `is_canonical = True`.
- `pos_sent = mean(max(sent,0))`, `neg_sent = mean(max(-sent,0))`; `attention_k = N_k,t / N_t`.

## 4. `data/processed/market_daily.parquet` — owner: Codex
`date, asset, close, ret (log), rv (tổng bình phương log-return giờ), volume_usd, logvol, ret_lag1..7`

## 5. Ghép & mục tiêu (owner: Codex)
`panel = text_daily(t) ⨝ market_daily(t)`; target `y_{t+h}` lấy từ market_daily dịch **−h**. Feature ngày t không bao giờ chứa thông tin sau `t+1 00:00 UTC`.

Trước khi có dữ liệu thật, Codex dùng `tests/fixtures/make_fixtures.py` sinh `text_daily` giả đúng schema.
