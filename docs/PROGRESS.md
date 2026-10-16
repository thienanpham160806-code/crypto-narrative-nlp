# Nhật ký tiến độ (cả hai agent append, mới nhất ở dưới)

Định dạng: `YYYY-MM-DD HH:MM | agent | giai đoạn | việc đã xong | việc tiếp | chặn/quyết định`

2026-10-16 | setup | 0 | Khung repo theo blueprint 10, port lexicon/FinBERT/http/llm_client/event_study từ disclosure-tone-car, 5 test pass | Claude: C1, Codex: X1 | —
2026-10-16 14:31 | claude | 4 (paper) | paper/related_work.md + references.bib: 7 bài mục 5 blueprint, bảng so sánh, 6 khoảng trống gắn RQ1–5 | điền ô [không tìm được] khi có full text (Chou, Walker, Kao, Gür, Khaksar) | 5/7 bài chỉ đọc abstract; nhánh claude/related-work
2026-10-16 14:48 | claude | 4 (paper) | related_work: Walker đọc bản in, Khaksar qua luận văn Brock 2023, tên tác giả xác minh Crossref; +13 bài OA theo RQ (docs/research/PAPERS.md), bib 21 mục | tải tay PDF Gür (OA, captcha), Khaksar bản in, Chou, Kao vào paper/sources/ | docs/prompts/04_research.md không có trong repo, tiêu chí R2 tự đặt
2026-10-16 14:37 | claude | 0 | setup xong: plugin caveman/codex/claude-mem + skill ponytail/impeccable (Claude), caveman/ponytail/claude-mem (Codex), worktree cnn-claude (claude/phase1) + cnn-codex (codex/phase1), venv dùng chung crypto-narrative-nlp/.venv (torch CPU), pytest pass | Claude: C1 → C2 | Windows cần VC++ redist mới (vcruntime140_threads.dll) để import torch
2026-10-16 | claude | 0 | Thử thật nguồn tin, ghi docs/SOURCES.md: GDELT DOC (tiêu đề) là nguồn chính, EDGAR FTS phụ, loại CryptoPanic (trả phí), RSS chỉ live | Thu GDELT có backoff+cache; thử lại domain: | GDELT 429 nặng; volume GDELT đứt gãy quanh 2025-01; ToS CoinDesk/CT/Decrypt cấm scraping
2026-10-16 | claude | 1 | Merge claude/related-work → claude/phase1 (SOURCES.md, paper/, docs/research). Xung đột PROGRESS.md: giữ cả hai phía theo giờ | C1 | —
2026-10-16 | claude | 1 | C1 dở: news_gdelt (GKG raw thay DOC API vì 429 ≈1 lệnh/4 phút; lấy lô :00 mỗi giờ ≈25% bài), news_rss, news_sec, build_documents + 15 test pass; config.text.sources = [gdelt, rss, sec]; thử 2024-03-01: 182 tiêu đề EN | chạy bộ thu GKG cả mẫu (~12 giờ), audit html_meta, build | SEC cần env CONTACT_EMAIL; dừng để gộp về 1 folder (dev)
