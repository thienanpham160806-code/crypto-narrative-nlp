# Kết quả dữ liệu thật

Bằng chứng dưới đây chỉ áp dụng cho dữ liệu đã xử lý. Tin cùng ngày được gom theo ngày khi kiểm định sự kiện.

Coverage: corpus chung có 1352/1369 ngày có tin (98.76%); riêng BTC có 1351 ngày tin gắn mã (98.69%), 1 ngày mô hình dùng corpus chung; từ 2023-01-01 00:00:00+00:00 đến 2026-09-30 00:00:00+00:00. Core spec dùng 1344 ngày BTC, train/valid/test=890/182/272.

Robustness text ngày: BNB fallback 551/866 ngày mô hình (63.63%); BTC fallback 1/1344 ngày mô hình (0.0744%); ETH fallback 31/1253 ngày mô hình (2.474%); SOL fallback 140/1035 ngày mô hình (13.53%); XRP fallback 79/1179 ngày mô hình (6.701%). Cờ missing_coin_text tách text riêng coin khỏi corpus chung.

Sự kiện giờ: 142646 tin canonical tiếng Anh, 150160 cặp tin–asset trên 1363 ngày; 140593 tin có FinBERT. Mẫu 2023-01-01 02:00:00+00:00 đến 2026-10-01 00:00:00+00:00.

Bản documents có tin trên 1352 ngày GKG và 503 ngày SEC; đây là số ngày thực sự có tin, không phải số ngày GKG đã thu.

Text BNB: tỷ lệ fallback tin thị trường chung 0% cặp tin–asset; cờ missing_coin_text trong event_observations.csv.
Text BTC: tỷ lệ fallback tin thị trường chung 58.06% cặp tin–asset; cờ missing_coin_text trong event_observations.csv.
Text ETH: tỷ lệ fallback tin thị trường chung 0% cặp tin–asset; cờ missing_coin_text trong event_observations.csv.
Text SOL: tỷ lệ fallback tin thị trường chung 0% cặp tin–asset; cờ missing_coin_text trong event_observations.csv.
Text XRP: tỷ lệ fallback tin thị trường chung 0% cặp tin–asset; cờ missing_coin_text trong event_observations.csv.

Phản ứng chung 4 nến [0,3] car: -0.007821 %, 1363 ngày, HAC p=0.4337, Holm họ 9=1, bootstrap 95%=[-0.0002771, 0.0001286], MDE≈0.0002799 log return.
Phản ứng chung 4 nến [0,3] absret: 0.06882 %, 1363 ngày, HAC p=0.00156, Holm họ 9=0.01092, bootstrap 95%=[0.0002635, 0.001116], MDE≈0.0006096 log return.
Phản ứng chung 4 nến [0,3] volume: 0.04245 log điểm, 1363 ngày, HAC p=0.00454, Holm họ 9=0.02724, bootstrap 95%=[0.01354, 0.073], MDE≈0.04191 log điểm.
Abnormal volume là chênh log(1+USD volume) so với 144 giờ ước lượng trước tin; abnormal |return| là chênh tổng độ lớn lợi suất log.

### So sánh CAR trước và sau sửa căn nến

Số cũ dùng return lệch một nến và cửa sổ 1/4/24 giờ gồm 2/5/25 nến; số mới dùng 1/4/24 nến. P cũ là t thường với Holm họ lớn; p mới là HAC(7) với Holm họ 9 cho nhóm chung.

CAR 1 giờ: cũ -0.003585%, mới 0.0007037%; dấu đổi; kết luận ý nghĩa sau Holm giữ (cũ False, mới False).
CAR 4 giờ: cũ -0.006788%, mới -0.007821%; dấu giữ; kết luận ý nghĩa sau Holm giữ (cũ False, mới False).
CAR 24 giờ: cũ -0.03057%, mới -0.02442%; dấu giữ; kết luận ý nghĩa sau Holm giữ (cũ False, mới False).
Tương phản tốt−xấu CAR 4 giờ (khám phá): cũ -0.01392 điểm %, Holm=0.4308; mới -0.02118 điểm %, Holm họ lớn=0.02032. Kết luận ý nghĩa sau Holm đổi.

## RQ1: FinBERT và từ điển

