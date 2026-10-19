# Đăng ký trước phân tích event theo giờ

Ngày chốt: 2026-10-20. Tài liệu này được commit trước khi chạy lại hoặc xem kết quả event theo quy tắc nến đã sửa. Đơn vị quan sát là tin canonical tiếng Anh gắn với tài sản; T0 là nến Binance 1 giờ đầu tiên bắt đầu sau `public_ts_utc`.

## Endpoint và họ kiểm định

Hai endpoint chính là CAR và abnormal volume trong 4 nến `[0,3]` sau T0. Họ kiểm định chính gồm đúng 9 kiểm định hai phía: CAR, abnormal absolute return (`|ret|`) và abnormal volume, mỗi biến ở 1 giờ `[0,0]`, 4 giờ `[0,3]` và 24 giờ `[0,23]`. Báo p thô và p Holm trong họ 9 kiểm định; mức ý nghĩa 0,05. Không chọn endpoint hoặc cửa sổ theo kết quả.

CAR cộng log return của đúng các nến trong cửa sổ; return ở nến i là `log(C[i]/C[i−1])`. Biến `|ret|` và volume căn cùng nến với CAR. Cửa sổ trước tin là `[-4,-1]`. Placebo dời 24 giờ phải loại mọi cửa sổ chồng T0 thật.

Suy luận chính gom event thành trung bình theo ngày UTC, giữ nguyên khoảng trống ngày không có tin, rồi ước lượng sai số chuẩn HAC Bartlett 7 lag theo ngày lịch. Kiểm tra độ nhạy bằng bootstrap block 7 ngày, 1.999 lần lặp, seed 42. Báo MDE xấp xỉ `2,802 × SE` cho từng endpoint và cửa sổ. Các nhóm FinBERT, LM, narrative, trước tin, placebo và so sánh T0 công bố với GDELT seendate là phân tích phụ. Tương phản tin tốt trừ tin xấu mang tính khám phá; báo p Holm trên toàn bộ họ khám phá liên quan, ngoài p thô.

Robustness nguồn text tách tin chung thị trường và tin riêng từng coin, kèm cờ thiếu text và tỷ lệ fallback theo coin. Phân tích này không thay thế đặc tả chính. Chỉ diễn giải kết quả thật cùng coverage, cỡ mẫu, và giới hạn của timestamp.
