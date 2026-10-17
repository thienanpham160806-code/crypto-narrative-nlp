# Narrative và sentiment tin tức trên thị trường tiền mã hóa: Tín hiệu văn bản theo thời điểm công bố cho lợi suất, biến động và khối lượng giao dịch

*Nhóm nghiên cứu Fintech, Trường Đại học Kinh tế – Luật (UEL), ĐHQG-HCM.*

*Phiên bản làm việc ngày 18/10/2026.*

> **Trạng thái dữ liệu.** Bộ thu GDELT mới phủ một phần mẫu (xem mục 4.5). Các con số ở mục 6 chỉ dùng dữ liệu đã thu tới ngày lập bản này và được ghi "sơ bộ". Kết quả RQ2–RQ5 lấy từ `outputs/tables/real/RESULTS.md` (bản chụp 180 ngày có tin) và sẽ được tính lại trên toàn mẫu. Không có con số nào trong bài được ước đoán.

## Tóm tắt

Nghiên cứu xây dựng chỉ số sentiment, attention và narrative từ tin tức tiếng Anh về tiền mã hóa giai đoạn 01/2023–09/2026. Mục tiêu là kiểm định các chỉ số này có mang thông tin gia tăng cho lợi suất, biến động thực hiện và khối lượng của BTC, ETH, SOL, BNB, XRP hay không, ngoài các biến thị trường.

Đóng góp chính là phương pháp. Mỗi tin được gán ngày theo thời điểm ra công chúng có kiểm chứng. Độ lệch giữa các đồng hồ dữ liệu được đo theo nguồn. Mọi mô hình văn bản chỉ được ước lượng trên kỳ huấn luyện.

Kết quả về đo lường cho thấy:
- Đồng hồ "thấy tin" của GDELT trễ trung vị 142 phút so với giờ đăng trong trang. 16,7% tin sẽ bị gán sang ngày UTC khác nếu dùng đồng hồ này.
- Ngày nộp hồ sơ (`file_date`) của SEC lệch ngày so với giờ chấp nhận ở 6,4% hồ sơ.
- Trên 6.995 tiêu đề có nhãn yếu từ phiếu bình chọn của người dùng CryptoPanic, FinBERT phân biệt tin tốt và tin xấu tốt nhất (AUC 0,712). Từ điển Loughran–McDonald đạt 0,612, CryptoBERT 0,591, Harvard IV-4 0,571.

Kết quả sơ bộ về tác động tới giá (180 ngày có tin) cho thấy:
- Chưa có phản ứng giá có ý nghĩa sau hiệu chỉnh kiểm định bội theo sắc thái hay narrative.
- Kết luận về phản ứng trong 24 giờ đổi theo đồng hồ dùng để gán thời điểm.
- Văn bản chưa cải thiện dự báo biến động BTC ngoài mẫu (R² ngoài mẫu −0,008).

**Từ khóa:** tiền mã hóa, phân tích văn bản, FinBERT, narrative economics, look-ahead bias, dự báo ngoài mẫu.

## 1. Giới thiệu

Thị trường tiền mã hóa không có dòng tiền cơ bản như cổ tức hay lợi nhuận doanh nghiệp. Vì vậy giá phụ thuộc nhiều vào câu chuyện mà nhà đầu tư cùng chia sẻ. Đó là các narrative về quy định pháp lý, quỹ ETF, dòng tiền tổ chức, các vụ tấn công sàn, stablecoin, DeFi, token trí tuệ nhân tạo và chính sách tiền tệ (Shiller, 2017; Walker, 2024). Tin tức là kênh chính để các narrative này lan truyền.

Câu hỏi thực nghiệm là: thông tin trích từ văn bản có giúp giải thích và dự báo lợi suất, biến động và khối lượng không, khi đã kiểm soát những gì giá và khối lượng quá khứ chứa đựng?

Tài liệu hiện có trả lời câu hỏi này theo từng mảnh. Có nghiên cứu dùng sentiment tổng hợp từ mạng xã hội (Kraaijeveld & De Smedt, 2020) hoặc từ tin tức (Chou et al., 2023; Kao et al., 2024; Gür & Ünal, 2026). Có nghiên cứu dùng chủ đề trên diễn đàn (Khaksar et al., 2026) hoặc narrative trên báo in (Walker, 2024). Ba vấn đề thường bị bỏ qua:
1. Thời điểm một tin thực sự ra công chúng ít khi được kiểm chứng. Vì vậy chỉ số ngày t có thể chứa tin xuất hiện sau khi giá đã phản ứng.
2. Mô hình văn bản thường được ước lượng trên toàn mẫu, kể cả kỳ dùng để đánh giá.
3. Từ điển và transformer hiếm khi được so trên cùng corpus crypto và cùng biến mục tiêu.

