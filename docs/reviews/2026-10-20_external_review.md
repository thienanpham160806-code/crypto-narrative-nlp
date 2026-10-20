# Tổng hợp phản biện ngoài ngày 2026-10-20

Phạm vi: phân tích sự kiện theo giờ, suy luận thống kê, đặc tả text và khả năng tái lập kết quả thật. Đây là tóm tắt yêu cầu phản biện; không phải một bộ kết quả mới. Đặc tả được khóa trước khi chạy lại trong `docs/PREREG_EVENT.md` (commit `8edbc25`).

## Blocker

- Return phải gắn với đúng nến: `log(C[i]/C[i−1])`. Đặc tả cũ dịch return lên một nến. Cửa sổ 1/4/24 giờ phải có đúng 1/4/24 nến `[0,0]`, `[0,3]`, `[0,23]`; trước tin chỉ `[-4,-1]`; placebo không được chạm T0. Cần test cú sốc duy nhất tại nến sau tin.
- Chốt endpoint CAR và abnormal volume 4 giờ, cùng họ 9 kiểm định, trước khi xem kết quả sửa. Không chọn cửa sổ theo p-value.
- Thiếu input bắt buộc phải làm lệnh chạy thật thất bại với exit code khác 0. Khóa chạy phải phụ thuộc nội dung input, config chuẩn hóa, toàn bộ mã `src/` liên quan và phiên bản thư viện/model.

## Should-fix

- Ước lượng HAC Bartlett 7 lag trên trung bình ngày sự kiện với khoảng trống lịch; kiểm tra bằng bootstrap block 7 ngày, 1.999 lần, seed 42. Báo MDE xấp xỉ `2,802 × SE` cho từng cửa sổ.
- Phân tích tin tốt trừ tin xấu là khám phá; báo Holm của họ lớn ngoài p thô. Tách text thị trường chung và riêng coin, có cờ thiếu text và tỷ lệ fallback theo coin; không thay đặc tả chính.
- Watcher chỉ publish kết quả do chính lần chạy sentinel kích hoạt. Lệnh chạy tay không được khiến watcher tự push.

## Báo cáo lại

- Tạo lại bảng event, hình và `RESULTS.md`; đặt cạnh CAR cũ và mới, ghi kết luận nào giữ hoặc đổi, coverage và giới hạn thời điểm công bố. Chạy pytest offline, commit đúng vùng sở hữu, pull rebase rồi push `dev`.

## Handoff cho phần paper (vùng Claude)

- `paper/fill_results.py:188-210,385-392,488,519` và `paper/paper.md:212,232,242,260` vẫn dùng cửa sổ cũ `[0,1]`, `[0,4]`, `[0,24]`, `[-4,-2]` hoặc cột `car_0_4`. Khi bảng event chuyển sang đúng 1/4/24 nến, ba test trong `paper/test_paper.py` dừng ở `fill_results.py:210` (`0_24` không còn). Cần cập nhật selector, câu chữ, bảng và kết luận theo số mới; tuyệt đối không gắn nhãn cũ cho số mới.
