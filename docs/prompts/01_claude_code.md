# Prompt phiên Claude Code (dán vào `../cnn-claude`)

```text
/caveman full
/ponytail full

Repo: crypto-narrative-nlp (Blueprint 10 – Crypto Narrative & NLP Sentiment). Bạn là owner phần TEXT + NLP + DASHBOARD + PAPER.
Codex đang chạy SONG SONG ở worktree khác, owner phần MARKET DATA + ECONOMETRICS + ML. Không sửa thư mục của Codex.

Đầu phiên:
1. Tra claude-mem xem các phiên trước đã làm gì; đọc CLAUDE.md, AGENTS.md, docs/PLAN.md, docs/DATA_CONTRACT.md, docs/PORTED.md, docs/PROGRESS.md, docs/blueprint.md.
2. Không hỏi lại tôi những gì đã có trong các file trên hoặc trong claude-mem. Không tường thuật từng bước.

Việc giai đoạn C1 → C2 (theo docs/PLAN.md), làm tuần tự, mỗi mục xong mới sang mục sau:

C1 – Thu thập text → data/interim/documents.parquet (đúng DATA_CONTRACT §1)
- src/data/news_gdelt.py: GDELT DOC 2.0 API, query BTC/ETH/crypto/stablecoin/ETF…, chia cửa sổ thời gian nhỏ để vượt giới hạn 250 bài/lượt, cache JSON thô ở data/raw/.
- src/data/news_rss.py: RSS các trang crypto tiếng Anh (CoinDesk, Cointelegraph, The Block, Decrypt…) — chỉ lưu tiêu đề + tóm tắt + link + pubDate (không lưu toàn văn).
- src/data/news_sec.py: văn bản SEC liên quan ETF crypto (19b-4, S-1, order phê duyệt) lấy bản .txt/.htm từ EDGAR — có text thì lấy text, không OCR.
- src/data/vn_news.py (nhánh phụ, lang=vi): tin tiền mã hóa tiếng Việt; ý tưởng từ disclosure-tone-car/src/vn/v05_news.py (giờ đăng giờ VN → to_utc(..., "Asia/Ho_Chi_Minh")). Báo VN có bản tiếng Anh thì ưu tiên bản Anh.
- src/data/build_documents.py: hợp nhất, chuẩn hóa UTC, public_ts_utc = min(published, first_seen hợp lệ), dedup bằng rapidfuzz (giữ bản sớm nhất), asset tagging bằng regex ticker/tên coin.
- Xuất outputs/tables/corpus_stats.csv và outputs/tables/timestamp_accuracy.csv (theo nguồn: % có giờ, trung vị |published − first_seen|, % lệch > 1h). Đây là điểm thầy nhấn mạnh: đúng ngày ra công chúng mới đánh giá được độ chính xác.

C2 – NLP → doc_scores.parquet + text_daily.parquet (DATA_CONTRACT §2–3)
- Tái dùng src/features/lexicon/* (LM, Harvard, VietScorer) và src/features/finbert.py — đã port, đừng viết lại.
- Tạo dict/crypto_vn.csv (word,category) mở rộng fin_vn.csv cho crypto; dictionaries.load_fin_vn() đọc cả hai file.
- Narrative: LDA (benchmark) → BERTopic → zero-shot 8 narrative trong config.nlp.narratives; fit chỉ trên train (≤ split.train_end), transform cho valid/test.
- Port xong src/utils/llm_client.py: bỏ phần OCR, thêm classify_narrative() (JSON schema, temperature 0, cache) — chỉ bật khi config.nlp.llm.enabled.
- Validation: sinh data/interim/validation_sample.csv 300 tiêu đề ngẫu nhiên (seed) để tôi gán nhãn tay; viết script đo accuracy/F1 cho LM vs Harvard vs FinBERT vs zero-shot (RQ1).
- src/features/daily_index.py: build text_daily theo đúng quy tắc cắt ngày.

Quy tắc:
- Test cho mọi module (pytest -q chạy không cần mạng; mock HTTP). Commit nhỏ, message tiếng Anh, theo từng mục.
- Cuối C1 và cuối C2: chạy `/codex:review --base main --background`, sau đó `/codex:result`; sửa lỗi hợp lệ, ghi lỗi bác bỏ + lý do vào docs/PROGRESS.md.
- Trước khi báo xong C2: chạy `/codex:adversarial-review --background` với trọng tâm "look-ahead bias / text leakage / timezone / dedup giữ bản muộn".
- Cuối phiên: append 1 dòng vào docs/PROGRESS.md, push nhánh claude/phase1, mở PR vào main.

Chỉ báo lại tôi: (a) file đã tạo/sửa, (b) số liệu corpus, (c) việc cần tôi làm tay (gán nhãn 300 tiêu đề, API key).
```

## Prompt giai đoạn C3 – Dashboard (phiên sau)
```text
/caveman full
Tra claude-mem + docs/PROGRESS.md rồi làm C3. Dùng impeccable: chạy lệnh dựng design context (teach/init của impeccable) với bối cảnh "dashboard nghiên cứu tài chính, người xem là giảng viên Fintech, ưu tiên đọc số liệu, dark/light", rồi dựng dashboard/ (FastAPI đọc outputs/ + data/processed, frontend Vite React).
Màn hình: thẻ tóm tắt (Dominant narrative, Narrative intensity, Overall sentiment, Negative-news acceleration, BTC volatility risk – như mục 4.2 blueprint), narrative trends, sentiment vs BTC, attention theo coin, snippet đại diện có link + public_ts_utc, predicted volatility (đọc từ outputs của Codex), trang "Timing accuracy".
Xong thì chạy /audit rồi /polish của impeccable, sửa đến khi sạch. Sau đó /codex:review --base main --background.
```

## Prompt giai đoạn C4 – Paper
```text
/caveman lite
Tra claude-mem + PROGRESS. Viết paper/ (Markdown → có thể xuất docx): Giới thiệu, Dữ liệu (corpus stats, timestamp accuracy), Phương pháp, Kết quả RQ1–RQ5 (đọc outputs/tables, outputs/figures của cả hai agent), Robustness, Hạn chế, Kết luận kinh tế. Mỗi bảng có 1–2 câu "nghĩa là gì". Trích dẫn đúng 7 tài liệu ở mục 5 blueprint. Đối chiếu checklist mục 6, đánh dấu cái nào còn thiếu.
```