Nghiên cứu đặt năm câu hỏi:
- **RQ1:** Sentiment từ transformer có đo giọng điệu tin crypto tốt hơn từ điển không?
- **RQ2:** Tin xấu có tác động khác tin tốt không?
- **RQ3:** Narrative nào liên hệ mạnh nhất với lợi suất, biến động và khối lượng?
- **RQ4:** Văn bản dẫn dắt giá, hay giá dẫn dắt văn bản?
- **RQ5:** Văn bản có cải thiện dự báo ngoài mẫu so với mô hình chỉ có biến thị trường không?

## 2. Cơ sở lý thuyết

### 2.1. Thông tin, hiệu quả thị trường và sentiment nhà đầu tư

Theo giả thuyết thị trường hiệu quả (Fama, 1970), thông tin công khai được phản ánh nhanh vào giá. Khi đó, chỉ số văn bản dựng từ tin đã công bố không thể dự báo lợi suất tương lai một cách có hệ thống. Ngược lại, tài chính hành vi cho rằng sentiment nhà đầu tư, tức niềm tin không hoàn toàn dựa trên dữ kiện cơ bản, có thể đẩy giá lệch khỏi giá trị nội tại rồi đảo chiều (Baker & Wurgler, 2007).

Tetlock (2007) cho thấy mức độ bi quan của một chuyên mục báo tài chính dự báo áp lực giảm giá cổ phiếu Mỹ, sau đó giá hồi lại. Đây là dấu hiệu của sentiment hơn là thông tin cơ bản. Antweiler và Frank (2004) đo mức bất đồng giữa các bài đăng trên diễn đàn và thấy nó gắn với khối lượng giao dịch. Như vậy, không chỉ mức sentiment mà cả độ phân tán của nó cũng mang thông tin.

### 2.2. Sự chú ý và narrative

Nhà đầu tư có giới hạn về sự chú ý. Tài sản được chú ý nhiều hơn sẽ có áp lực mua ngắn hạn rồi đảo chiều (Da et al., 2011). Với tiền mã hóa, Liu và Tsyvinski (2021) cho thấy momentum và sự chú ý của nhà đầu tư dự báo lợi suất. Kristoufek (2013) ghi nhận quan hệ hai chiều giữa lượt tìm kiếm và giá Bitcoin.

Shiller (2017) đề xuất "kinh tế học narrative": các câu chuyện lan truyền như dịch bệnh và tác động lên hành vi kinh tế. Bybee et al. (2024) chuyển ý tưởng này thành phép đo: tỷ trọng chủ đề trong tin kinh doanh theo thời gian, từ đó giải thích và dự báo hoạt động kinh tế. Nghiên cứu này áp dụng cùng logic cho crypto. Narrative attention được định nghĩa là tỷ trọng tin thuộc mỗi narrative trong ngày.

### 2.3. Luồng thông tin và biến động

Giả thuyết phân phối hỗn hợp (MDH) cho rằng biến động và khối lượng cùng phản ứng đồng thời với luồng thông tin. Giả thuyết thông tin đến tuần tự (SIAH) cho rằng thông tin lan dần, nên có quan hệ trễ. Chou et al. (2023) thấy tin tiêu cực về Bitcoin phù hợp SIAH, còn tin tích cực phù hợp MDH. Kao et al. (2024) có kết quả tương tự trên hợp đồng tương lai. Đây là cơ sở cho RQ2 (bất đối xứng) và RQ4 (lead-lag).

### 2.4. Đo giọng điệu văn bản

Loughran và McDonald (2011) cho thấy từ điển tổng quát như Harvard IV-4 phân loại sai nhiều từ trong ngữ cảnh tài chính. Ví dụ, "liability" hay "tax" mang nghĩa trung tính trong báo cáo tài chính. Họ đề xuất một từ điển chuyên ngành. FinBERT (Araci, 2019) tinh chỉnh mô hình ngôn ngữ BERT trên câu tin tài chính, nên nắm được ngữ cảnh và phủ định tốt hơn danh sách từ. Với crypto, Nasekin và Chen (2020) và Ider và Lessmann (2022) cho thấy mô hình học sâu và nhãn yếu cải thiện việc dựng sentiment. RQ1 kiểm định trực tiếp lợi thế này trên tiêu đề tin crypto.

## 3. Tổng quan nghiên cứu và tính mới

Bảng so sánh chi tiết 7 nghiên cứu lõi nằm trong `paper/related_work.md`.
- **Về sentiment:** Kraaijeveld và De Smedt (2020) dùng từ điển trên Twitter và thấy với nhiều coin, giá dẫn dắt sentiment. Gür và Ünal (2026) dùng FinBERT trên hơn 650.000 tiêu đề, nhưng không so với từ điển.
- **Về chủ đề:** Khaksar et al. (2026) dùng LDA trên Bitcointalk và đo độ phân tán sentiment theo chủ đề.
- **Về narrative:** Walker (2024) phân tích narrative crypto trên báo chính thống.
- **Về dự báo:** Garcia và Schweitzer (2015) và Critien et al. (2022) đánh giá ngoài mẫu. Ortu et al. (2022) kết hợp chỉ báo kỹ thuật và mạng xã hội.

