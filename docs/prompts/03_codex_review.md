# Prompt Codex review công việc của Claude

## Cách 1 – từ trong Claude Code (plugin codex-plugin-cc)
```text
/codex:review --base main --background
```
```text
/codex:adversarial-review --background Soi nhánh này như giảng viên chấm đồ án tài chính định lượng. Ưu tiên: (1) look-ahead bias: feature ngày t có dùng tin public_ts_utc ≥ t+1 không, BERTopic/vectorizer/ngưỡng có fit trên test không; (2) timezone: tin VN có quy về UTC đúng không; (3) dedup có giữ bản công bố SỚM nhất không; (4) dịch Việt↔Anh để chấm (cấm); (5) code thừa, abstraction không dùng; (6) test có thật sự kiểm tra hay chỉ chạy qua. Trả danh sách lỗi theo mức nghiêm trọng, kèm file:dòng và cách sửa.
```
Đọc kết quả: `/codex:status` → `/codex:result`.

## Cách 2 – phiên Codex riêng, review PR của Claude
```text
$caveman full
Review PR từ dev vào main (git diff main...dev). Đọc AGENTS.md + docs/DATA_CONTRACT.md trước.
Chỉ REVIEW, không sửa code. Kiểm tra: point-in-time & leakage, đúng schema contract, timestamp/UTC, dedup, nhánh tiếng Việt dùng từ điển Việt (không dịch), test pass (pytest -q), code tối giản.
Ghi kết quả vào docs/reviews/<yyyy-mm-dd>_claude_phaseN.md: Blocker / Should-fix / Nit, mỗi mục có file:dòng + đề xuất. Cuối file: "Merge được không: Có/Không".
```
Sau đó trong Claude Code: `Đọc docs/reviews/<file mới nhất>, sửa Blocker + Should-fix, ghi lỗi bác bỏ + lý do vào PROGRESS.`
