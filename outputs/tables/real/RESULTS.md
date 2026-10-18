# Kết quả thật, bộ tin đang thu

Bằng chứng dưới đây chỉ áp dụng cho dữ liệu đã thu. Tin cùng ngày được gom theo ngày khi kiểm định sự kiện.

Coverage: corpus chung có 1352/1369 ngày có tin (98.76%); riêng BTC có 1351 ngày tin gắn mã (98.69%), 1 ngày mô hình dùng corpus chung; từ 2023-01-01 00:00:00+00:00 đến 2026-09-30 00:00:00+00:00. Core spec dùng 1344 ngày BTC, train/valid/test=890/182/272.

Sự kiện giờ: 142646 tin canonical tiếng Anh, 150160 cặp tin–asset trên 1363 ngày; 140593 tin có FinBERT. Mẫu 2023-01-01 02:00:00+00:00 đến 2026-10-01 00:00:00+00:00.

Bản documents hiện phủ 1352 ngày GKG và 503 ngày SEC; text_daily có thể chưa được build lại trên cùng ảnh chụp dữ liệu.

Phản ứng chung [0,4]h car: -0.006788 %, 1363 ngày, p t Holm=1.
Phản ứng chung [0,4]h absret: 0.05448 %, 1363 ngày, p t Holm=1.
Phản ứng chung [0,4]h volume: 0.03311 log điểm, 1363 ngày, p t Holm=1.
Abnormal volume là chênh log(1+USD volume) so với 144 giờ ước lượng trước tin; abnormal |return| là chênh tổng độ lớn lợi suất log.

## RQ1: FinBERT và từ điển

Đã có: hệ số BTC h=1 sent_lm=-0.0004216, Holm p=1 (n=1073); sent_hv=0.006507, Holm p=1 (n=1073); sent_finbert=0.003279, Holm p=1 (n=1073).
Chưa đủ: cần nhãn kiểm định độc lập và mẫu tin dày hơn để xếp hạng độ chính xác.
Nghĩa kinh tế: chênh hệ số dự báo không chứng minh FinBERT đọc tin đúng hơn từ điển.

## RQ2: tin xấu và tin tốt

Đã có: CAR [0,4]h FinBERT xấu trừ tốt = 0.01394 điểm %, 1352 ngày ghép cặp, p t=0.09293, Holm=0.4308; xem event_asymmetry.csv.
Biến động tuyệt đối [0,1]h xấu trừ tốt = -0.01616 điểm %, Holm t=0.01296, Holm Wilcoxon=0.1358; hai kiểm định chưa đồng thuận.
Chưa đủ: nhiều giờ có tin chồng lấp; Wald và phân vị theo ngày vẫn phụ thuộc coverage thưa.
Nghĩa kinh tế: CAR khác nhau là phản ứng giá có điều kiện, chưa xác định tác động nhân quả của sắc thái tin.

## RQ3: narrative

Đã có: regulation CAR [0,4]h = -0.004823%, 1333 ngày, p t=0.788, Holm=1.
Đã có: security_hacks CAR [0,4]h = -0.01075%, 1350 ngày, p t=0.5336, Holm=1.
Đã có: etf_institutional CAR [0,4]h = -0.01675%, 1352 ngày, p t=0.2452, Holm=1.
Chưa đủ: cần hiệu chỉnh nhiều kiểm định và kiểm soát tin trùng giờ để so thứ hạng narrative.
Nghĩa kinh tế: nhóm có CAR lớn hơn chỉ là liên hệ trong mẫu tin đã thu.

## RQ4: tin dẫn giá hay giá đi trước tin

Đã có: CAR trước tin nghiêm ngặt [-4,-2]h = -0.001552%, 1363 ngày, p t=0.8625, Holm=1. [-4,0]h có cả nến T0 nên không thuần trước tin.
Độ nhạy giờ [0,1]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.007833%, seen=-0.1269%, p published/seen=0.9507/0.09959, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.7249.
Độ nhạy giờ [0,4]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.2471%, seen=-0.1988%, p published/seen=0.1438/0.221, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.8208.
Độ nhạy giờ [0,24]: 36 tin, 38 cặp tin–asset trên 31 ngày, CAR published=-0.5025%, seen=-0.8663%, p published/seen=0.2049/0.02592, đổi kết luận p<0,05=True, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.3625.
Chưa đủ: 20 kiểm định Granger dùng được; VAR chỉ chạy trên đoạn ngày liên tục ≥30.
Nghĩa kinh tế: CAR trước T0 gợi ý giá đã phản ánh thông tin sớm hoặc sai số giờ công bố; không chứng minh rò rỉ.

## RQ5: dự báo ngoài mẫu

Đã có: 58284 hàng dự báo ngoài mẫu; 272 hàng BTC EN/text RV h=1 đúng schema dashboard/export.py.
As-of 2026-09-29 00:00:00+00:00: RV dự báo=0.0004627, 270 sai số quá khứ đã biết; fan chart đủ ngưỡng 30.
EN/text BTC RV h=1: R² CT=0.2073, RMSE=0.0005552; DM Holm p=1.
Chưa đủ: ngày test có tin rời rạc; DM/GW/MCS cần đoạn liên tục. Dải fan theo sai số có thể xuống dưới RV=0.
Nghĩa kinh tế: dự báo thật có thể xuất cho dashboard; lợi ích của text chỉ đáng tin nếu kiểm định ghép cặp có đủ đoạn liên tục.

Giới hạn thời điểm: GDELT seendate trễ tuyệt đối trung vị 141.5 phút trong 42 cặp audit.
GDELT đang thu tiếp; các p-value chưa giải quyết lựa chọn mẫu tin và nhiều sự kiện trùng ngày.
