# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Do người dùng chọn (đề bài C3, `docs/prompts/01_claude_code.md`): backend FastAPI (Python) đọc `outputs/` và `data/processed/`; frontend Vite + React trong `dashboard/`.
Triển khai: Vercel (bản công khai, chỉ đọc) + chạy local (uvicorn + Vite). Người dùng xác nhận 2026-10-16.

## Users
- Chính: giảng viên Fintech chấm đề tài nghiên cứu. Họ đọc số liệu, kiểm tra kết quả có đứng vững không (rò rỉ thông tin, độ chính xác timestamp, kiểm định ngoài mẫu). Họ mở link Vercel tự xem, hoặc xem chiếu trong buổi bảo vệ.
- Phụ: nhóm sinh viên làm đề tài, dùng bản local để trình bày và kiểm tra pipeline.

## Product Purpose
"Crypto Narrative Intelligence": cho thấy narrative/sentiment trích từ tin tức (GDELT, SEC; nhánh phụ tin tiếng Việt) có giải thích và dự báo được return, volatility, volume của crypto (BTC, ETH, SOL, BNB, XRP) hay không. Mẫu 2023-01 → 2026-09.
Thành công = người xem đọc được trạng thái narrative hiện tại, xem chỉ số so với giá, và tự kiểm chứng được độ tin cậy của dữ liệu (timestamp, dedup, validation).

## Positioning
Mọi con số đều point-in-time: tin được gán ngày bằng `public_ts_utc` (thời điểm ra công chúng). Có trang "Timing accuracy" công khai sai lệch giờ đăng theo nguồn. Topic model chỉ fit trên train. Kết quả dự báo so market-only với market+text bằng kiểm định thống kê, không chỉ bằng metric.

## Operating Context
- Mở trên laptop hoặc máy chiếu phòng bảo vệ. Giảng viên đọc nhanh thẻ tóm tắt rồi đi sâu vào biểu đồ và bảng.
- Dữ liệu nghiên cứu là bản chụp đóng băng của pipeline (`outputs/tables/*.csv`, `data/processed/*.parquet`). Python xuất ra JSON tĩnh để Vercel phục vụ.
- Tab "Live" tách riêng khỏi kết quả nghiên cứu: tin RSS mới nhất, chấm FinBERT + narrative. Tab này không bao giờ trộn vào chỉ số nghiên cứu.

## Capabilities and Constraints
- Màn hình (blueprint 4.2 + đề C3):
  - Thẻ tóm tắt: Dominant narrative, Narrative intensity, Overall sentiment, Negative-news acceleration, BTC volatility risk.
  - Biểu đồ: narrative trends; sentiment vs BTC; attention theo coin.
  - Tin đại diện: snippet có link và `public_ts_utc`.
  - Predicted volatility: đọc từ output của Codex.
  - Trang "Timing accuracy".
  - Tab Live.
- Song ngữ Việt/Anh, có nút chuyển. Thuật ngữ chỉ số giữ tiếng Anh ở cả hai ngôn ngữ (sentiment, attention, narrative, disagreement).
- Sáng/tối (dark/light).
- Vercel chỉ phục vụ file tĩnh/serverless nhẹ. FinBERT không chạy trên Vercel. Dữ liệu Live trên bản Vercel là bản chụp được làm mới định kỳ ngoài Vercel; bản local chấm trực tiếp.
- Bản công khai hiển thị tiêu đề + link tới nguồn, không hiển thị toàn văn. CoinDesk, Cointelegraph, Decrypt cấm scraping (`docs/SOURCES.md`). Vì vậy tab Live công khai chỉ dùng feed cho phép, hoặc chỉ hiện điểm tổng hợp. Quyết định cụ thể ghi lúc làm tab Live.
- Mẫu GDELT là lô :00 mỗi giờ (≈25% bài). Kỳ test = sau 2025-12-31. Tới khi GKG thu xong, dashboard chạy trên phần đã thu và phải ghi rõ độ phủ.

## Evidence on Hand
- `outputs/tables/`: corpus_stats, timestamp_accuracy, narrative_taxonomy, narrative_topics, lda_k_selection; bảng của Codex: regressions, wald, granger, oos, forecasts, shap, strategy, market_coverage.
- `data/processed/`: text_daily, market_daily, ucry_daily. `data/interim/`: documents, doc_scores, narratives.
- Không có testimonial, logo đối tác hay số liệu marketing. Không bịa thêm.

## Product Principles
1. Số liệu trước, trang trí sau. Mỗi biểu đồ hoặc bảng kèm 1–2 câu "nghĩa là gì".
2. Minh bạch về độ tin cậy: hiện độ phủ dữ liệu, n, khoảng thời gian, và train/valid/test ngay cạnh kết quả.
3. Không đánh lừa bằng thời gian: mọi trục thời gian theo UTC. Kết quả ngoài mẫu tách rõ khỏi trong mẫu.
4. Live là demo sản phẩm, không phải bằng chứng nghiên cứu. Luôn tách khỏi kết quả nghiên cứu.

## Accessibility & Inclusion
Đọc được trên máy chiếu: tương phản cao, chữ số rõ, không dùng màu làm kênh mã hóa duy nhất. Biểu đồ có nhãn trực tiếp hoặc bảng thay thế.