Tính mới của nghiên cứu nằm ở năm điểm:
1. **Thời điểm công bố được kiểm chứng.** Mỗi tin có `public_ts_utc` dựng từ nhiều đồng hồ và quy tắc chống lùi ngày. Sai lệch giữa các đồng hồ được công bố theo nguồn, chứ không mặc định ngày trong dữ liệu là ngày công bố.
2. **Không rò rỉ từ mô hình văn bản.** Vectorizer, LDA, BERTopic và ngưỡng phân loại chỉ fit trên kỳ train. LLM không được dùng làm feature, vì mô hình ngôn ngữ lớn có thể "biết" sự kiện xảy ra sau ngày của tin.
3. **So sánh đo lường trên cùng corpus crypto.** Từ điển tài chính, từ điển tổng quát, FinBERT và CryptoBERT được so trên cùng tập tiêu đề có nhãn.
4. **Narrative có tên, định trước.** Tám narrative được đo bằng zero-shot. LDA và BERTopic được báo cáo song song để đối chứng.
5. **Đánh giá ngoài mẫu bằng kiểm định thống kê.** Mô hình chỉ có biến thị trường được so với mô hình thêm văn bản theo walk-forward, có kiểm định Diebold–Mariano và hiệu chỉnh kiểm định bội.

## 4. Dữ liệu

### 4.1. Mẫu và chia kỳ

Mẫu gồm năm tài sản BTC, ETH, SOL, BNB, XRP, từ 01/01/2023 đến 30/09/2026, theo ngày. Ngày được tính là [00:00, 24:00) giờ UTC, vì thị trường giao dịch liên tục. Mẫu chia ba kỳ không chồng nhau:
- train: đến 30/06/2025;
- valid: đến 31/12/2025;
- test: từ 01/01/2026.

Kỳ test không được dùng khi chọn tham số, chọn số chủ đề hay ngưỡng.

### 4.2. Dữ liệu thị trường

Giá lấy từ Binance qua thư viện ccxt, nến ngày và nến giờ. Lợi suất là log-return ngày. Biến động thực hiện (RV) là tổng bình phương log-return giờ trong ngày (Andersen & Bollerslev, 1998). Khối lượng tính theo USD và lấy log.

### 4.3. Dữ liệu văn bản

| Nguồn | Vai trò | Đồng hồ gán ngày | Ghi chú |
|---|---|---|---|
| GDELT GKG 2.0, lô :00 mỗi giờ | Nguồn chính: tiêu đề tin tiếng Anh, lọc bằng từ khóa crypto | Giờ GDELT thấy tin; dùng giờ đăng trong HTML meta khi có và cùng ngày UTC | Lô :00 ≈ 25% số bài; lấy theo thứ tự rải đều thời gian, không chọn theo nội dung |
| SEC EDGAR full-text search | Sự kiện pháp lý/ETF (S-1, 19b-4, 8-K) | Giờ "Accepted" (New York → UTC) | Không đưa vào chỉ số ngày; dùng cho phân tích sự kiện |
| GDELT translation, tiếng Việt | Nhánh phụ | Giờ GDELT thấy tin | Chấm bằng từ điển tài chính tiếng Việt, không dịch |
| CryptoPanic dataset (CC0) | Nhãn yếu cho RQ1 | `newsDatetime` (UTC, mục 5.1) | Dừng ở 03/12/2025, không phủ kỳ test, nên không dùng làm feature |
| UCRY Policy/Price (Lucey et al., 2022) | Biến kiểm soát bất định chung | Tuần kết thúc Chủ nhật, dùng từ thứ Hai | Có đến hết 2024 |

RSS của các trang tin crypto chỉ lưu khoảng hai ngày gần nhất, và điều khoản của CoinDesk, Cointelegraph, Decrypt cấm thu tự động. Vì vậy RSS chỉ dùng cho bản demo trực tiếp của dashboard.

### 4.4. Thời điểm ra công chúng, trùng lặp và gắn mã

Mỗi tin có:
- giờ đăng (`published_at_utc`), nếu nguồn công bố;
- giờ hệ thống thấy tin (`first_seen_utc`).

Thời điểm ra công chúng được tính là `public_ts_utc = min(giờ đăng hợp lệ, giờ thấy)`. Giờ đăng hợp lệ phải thỏa ba điều kiện:
1. không sau giờ thấy;
2. không sớm hơn giờ thấy quá 48 giờ;
3. cùng ngày UTC với giờ thấy.

Điều kiện (3) xuất phát từ kiểm tra đối kháng. Văn bản ta có là bản thấy lúc `first_seen_utc`, và bài có thể đã sửa sau giờ đăng. Nếu lùi văn bản đó qua nửa đêm, thông tin của ngày t+1 sẽ lọt vào chỉ số ngày t. Tin thuộc ngày t khi `public_ts_utc ∈ [t, t+1)` UTC.

