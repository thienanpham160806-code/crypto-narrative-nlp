# Kết quả thật, bộ tin đang thu

Bằng chứng dưới đây chỉ áp dụng cho dữ liệu đã thu. Tin cùng ngày được gom theo ngày khi kiểm định sự kiện.

Coverage: 180/1369 ngày có tin (13.15%); từ 2023-01-01 00:00:00+00:00 đến 2026-09-23 00:00:00+00:00. Core spec dùng 176 ngày BTC, train/valid/test=130/12/34.

Sự kiện giờ: 37179 tin canonical tiếng Anh, 39003 cặp tin–asset trên 772 ngày; 18738 tin có FinBERT. Mẫu 2023-01-01 02:00:00+00:00 đến 2026-09-30 21:00:00+00:00.

Bản documents hiện phủ 339 ngày GKG và 503 ngày SEC; text_daily có thể chưa được build lại trên cùng ảnh chụp dữ liệu.

Phản ứng chung [0,4]h car: 0.03715 %, 772 ngày, p t Holm=1.
Phản ứng chung [0,4]h absret: 0.03134 %, 772 ngày, p t Holm=1.
Phản ứng chung [0,4]h volume: 0.03151 log điểm, 772 ngày, p t Holm=1.
Abnormal volume là chênh log(1+USD volume) so với 144 giờ ước lượng trước tin; abnormal |return| là chênh tổng độ lớn lợi suất log.

## RQ1: FinBERT và từ điển

Đã có: hệ số BTC h=1 sent_lm=-0.02807, Holm p=1 (n=143); sent_hv=-0.01155, Holm p=1 (n=143); sent_finbert=0.008371, Holm p=1 (n=143).
Chưa đủ: cần nhãn kiểm định độc lập và mẫu tin dày hơn để xếp hạng độ chính xác.
Nghĩa kinh tế: chênh hệ số dự báo không chứng minh FinBERT đọc tin đúng hơn từ điển.

## RQ2: tin xấu và tin tốt

Đã có: CAR [0,4]h FinBERT xấu trừ tốt = -0.01813 điểm %, 215 ngày ghép cặp, p t=0.4331, Holm=1; xem event_asymmetry.csv.
Biến động tuyệt đối [0,1]h xấu trừ tốt = -0.0409 điểm %, Holm t=0.03065, Holm Wilcoxon=0.3061; hai kiểm định chưa đồng thuận.
Chưa đủ: nhiều giờ có tin chồng lấp; Wald và phân vị theo ngày vẫn phụ thuộc coverage thưa.
Nghĩa kinh tế: CAR khác nhau là phản ứng giá có điều kiện, chưa xác định tác động nhân quả của sắc thái tin.

## RQ3: narrative

Đã có: regulation CAR [0,4]h = 0.03834%, 388 ngày, p t=0.4051, Holm=1.
Đã có: security_hacks CAR [0,4]h = -0.04233%, 215 ngày, p t=0.2991, Holm=1.
Đã có: etf_institutional CAR [0,4]h = -0.02076%, 361 ngày, p t=0.6113, Holm=1.
Chưa đủ: cần hiệu chỉnh nhiều kiểm định và kiểm soát tin trùng giờ để so thứ hạng narrative.
Nghĩa kinh tế: nhóm có CAR lớn hơn chỉ là liên hệ trong mẫu tin đã thu.

## RQ4: tin dẫn giá hay giá đi trước tin

Đã có: CAR trước tin nghiêm ngặt [-4,-2]h = -0.0156%, 772 ngày, p t=0.5206, Holm=1. [-4,0]h có cả nến T0 nên không thuần trước tin.
Độ nhạy giờ [0,1]: 37 tin, 39 cặp tin–asset trên 32 ngày, CAR published=0.03999%, seen=-0.1251%, p published/seen=0.7619/0.09349, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.4466.
Độ nhạy giờ [0,4]: 37 tin, 39 cặp tin–asset trên 32 ngày, CAR published=-0.1608%, seen=-0.1915%, p published/seen=0.382/0.2236, đổi kết luận p<0,05=False, sau Holm=False; kiểm định chênh lệch ghép cặp Holm p=0.8896.
Độ nhạy giờ [0,24]: 37 tin, 39 cặp tin–asset trên 32 ngày, CAR published=-0.4633%, seen=-1.021%, p published/seen=0.229/0.01354, đổi kết luận p<0,05=True, sau Holm=True; kiểm định chênh lệch ghép cặp Holm p=0.2009.
Chưa đủ: 0 kiểm định Granger dùng được; VAR chỉ chạy trên đoạn ngày liên tục ≥30.
Nghĩa kinh tế: CAR trước T0 gợi ý giá đã phản ánh thông tin sớm hoặc sai số giờ công bố; không chứng minh rò rỉ.

## RQ5: dự báo ngoài mẫu

Đã có: 6480 hàng dự báo ngoài mẫu; 34 hàng BTC EN/text RV h=1 đúng schema dashboard/export.py.
As-of 2026-09-23 00:00:00+00:00: RV dự báo=0.0004446, 32 sai số quá khứ đã biết; fan chart đủ ngưỡng 30.
EN/text BTC RV h=1: R² CT=-0.007658, RMSE=0.0005086; DM Holm p=NA.
Chưa đủ: ngày test có tin rời rạc; DM/GW/MCS cần đoạn liên tục. Dải fan theo sai số có thể xuống dưới RV=0.
Nghĩa kinh tế: dự báo thật có thể xuất cho dashboard; lợi ích của text chỉ đáng tin nếu kiểm định ghép cặp có đủ đoạn liên tục.

Giới hạn thời điểm: GDELT seendate trễ tuyệt đối trung vị 141.5 phút trong 42 cặp audit.
GDELT đang thu tiếp; các p-value chưa giải quyết lựa chọn mẫu tin và nhiều sự kiện trùng ngày.