Đã có: hệ số BTC h=1 sent_lm=-0.0004216, Holm p=1 (n=1073); sent_hv=0.006507, Holm p=1 (n=1073); sent_finbert=0.003279, Holm p=1 (n=1073).
Đã có: 300 tiêu đề gán nhãn độc lập; AUC FinBERT=0.894, LM=0.718, Harvard IV-4=0.726.
Giới hạn: bộ nhãn tay có 300 tiêu đề; hồi quy dự báo theo ngày không thay thế kiểm định độ chính xác phân loại.
Nghĩa kinh tế: AUC FinBERT cao hơn trên bộ nhãn độc lập, nhưng chênh hệ số dự báo không chứng minh lợi ích giao dịch.

## RQ2: tin xấu và tin tốt

Đã có (khám phá): CAR 4 nến [0,3] FinBERT tốt trừ xấu = -0.02118 điểm %, 1352 ngày ghép cặp, HAC p=0.001693, Holm họ lớn=0.02032; xem event_asymmetry.csv.
Biến động tuyệt đối 1 nến [0,0] xấu trừ tốt = -0.01018 điểm %, Holm HAC=0.01897, Holm Wilcoxon=0.02646; hai kiểm định đồng thuận.
Giới hạn: nhiều tin chồng lấp trong cùng giờ; kết quả Wald và phân vị theo ngày không tách được tác động của từng tin.
Nghĩa kinh tế: CAR khác nhau là phản ứng giá có điều kiện, chưa xác định tác động nhân quả của sắc thái tin.

## RQ3: narrative

Đã có: regulation CAR 4 nến [0,3] = -0.00307%, 1333 ngày, HAC p=0.831, Holm họ lớn=1.
Đã có: security_hacks CAR 4 nến [0,3] = 0.002822%, 1350 ngày, HAC p=0.8344, Holm họ lớn=1.
Đã có: etf_institutional CAR 4 nến [0,3] = -0.007642%, 1352 ngày, HAC p=0.4817, Holm họ lớn=1.
Giới hạn: đã hiệu chỉnh Holm, nhưng tin trùng giờ và sai số phân loại narrative vẫn cản trở việc xếp thứ hạng tác động.
Nghĩa kinh tế: nhóm có CAR lớn hơn chỉ là liên hệ trong mẫu tin đã thu.

## RQ4: tin dẫn giá hay giá đi trước tin

Đã có: CAR trước tin [-4,-1] = -0.00172%, 1363 ngày, HAC p=0.8638, Holm họ lớn=1.
Abnormal volume trước tin [-4,-1] = 0.07392 log điểm, HAC p=3.513e-07, Holm họ lớn=9.451e-05; hoạt động trước T0 có thể phản ánh tin khác, thời điểm công bố sai hoặc diễn biến nội sinh.
Độ nhạy giờ [0,0]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=0.1155%, seen=-0.1103%, p published/seen=0.3559/0.253, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.4675.
Độ nhạy giờ [0,3]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.1254%, seen=-0.1375%, p published/seen=0.5118/0.2394, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.953.
Độ nhạy giờ [0,23]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.4533%, seen=-0.8112%, p published/seen=0.2319/0.06419, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.4675.
Đã có: 20 kiểm định Granger trên đoạn ngày liên tục ít nhất 30 quan sát; quan hệ dẫn trước không chứng minh nhân quả.
Nghĩa kinh tế: CAR trước T0 không có ý nghĩa sau Holm; sai số giờ công bố và tin trùng thời điểm không cho phép kết luận giá đi trước tin.

## RQ5: dự báo ngoài mẫu

Đã có: 58284 hàng dự báo ngoài mẫu; 272 hàng BTC EN/text RV h=1 đúng schema dashboard/export.py.
As-of 2026-09-29 00:00:00+00:00: RV dự báo=0.0004627, 270 sai số quá khứ đã biết; fan chart đủ ngưỡng 30.
EN/text BTC RV h=1: R² CT=0.2073, RMSE=0.0005552; DM Holm p=1.
Giới hạn: GW có 90 kết quả và MCS có 108 hàng mô hình; độ dài đoạn dự báo chung thay đổi theo tài sản và mục tiêu. Dải fan theo sai số có thể xuống dưới RV=0.
Nghĩa kinh tế: dự báo thật có thể xuất cho dashboard, nhưng chưa có bằng chứng sau hiệu chỉnh Holm rằng văn bản cải thiện dự báo ngoài mẫu.

Giới hạn thời điểm: GDELT seendate trễ tuyệt đối trung vị 141.5 phút trong 42 cặp audit.
Độ phủ trên là số ngày có tin trong mẫu đã xử lý; các p-value chưa giải quyết việc chỉ lấy một lô GKG mỗi giờ và nhiều sự kiện trùng ngày.