Hai tin được coi là trùng khi cùng URL chuẩn hóa, hoặc khi tiêu đề giống nhau ít nhất 90% với một bản gốc trong vòng 3 ngày trước. URL chuẩn hóa chỉ bỏ tham số theo dõi, giữ đường dẫn và tham số định danh bài. Bản gốc là bản công bố sớm nhất. So khớp không nối chuỗi: mỗi tin chỉ so với bản gốc, không so với bản trùng khác. Mã coin gắn bằng biểu thức chính quy theo ticker và tên.

### 4.5. Độ phủ dữ liệu

Tại thời điểm lập bản này, GDELT đã thu được 445/1.369 ngày. Chuỗi văn bản đã dựng lại trên 338 ngày, gồm 35.126 tin tiếng Anh canonical. Mô hình kinh tế lượng ở mục 6.3 chạy trên bản chụp trước đó (180 ngày). Bảng thống kê corpus (`outputs/tables/corpus_stats.csv`) sẽ được cập nhật khi thu đủ.

## 5. Phương pháp

### 5.1. Kiểm định đồng hồ dữ liệu

Độ lệch giữa giờ thấy và giờ đăng được đo cho từng nguồn:
- **GDELT:** lấy một mẫu ngẫu nhiên URL (seed cố định). Chỉ truy cập các trang mà robots.txt cho phép, và đọc giờ đăng có múi giờ trong thẻ meta.
- **SEC:** so giờ chấp nhận (đổi sang UTC) với `file_date`.
- **CryptoPanic:** suy ra múi giờ bằng cách khớp tiêu đề trùng với GDELT.

### 5.2. Sentiment từng tin

- **Loughran–McDonald** (Loughran & McDonald, 2011). Mẫu số là số từ thuộc từ điển gốc. Một từ tích cực bị bỏ nếu có từ phủ định trong ba từ đứng trước. Điểm ròng = (P − N)/(P + N).
- **Harvard IV-4**: từ điển tổng quát, làm đối chứng.
- **FinBERT** (Araci, 2019). Điểm = P(tích cực) − P(tiêu cực) ∈ [−1, 1], trung bình trên tối đa 20 câu đầu.
- **CryptoBERT**: mô hình huấn luyện trên bài đăng crypto, điểm = P(Bullish) − P(Bearish). Chỉ dùng ở bước kiểm định, vì không rõ dữ liệu huấn luyện của nó có trùng giai đoạn mẫu không.
- **Tin tiếng Việt**: từ điển tài chính tiếng Việt cộng từ điển crypto tự xây, khớp cụm dài nhất, có xử lý phủ định.

### 5.3. Narrative

Tám narrative định trước: quy định, ETF/tổ chức, an ninh/hack, stablecoin, DeFi, token AI, vĩ mô/tiền tệ, giá/đầu cơ.

- **Zero-shot (phương pháp chính).** Tin và mô tả mỗi narrative được biểu diễn bằng embedding đa ngữ. Xác suất narrative là softmax của độ tương đồng cosine. Tin có độ tương đồng cao nhất dưới phân vị 20% của kỳ train được gán "other".
- **LDA** (benchmark). Vectorizer và mô hình chỉ fit trên train. Số chủ đề K ∈ {8, 12, 16, 20} chọn theo perplexity trên kỳ valid.
- **BERTopic** (Grootendorst, 2022). Chỉ fit trên train, các kỳ sau dùng transform.

Chủ đề của LDA và BERTopic được ánh xạ sang narrative bằng embedding của mười từ đặc trưng.

### 5.4. Chỉ số ngày

Với mỗi ngày t, xét riêng toàn thị trường và từng mã coin:
- **Sentiment:** Sent_t = (1/N_t) Σ_d s_d. Tách thành pos_t = trung bình max(s, 0) và neg_t = trung bình max(−s, 0) để kiểm định bất đối xứng.
- **Attention cứng:** Att_k,t = N_k,t / N_t. **Attention mềm:** trung bình xác suất narrative.
- **Hai thước đo bất đồng, đặt tên riêng:**
  - Antweiler–Frank: √(1 − A_t²), với A_t = (N⁺ − N⁻)/(N⁺ + N⁻) theo nhãn FinBERT (Antweiler & Frank, 2004).
  - Độ lệch chuẩn sentiment trong ngày, theo tinh thần Khaksar et al. (2026).
- **Gia tốc tin xấu:** neg_t − neg_{t−1}.

Chỉ dùng tin báo tiếng Anh. Mỗi tin có trọng số bằng nhau.

### 5.5. Kiểm định đo lường (RQ1)

- **Nhãn tay:** 300 tiêu đề chọn ngẫu nhiên trước kỳ test, gán nhãn giọng điệu và narrative.
- **Nhãn yếu:** 6.995 tiêu đề CryptoPanic có ít nhất ba phiếu, chênh lệch phiếu ít nhất hai. Nhãn là phiếu tích cực/tiêu cực của người dùng, phản ánh kỳ vọng giá của đám đông.

