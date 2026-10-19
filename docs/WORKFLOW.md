# Quy trình phát triển

Dự án được phát triển bởi hai agent (Claude Code và Codex) chạy song song trong cùng một thư mục, trên nhánh `dev`; `main` chỉ nhận thay đổi qua pull request.

## Bắt đầu
Xem [`docs/prompts/START.md`](prompts/START.md) (clone repo → chạy hai prompt khởi tạo). Prompt từng phiên ở [`docs/prompts/`](prompts).

## Tài liệu điều phối
| Tài liệu | Vai trò |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | Luật chung cho mọi agent (point-in-time, ngôn ngữ, test, git) |
| [`docs/PLAN.md`](PLAN.md) | Phân công và thư mục mỗi agent sở hữu |
| [`docs/DATA_CONTRACT.md`](DATA_CONTRACT.md) | Schema các file trao đổi; giao thức `REBUILD_DONE.json` / `RUN_DONE.json` (§7) |
| [`docs/PROGRESS.md`](PROGRESS.md) | Nhật ký, mỗi phiên append một dòng |
| [`docs/PAPER_STYLE.md`](PAPER_STYLE.md) | Khuôn trình bày bài nghiên cứu |
| [`docs/LABELING_GUIDE.md`](LABELING_GUIDE.md) | Hướng dẫn gán nhãn 300 tiêu đề kiểm định |

## Quy tắc git khi làm chung một thư mục
- Chỉ `git add <đường dẫn của mình>`; không `git add -A`, `git stash`, `git checkout .`, `git reset --hard`, không đổi nhánh, không chạy formatter toàn repo.
- `git pull --rebase` trước mỗi lần push; `docs/PROGRESS.md` chỉ append rồi commit + push ngay.
- Cuối mỗi giai đoạn: review chéo (`/codex:review --base main`), sửa lỗi hợp lệ, ghi lỗi bác bỏ kèm lý do vào PROGRESS, rồi merge `dev` → `main` qua PR.
- CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) chạy `pytest -q` offline trên Python 3.10–3.12 cho mọi push/PR vào `main` và `dev`.

## Bắt tay giữa hai pipeline
1. Bộ canh `src/data/rebuild_watch.py` (Claude) chờ GKG thu đủ ngày, dựng lại `documents → narratives → doc_scores → text_daily`, rồi ghi `data/processed/REBUILD_DONE.json` kèm SHA-256.
2. `python -m src.models.run_real --watch` (Codex) nhận cờ khi hash khớp, chạy phân tích thật và ghi `outputs/tables/real/RUN_DONE.json`.
3. Khi `RUN_DONE.json` có `status: ok`, bộ canh điền lại bài nghiên cứu (`paper/build_docx.py`) và xuất dashboard.
4. Dashboard deploy tự động trên Vercel: push `dev` tạo bản Preview, merge vào `main` lên Production.
