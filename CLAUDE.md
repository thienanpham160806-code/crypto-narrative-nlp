@AGENTS.md

## Riêng Claude Code
- Đầu phiên: tra claude-mem (phiên trước làm gì) + đọc `docs/PROGRESS.md`, không hỏi lại người dùng điều đã có.
- Giao tiếp ngắn (caveman). Code tối giản (ponytail). UI dashboard dùng impeccable.
- Không tường thuật từng bước; báo kết quả + file đã đổi + việc tiếp.
- Cuối mỗi giai đoạn: `/codex:review --base main --background`, đọc kết quả bằng `/codex:result`, sửa các lỗi hợp lệ, ghi lỗi bác bỏ + lý do vào PROGRESS.