Chỉ tiêu: accuracy, macro-F1 và AUC giữa tin tốt và tin xấu. AUC không bị ảnh hưởng bởi mất cân bằng lớp. Điểm bằng 0 (phương pháp không chọn phía) được tính là sai.

### 5.6. Hồi quy dự báo, bất đối xứng và lead-lag (RQ2–RQ4)

Hồi quy dự báo có dạng y_{i,t+h} = α + β·Text_{i,t} + γ′·Market_{i,t} + ε. Trong đó y là lợi suất, RV hoặc log khối lượng, và h ∈ {1, 3, 7}. Sai số chuẩn dùng Newey–West (Newey & West, 1987), độ trễ 7.

RQ2 tách sentiment thành phần dương và âm, kiểm định Wald H₀: β⁻ = β⁺. RQ4 dùng VAR hai chiều, chọn độ trễ theo AIC, với kiểm định nhân quả Granger (Granger, 1969). Holm và Benjamini–Hochberg kiểm soát lỗi khi kiểm định nhiều giả thuyết.

### 5.7. Nghiên cứu sự kiện theo giờ

Quanh mỗi tin, lợi suất bất thường tích lũy (CAR) được tính trên nến giờ, so với trung bình 144 giờ ước lượng trước tin. Tin cùng ngày được gom theo ngày để tránh đếm trùng. Cửa sổ trước tin [−4, −2] giờ kiểm tra giá có chạy trước tin không. Các tin có cả giờ đăng và giờ thấy được tính hai lần, mỗi lần theo một đồng hồ, để đo độ nhạy của kết luận với đồng hồ.

### 5.8. Dự báo ngoài mẫu (RQ5)

Elastic Net, XGBoost và LightGBM được ước lượng theo cửa sổ mở rộng (walk-forward). Có ba phiên bản:
1. chỉ biến thị trường;
2. thị trường cộng attention thô;
3. thị trường cộng toàn bộ văn bản.

Siêu tham số chọn trên kỳ valid. Chỉ tiêu là RMSE và R² ngoài mẫu so với trung bình lịch sử (Campbell & Thompson, 2008). So sánh dùng kiểm định Diebold–Mariano (Diebold & Mariano, 1995). Vì mô hình chỉ có biến thị trường lồng trong mô hình có văn bản, kết quả được đối chiếu thêm với kiểm định Clark–West (Clark & West, 2007). Giá trị kinh tế được đánh giá bằng chiến lược tín hiệu sau phí giao dịch 10 điểm cơ bản.

## 6. Kết quả

### 6.1. Độ tin cậy của đồng hồ dữ liệu

**Bảng 1.** Độ lệch giữa các đồng hồ dữ liệu

| So sánh | n cặp | Trung vị lệch | % lệch > 1 giờ | % đổi ngày UTC |
|---|---|---|---|---|
| GDELT giờ thấy so với giờ đăng trong HTML | 42 | +142 phút | 78,6 | 16,7 |
| SEC giờ chấp nhận (UTC) so với `file_date` | 2.053 | — | — | 6,4 |
| GDELT giờ thấy so với CryptoPanic, tiêu đề trùng | 695 | +1,3 giờ | — | — |

**Ý nghĩa.**
- GDELT thấy tin trễ khoảng hai giờ so với giờ đăng, và cứ sáu tin thì có một tin rơi sang ngày UTC hôm sau. Nghiên cứu gán những tin này vào ngày *thấy*, tức là phía an toàn. Cách này có thể làm trễ tín hiệu nhưng không tạo look-ahead. Do đó các hệ số ở mục 6.3 nếu có sai lệch thì là sai lệch về phía thận trọng.
- Với SEC, dùng ngày nộp hồ sơ sẽ gán sai ngày cho 6,4% hồ sơ, vì hồ sơ nộp sau 17:30 giờ New York được tính sang ngày làm việc kế tiếp.
- Độ lệch +1,3 giờ giữa GDELT và CryptoPanic, cộng với việc lệch gần như luôn dương, cho thấy CryptoPanic ghi giờ theo UTC.

### 6.2. Đo lường sentiment (RQ1)

**Bảng 2.** Sentiment so với nhãn yếu CryptoPanic (n = 6.995; 81,6% nhãn tích cực)

| Phương pháp | Accuracy | Macro-F1 | AUC | % tin có phân định |
|---|---|---|---|---|
| Loughran–McDonald | 0,155 | 0,184 | 0,612 | 25,8 |
| Harvard IV-4 | 0,312 | 0,245 | 0,571 | 49,2 |
| FinBERT | 0,748 | 0,637 | **0,712** | 100,0 |
| CryptoBERT | 0,802 | 0,520 | 0,591 | 100,0 |

