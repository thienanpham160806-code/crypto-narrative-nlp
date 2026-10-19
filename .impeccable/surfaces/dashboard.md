---
version: 1
slug: "dashboard"
primary_target: "dashboard"
related_targets: []
---

# Surface brief: dashboard (Crypto Narrative Intelligence)

Scope: toàn bộ dashboard/ (web Vite React + export JSON + FastAPI local). Mode: Operate.
Audience: giảng viên Fintech chấm đề tài; đọc số liệu, kiểm chứng point-in-time. Job: nắm trạng thái narrative/sentiment, so với giá, kiểm tra độ tin cậy (timing, validation, ngoài mẫu).
Constraints: song ngữ VI/EN (thuật ngữ chỉ số giữ tiếng Anh); sáng/tối; Vercel tĩnh + local; Live tách khỏi nghiên cứu; mọi trục thời gian UTC; mỗi exhibit có bảng thay thế.
Memorable moment: mỗi biểu đồ là một exhibit đánh số có câu nhận định, và vùng valid/test được tô như "kỳ dự phóng" của báo cáo ngân hàng trung ương.
Unresolved: chính sách feed cho tab Live công khai (chỉ feed cho phép hay chỉ điểm tổng hợp).

## Direction contract
THESIS: Dashboard đọc như một Monetary Policy Report: mỗi biểu đồ là exhibit đánh số kèm một câu nhận định và nguồn. Từ chối lưới thẻ KPI + biểu đồ không lời giải thích của dashboard crypto thông thường.
OWN-WORLD: Nền trắng giấy báo cáo, thanh trên navy #0B2545, mực navy #13315C, mist #8DA9C4, đường kẻ #D6DEE7; đỏ #C0392B chỉ cho rủi ro/tin xấu. Exhibit có gạch trên navy 3px, tiêu đề serif (Source Serif 4) với số "Exhibit 1.2", chữ UI Source Sans 3, chú thích nguồn nhỏ dưới hình. Fan chart cho bất định dự báo. Dark: navy đêm #0F1B2D, mực #E6EDF5.
STORY: Người xem đọc cột "Nhận định chính" (5 chỉ số tóm tắt bằng câu), lướt 4 exhibit, rồi đi sâu theo mục lục (Narratives, Sentiment, Coins, Forecast, Timing, Validation, Live) để kiểm chứng.
FIRST VIEWPORT: Thanh trên navy: tên báo cáo, mục lục exhibit dạng tab, chuyển VI/EN, sáng/tối, chip độ phủ dữ liệu. Dưới: hàng lọc thời gian (30/90/365/toàn mẫu). Cột trái 320px "Nhận định chính" + 4 chỉ số. Phải: lưới 2×2 exhibit (attention theo narrative, sentiment vs BTC, fan chart RV BTC, độ lệch giờ đăng). Signature move: dải tô kỳ valid/test trên mọi trục thời gian, như vùng projection; mỗi exhibit có công tắc Hình/Bảng.
FORM: Monetary Policy Report — vị trí 1 trong danh sách của tôi (IMPECCABLE'S PICK, người dùng chọn). seed:0c55260ddea454fb
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
