# AGENTS.md — luật chung cho mọi agent (Codex đọc file này; Claude đọc qua CLAUDE.md)

Dự án: Blueprint 10 — Crypto Narrative & NLP Sentiment Intelligence (`docs/blueprint.md`).
Phân công: `docs/PLAN.md`. Schema: `docs/DATA_CONTRACT.md`. Đã tái dùng gì: `docs/PORTED.md`.

## Bắt buộc
1. **Point-in-time.** Gán ngày bằng `public_ts_utc`. Feature ngày t chỉ dùng thông tin < t+1 00:00 UTC. Test set (sau `split.valid_end`) không được chạm khi tuning, chọn topic số K, chọn ngưỡng, hay fit vectorizer/BERTopic.
2. **Tiếng Anh là nhánh chính** (LM, Harvard IV-4, FinBERT). Tiếng Việt chấm bằng `dict/fin_vn.csv` + `dict/crypto_vn.csv` qua `VietScorer`. **Không dịch** Việt↔Anh để chấm.
3. **Có text thì lấy text**, không OCR khi nguồn đã có text.
4. Code sạch, tối thiểu: không thêm abstraction không dùng, không file "utils2", hàm ngắn, không comment thừa. Ưu tiên tái dùng module đã port trước khi viết mới.
5. Chỉ sửa thư mục mình sở hữu (PLAN.md). Đổi schema → sửa DATA_CONTRACT.md trước.
6. Mỗi thay đổi có test (`pytest -q` không cần mạng; mạng thì mock/fixture). Seed = `config.seed`.
7. Không commit `.env`, `config.local.yaml`, `data/raw`, parquet lớn, từ điển LM tải ngoài.
8. Cuối mỗi phiên: append 1 dòng vào `docs/PROGRESS.md`.
9. Kết luận kinh tế, không chỉ metric: mỗi bảng kèm 1–2 câu "nghĩa là gì".

## Làm chung 1 folder
Claude và Codex cùng làm trong `crypto-narrative-nlp/`, cùng nhánh `dev` (không worktree, không nhánh riêng).
- Chỉ `git add <đường dẫn của mình>` (vùng sở hữu ở `docs/PLAN.md`).
- Cấm: `git add -A`/`git add .`, `git stash`, `git checkout .`/`git restore .`, `git reset --hard`, đổi nhánh, chạy formatter toàn repo.
- `git pull --rebase` trước mỗi push.
- `docs/PROGRESS.md`: chỉ append, commit + push ngay sau khi append.
- `/codex:review` dùng `--base main`.
- Cuối mỗi giai đoạn: merge `dev` → `main` qua PR.

## Lệnh
```bash
pip install -r requirements.txt
pytest -q
python -m src.data.<module>         # chạy từ gốc repo, PYTHONPATH=src
```