**Ý nghĩa.**
- FinBERT xếp hạng tin tốt trên tin xấu đúng hơn các phương pháp còn lại. Như vậy RQ1 được ủng hộ: transformer tốt hơn từ điển trên tiêu đề crypto.
- Hai từ điển bỏ trống phần lớn tiêu đề: Loughran–McDonald chỉ phân định được 25,8% số tin. Tiêu đề ngắn hiếm khi chứa từ trong danh sách, nên từ điển phù hợp với văn bản dài hơn tiêu đề.
- CryptoBERT có accuracy cao nhất chỉ vì gần như luôn đoán "bullish" trong khi 81,6% nhãn là tích cực. Macro-F1 và AUC thấp của nó cho thấy mô hình huấn luyện trên mạng xã hội không chuyển tốt sang tiêu đề tin.
- Nhãn yếu đo kỳ vọng giá của đám đông, không phải giọng điệu do chuyên gia đánh giá. Kết quả trên 300 nhãn tay sẽ bổ sung ở bản sau.

### 6.3. Bất đối xứng, narrative, lead-lag và dự báo ngoài mẫu (RQ2–RQ5) — sơ bộ

Kết quả mục này lấy từ `outputs/tables/real/RESULTS.md`. Bản chụp dữ liệu gồm 180/1.369 ngày có tin. Đặc tả chính cho BTC dùng 176 ngày, chia train/valid/test là 130/12/34. Nghiên cứu sự kiện theo giờ dùng 37.179 tin canonical tiếng Anh, tạo 39.003 cặp tin–tài sản trên 772 ngày. Khi bộ thu GDELT phủ đủ mẫu, các con số sẽ được tính lại. Mọi p-value dưới đây đã hiệu chỉnh Holm trong từng họ kiểm định.

**Bảng 3.** Phản ứng giá quanh thời điểm công bố, cửa sổ [0, 4] giờ

| Nhóm tin | Chỉ tiêu | Ước lượng | Số ngày | p (Holm) |
|---|---|---|---|---|
| Toàn bộ | CAR | 0,037% | 772 | 1,000 |
| Toàn bộ | \|lợi suất\| bất thường | 0,031% | 772 | 1,000 |
| Toàn bộ | Khối lượng bất thường (log) | 0,032 | 772 | 1,000 |
| Regulation | CAR | 0,038% | 388 | 1,000 |
| Security/hacks | CAR | −0,042% | 215 | 1,000 |
| ETF/institutional | CAR | −0,021% | 361 | 1,000 |

**RQ2: bất đối xứng.**
- Chênh lệch CAR [0, 4] giờ giữa tin FinBERT xấu và tin tốt là −0,018 điểm % (215 ngày ghép cặp; p = 0,433, Holm = 1).
- Với biến động tuyệt đối [0, 1] giờ, chênh lệch là −0,041 điểm %. Kiểm định t có ý nghĩa sau Holm (p = 0,031), nhưng kiểm định Wilcoxon thì không (p = 0,306).

*Ý nghĩa:* chưa có bằng chứng vững rằng tin xấu tác động mạnh hơn tin tốt. Hai kiểm định cho kết luận khác nhau, nên kết quả nhạy với phân phối đuôi và chưa đủ để kết luận.

**RQ3: narrative.** Không narrative nào có phản ứng giá có ý nghĩa thống kê (Bảng 3). Dấu ước lượng phù hợp trực giác (tin hack âm, tin quy định dương), nhưng độ lớn nhỏ so với sai số. *Ý nghĩa:* với mẫu hiện tại, chưa thể xếp hạng narrative theo tác động.

**RQ4: dẫn trước hay theo sau.**
- CAR trong cửa sổ trước tin [−4, −2] giờ là −0,016% (p = 0,521, Holm = 1). Không thấy giá đã chạy trước khi tin ra.
- Trên 37 tin có cả giờ đăng và giờ thấy, kiểm tra độ nhạy theo đồng hồ:
  - CAR [0, 24] giờ là −0,46% nếu tính từ giờ đăng và −1,02% nếu tính từ giờ GDELT thấy tin.
  - Chỉ đồng hồ "thấy" cho kết quả có ý nghĩa sau Holm.
  - Kiểm định chênh lệch ghép cặp giữa hai đồng hồ không có ý nghĩa (Holm p = 0,201).
- Chưa chạy được VAR/Granger, vì chưa có đoạn ≥ 30 ngày tin liên tục.

*Ý nghĩa:* chọn đồng hồ có thể đổi kết luận về phản ứng giá trong ngày. Đây là minh chứng thực nghiệm cho việc phải báo cáo độ lệch đồng hồ (mục 6.1).

**RQ5: dự báo ngoài mẫu.**
- Có 6.480 dự báo ngoài mẫu.
- Với BTC, mô hình Elastic Net thị trường + văn bản dự báo RV một ngày tới đạt R² ngoài mẫu −0,0077 so với trung bình lịch sử, RMSE 0,000509.
- Chưa tính được kiểm định Diebold–Mariano, vì các ngày test có tin còn rời rạc.

*Ý nghĩa:* ở bản chụp này, văn bản chưa giúp dự báo biến động BTC tốt hơn trung bình lịch sử. Kết luận cho RQ5 cần đoạn test liên tục.

