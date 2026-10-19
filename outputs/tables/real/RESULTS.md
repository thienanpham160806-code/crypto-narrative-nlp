# Kết quả dữ liệu thật

Bằng chứng dưới đây chỉ áp dụng cho dữ liệu đã xử lý. Tin cùng ngày được gom theo ngày khi kiểm định sự kiện.

Coverage: corpus chung có 1352/1369 ngày có tin (98.76%); riêng BTC có 1351 ngày tin gắn mã (98.69%), 1 ngày mô hình dùng corpus chung; từ 2023-01-01 00:00:00+00:00 đến 2026-09-30 00:00:00+00:00. Core spec dùng 1344 ngày BTC, train/valid/test=890/182/272.

Sự kiện giờ: 142646 tin canonical tiếng Anh, 150160 cặp tin–asset trên 1363 ngày; 140593 tin có FinBERT. Mẫu 2023-01-01 02:00:00+00:00 đến 2026-10-01 00:00:00+00:00.

Bản documents có tin trên 1352 ngày GKG và 503 ngày SEC; đây là số ngày thực sự có tin, không phải số ngày GKG đã thu.

Phản ứng chung [0,4]h car: -0.006788 %, 1363 ngày, p t Holm=1.
Phản ứng chung [0,4]h absret: 0.05448 %, 1363 ngày, p t Holm=1.
Phản ứng chung [0,4]h volume: 0.03311 log điểm, 1363 ngày, p t Holm=1.
Abnormal volume là chênh log(1+USD volume) so với 144 giờ ước lượng trước tin; abnormal |return| là chênh tổng độ lớn lợi suất log.

## RQ1: FinBERT và từ điển

Đã có: hệ số BTC h=1 sent_lm=-0.0004216, Holm p=1 (n=1073); sent_hv=0.006507, Holm p=1 (n=1073); sent_finbert=0.003279, Holm p=1 (n=1073).
Đã có: 300 tiêu đề gán nhãn độc lập; AUC FinBERT=0.894, LM=0.718, Harvard IV-4=0.726.
Giới hạn: bộ nhãn tay có 300 tiêu đề; hồi quy dự báo theo ngày không thay thế kiểm định độ chính xác phân loại.
Nghĩa kinh tế: AUC FinBERT cao hơn trên bộ nhãn độc lập, nhưng chênh hệ số dự báo không chứng minh lợi ích giao dịch.

## RQ2: tin xấu và tin tốt

Đã có: CAR [0,4]h FinBERT xấu trừ tốt = 0.01392 điểm %, 1352 ngày ghép cặp, p t=0.09336, Holm=0.4308; xem event_asymmetry.csv.
Biến động tuyệt đối [0,1]h xấu trừ tốt = -0.01615 điểm %, Holm t=0.01311, Holm Wilcoxon=0.1364; hai kiểm định chưa đồng thuận.
Giới hạn: nhiều tin chồng lấp trong cùng giờ; kết quả Wald và phân vị theo ngày không tách được tác động của từng tin.
Nghĩa kinh tế: CAR khác nhau là phản ứng giá có điều kiện, chưa xác định tác động nhân quả của sắc thái tin.

## RQ3: narrative

Đã có: regulation CAR [0,4]h = -0.004823%, 1333 ngày, p t=0.788, Holm=1.
Đã có: security_hacks CAR [0,4]h = -0.01075%, 1350 ngày, p t=0.5336, Holm=1.
Đã có: etf_institutional CAR [0,4]h = -0.01675%, 1352 ngày, p t=0.2452, Holm=1.
Giới hạn: đã hiệu chỉnh Holm, nhưng tin trùng giờ và sai số phân loại narrative vẫn cản trở việc xếp thứ hạng tác động.
Nghĩa kinh tế: nhóm có CAR lớn hơn chỉ là liên hệ trong mẫu tin đã thu.

## RQ4: tin dẫn giá hay giá đi trước tin

Đã có: CAR trước tin nghiêm ngặt [-4,-2]h = -0.001552%, 1363 ngày, p t=0.8625, Holm=1. [-4,0]h có cả nến T0 nên không thuần trước tin.
Độ nhạy giờ [0,1]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.007833%, seen=-0.1269%, p published/seen=0.9507/0.09959, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.7249.
Độ nhạy giờ [0,4]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.2471%, seen=-0.1988%, p published/seen=0.1438/0.221, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.8208.
Độ nhạy giờ [0,24]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.5025%, seen=-0.8663%, p published/seen=0.2049/0.02592, đổi kết luận p<0,05=True, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.3625.
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