**Tóm lại, ở giai đoạn sơ bộ:** FinBERT đo giọng điệu tốt hơn từ điển (RQ1). Việc chọn đồng hồ ảnh hưởng đến kết luận về phản ứng giá (RQ4). Các câu hỏi về độ lớn tác động (RQ2, RQ3, RQ5) chưa có bằng chứng có ý nghĩa. Điều này phù hợp với quan điểm thị trường hiệu quả ở tần suất ngày (Fama, 1970), nhưng cần kiểm tra lại khi mẫu đầy đủ.

## 7. Thảo luận

Kết quả đo lường có hai hàm ý cho các nghiên cứu dùng dữ liệu tin tức crypto. Thứ nhất, ngày trong cơ sở dữ liệu tin không phải lúc nào cũng là ngày công bố. Với khoảng một phần sáu số tin, chênh lệch đủ lớn để đổi ngày. Một nghiên cứu gán ngày theo giờ đăng mà không kiểm tra văn bản có bị sửa sau đó không sẽ có nguy cơ đưa thông tin tương lai vào chỉ số. Một nghiên cứu gán ngày theo giờ thấy thì làm trễ tín hiệu. Báo cáo cả hai độ lệch giúp người đọc đánh giá chiều sai lệch.

Thứ hai, với tiêu đề ngắn, lợi thế của transformer so với từ điển không nằm ở độ tinh tế mà ở độ phủ: từ điển không phân định được phần lớn tiêu đề. Điều này khớp với lập luận của Loughran và McDonald (2011) rằng công cụ đo phải phù hợp với loại văn bản.

## 8. Hạn chế của nghiên cứu

1. **Lấy mẫu GDELT.** Mới dùng lô :00 mỗi giờ, khoảng 25% số bài. Lấy mẫu theo thời gian nên không chọn lệch theo nội dung, nhưng làm giảm số tin mỗi ngày và tăng nhiễu cho mã coin ít tin.
2. **Kiểm chứng giờ đăng.** Mới làm được trên 42 cặp, vì phần lớn trang không công bố giờ đăng kèm múi giờ hoặc chặn robot. Ước lượng độ lệch do đó còn rộng.
3. **Chất lượng nhãn yếu.** Phiếu CryptoPanic phản ánh kỳ vọng giá của người dùng nền tảng, có thể lệch về phía lạc quan (81,6% tích cực). Đây không phải đánh giá giọng điệu độc lập.
4. **Narrative định trước.** Tám narrative có thể bỏ sót chủ đề mới nổi. LDA và BERTopic được báo cáo song song để giảm rủi ro này. Văn bản dùng cho narrative chỉ gồm tiêu đề và 500 ký tự đầu, nên sự kiện chính nằm sâu trong bài có thể bị bỏ qua.
5. **Mô hình tiền huấn luyện.** FinBERT huấn luyện trên tin tài chính chung, không riêng crypto. Nguồn gốc dữ liệu huấn luyện của CryptoBERT không công bố theo thời gian, nên nó chỉ dùng trong kiểm định.
6. **Biến kiểm soát.** UCRY là chuỗi tính lại hồi cứu, không có các bản công bố theo thời gian thực, và chỉ phủ đến 2024. Mô hình có UCRY chạy trên đoạn ngắn hơn.
7. **Nhân quả.** Hồi quy dự báo và kiểm định Granger cho thấy quan hệ dẫn trước, không chứng minh tin tức gây ra biến động giá.
8. **Phạm vi.** Mẫu gồm năm tài sản vốn hóa lớn, tin tiếng Anh là chính. Kết quả có thể không áp dụng cho token nhỏ hay cộng đồng ngôn ngữ khác.

## 9. Kết luận

Nghiên cứu xây dựng một quy trình dữ liệu văn bản cho thị trường tiền mã hóa, đặt trọng tâm vào tính đúng thời điểm. Mỗi tin được gán ngày theo thời điểm ra công chúng có kiểm chứng. Văn bản không được lùi ngày qua nửa đêm. Mô hình văn bản chỉ học trên kỳ train. Sai lệch đồng hồ được công bố.

Về đo lường, FinBERT phân biệt tin tốt và tin xấu tốt hơn từ điển và CryptoBERT trên tiêu đề crypto. Các câu hỏi về tác động tới giá (RQ2–RQ5) sẽ được trả lời trên toàn mẫu. Toàn bộ mã nguồn, bảng kết quả và dashboard được công bố để người khác kiểm tra lại.

## Tài liệu tham khảo

Andersen, T. G., & Bollerslev, T. (1998). Answering the skeptics: Yes, standard volatility models do provide accurate forecasts. *International Economic Review, 39*(4), 885–905. https://doi.org/10.2307/2527343

Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. *The Journal of Finance, 59*(3), 1259–1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x

Araci, D. (2019). *FinBERT: Financial sentiment analysis with pre-trained language models* (arXiv:1908.10063). arXiv. https://doi.org/10.48550/arXiv.1908.10063

Baker, M., & Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives, 21*(2), 129–151. https://doi.org/10.1257/jep.21.2.129

Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. *The Journal of Finance, 79*(5), 3105–3147. https://doi.org/10.1111/jofi.13377

Campbell, J. Y., & Thompson, S. B. (2008). Predicting excess stock returns out of sample: Can anything beat the historical average? *The Review of Financial Studies, 21*(4), 1509–1531. https://doi.org/10.1093/rfs/hhm055

Chou, K.-H., Day, M.-Y., & Chiu, C.-L. (2023). Do bitcoin news information flow and return volatility fit the sequential information arrival hypothesis and the mixture of distribution hypothesis? *International Review of Economics & Finance, 88*, 365–385. https://doi.org/10.1016/j.iref.2023.06.021

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics, 138*(1), 291–311. https://doi.org/10.1016/j.jeconom.2006.05.023

Critien, J. V., Gatt, A., & Ellul, J. (2022). Bitcoin price change and trend prediction through Twitter sentiment and data volume. *Financial Innovation, 8*(1), Article 45. https://doi.org/10.1186/s40854-022-00352-7

Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *The Journal of Finance, 66*(5), 1461–1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *The Journal of Finance, 25*(2), 383–417. https://doi.org/10.2307/2325486

Garcia, D., & Schweitzer, F. (2015). Social signals and algorithmic trading of Bitcoin. *Royal Society Open Science, 2*(9), Article 150288. https://doi.org/10.1098/rsos.150288

Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica, 37*(3), 424–438. https://doi.org/10.2307/1912791

Grootendorst, M. (2022). *BERTopic: Neural topic modeling with a class-based TF-IDF procedure* (arXiv:2203.05794). arXiv. https://doi.org/10.48550/arXiv.2203.05794

Gür, Y. E., & Ünal, E. (2026). The impact of news sentiment on the Bitcoin price via machine learning and deep learning-based NLP models. *Journal of Forecasting, 45*(3), 895–923. https://doi.org/10.1002/for.70068

Ider, D., & Lessmann, S. (2022). *Forecasting cryptocurrency returns from sentiment signals: An analysis of BERT classifiers and weak supervision* (arXiv:2204.05781). arXiv. https://doi.org/10.48550/arXiv.2204.05781

Kao, Y.-S., Day, M.-Y., & Chou, K.-H. (2024). A comparison of bitcoin futures return and return volatility based on news sentiment contemporaneously or lead-lag. *The North American Journal of Economics and Finance, 72*, Article 102159. https://doi.org/10.1016/j.najef.2024.102159

Khaksar, E., Biktimirov, E. N., Ayanso, A., & Sokolyk, T. (2026). Bitcoin returns and volume: Uncovering investor sentiment through topic modeling. *International Review of Financial Analysis, 116*, Article 105197. https://doi.org/10.1016/j.irfa.2026.105197

Kraaijeveld, O., & De Smedt, J. (2020). The predictive power of public Twitter sentiment for forecasting cryptocurrency prices. *Journal of International Financial Markets, Institutions and Money, 65*, Article 101188. https://doi.org/10.1016/j.intfin.2020.101188

Kristoufek, L. (2013). BitCoin meets Google Trends and Wikipedia: Quantifying the relationship between phenomena of the Internet era. *Scientific Reports, 3*, Article 3415. https://doi.org/10.1038/srep03415

Liu, Y., & Tsyvinski, A. (2021). Risks and returns of cryptocurrency. *The Review of Financial Studies, 34*(6), 2689–2727. https://doi.org/10.1093/rfs/hhaa113

Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance, 66*(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x

Lucey, B. M., Vigne, S. A., Yarovaya, L., & Wang, Y. (2022). The cryptocurrency uncertainty index. *Finance Research Letters, 45*, Article 102147. https://doi.org/10.1016/j.frl.2021.102147

Nasekin, S., & Chen, C. Y.-H. (2020). Deep learning-based cryptocurrency sentiment construction. *Digital Finance, 2*(1–2), 39–67. https://doi.org/10.1007/s42521-020-00018-y

Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica, 55*(3), 703–708. https://doi.org/10.2307/1913610

Ortu, M., Uras, N., Conversano, C., Bartolucci, S., & Destefanis, G. (2022). On technical trading and social media indicators for cryptocurrency price classification through deep learning. *Expert Systems with Applications, 198*, Article 116804. https://doi.org/10.1016/j.eswa.2022.116804

Shiller, R. J. (2017). Narrative economics. *American Economic Review, 107*(4), 967–1004. https://doi.org/10.1257/aer.107.4.967

Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *The Journal of Finance, 62*(3), 1139–1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x

Walker, C. B. (2024). Going mainstream: Cryptocurrency narratives in newspapers. *International Review of Financial Analysis, 94*, Article 103305. https://doi.org/10.1016/j.irfa.2024.103305
