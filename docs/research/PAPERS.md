# PAPERS.md — tài liệu bổ sung (open access), chi tiết

Tra ngày 2026-10-16. Tiêu chí chọn: (1) có bản toàn văn mở hợp pháp; (2) liên quan trực tiếp tới một RQ hoặc tới phương pháp đề tài dùng (từ điển vs transformer, narrative/topic, lead-lag, dự báo out-of-sample, sự kiện pháp lý). `docs/prompts/04_research.md` (mục R2) không có trong repo, nên tiêu chí trên là tự đặt.

Mức đọc: **TV** = đọc toàn văn; **AB** = chỉ abstract/trang tóm tắt. Phiên bản: VoR = bản in, AAM = bản thảo đã chấp nhận, WP = working paper, preprint = arXiv. Số liệu lấy từ phiên bản ghi ở từng mục; bản in có thể lệch nhỏ. Không có con số nào được ước đoán; chỗ chưa có ghi **[không tìm được]**.

Tóm tắt nhanh:

| # | Bài | RQ | Mức đọc | Bản đã đọc |
|---|---|---|---|---|
| 1 | Kristoufek (2013) | RQ4 | TV | VoR, Scientific Reports (OA) |
| 2 | Garcia & Schweitzer (2015) | RQ4, RQ5 | TV | preprint arXiv:1506.01513v2 (= bản RSOS) |
| 3 | Liu & Tsyvinski (2021) | RQ3, RQ5 | TV | NBER WP w24877 |
| 4 | Nasekin & Chen (2020) | RQ1, RQ5 | TV (một phần) | AAM, Glasgow eprints |
| 5 | Ider & Lessmann (2022) | RQ1, RQ5 | TV | preprint arXiv:2204.05781 |
| 6 | Loginova et al. (2024) | RQ1, RQ3, RQ5 | TV | VoR, Springer (bronze OA) |
| 7 | Ortu et al. (2022) | RQ5 | TV (một phần) | preprint arXiv:2102.08189 |
| 8 | Critien, Gatt & Ellul (2022) | RQ5 | TV (một phần) | VoR, Financial Innovation (OA) |
| 9 | Barjašić & Antulov-Fantulin (2021) | RQ3 (volatility), RQ5 | TV (một phần) | preprint arXiv:2004.00550v2 |
| 10 | Auer & Claessens (2018) | RQ2, RQ3 | TV | VoR HTML, BIS Quarterly Review |
| 11 | Lucey et al. (2022) | RQ3 | AB | abstract OpenAlex; PDF OA (Southampton, Cardiff) bị chặn truy cập tự động |
| 12 | Bybee, Kelly, Manela & Xiu (2024) | RQ3, RQ5 (phương pháp) | TV (một phần) | NBER WP w29344 |
| 13 | Grootendorst (2022) | phương pháp narrative | TV (một phần) | preprint arXiv:2203.05794 |

---

## 1. Kristoufek (2013) — BitCoin meets Google Trends and Wikipedia
- **Nguồn:** Scientific Reports 3, 3415. DOI 10.1038/srep03415. OA gold.
- **Dữ liệu:** Giá BTC từ khoảng 05/2011 đến 30/06/2013. Google Trends theo tuần (113 quan sát) và lượt xem Wikipedia theo ngày (788 quan sát).
- **Phương pháp:** Kiểm định dừng và đồng liên kết Johansen. Google Trends: VAR(1) trên sai phân log, sai số chuẩn HAC. Wikipedia: VECM vì có đồng liên kết.
- **Kết quả:** Quan hệ hai chiều, mỗi chiều có ý nghĩa trong 2 kỳ. Hàm phản ứng cho cú sốc 10% có tổng phản ứng khoảng 2% ở một chiều và 0,8% ở chiều kia; câu chữ trong bài không ghi rõ con số nào thuộc chiều nào, nên không gán. Tác động của mức quan tâm bất đối xứng tuỳ giá đang trên hay dưới xu hướng.
- **Dùng cho đề tài:** Tiền lệ cho RQ4 (attention ↔ giá hai chiều) và cho việc dùng VAR/VECM. Attention ở đây là lượt tìm kiếm, không phải text tin tức.

## 2. Garcia & Schweitzer (2015) — Social signals and algorithmic trading of Bitcoin
- **Nguồn:** Royal Society Open Science 2(9), 150288. DOI 10.1098/rsos.150288. OA gold. Đọc bản arXiv v2 (ghi rõ là bản RSOS).
- **Dữ liệu:** Giá đóng cửa ngày (23:59 GMT, CoinDesk BPI) từ 01/02/2011 đến 31/12/2014. Tweet về Bitcoin hơn 3 năm, cùng lượt tìm kiếm, khối lượng giao dịch và chỉ số dùng Bitcoin. Số tweet: **[không tìm được]**.
- **Phương pháp:** VAR(1) đa biến (tránh dương tính giả của Granger từng cặp). Chia giai đoạn phân tích và giai đoạn leave-out khoảng 1 năm. Backtest chiến lược có tính phí giao dịch.
- **Kết quả:** Phân cực ý kiến và khối lượng giao dịch tăng đi trước giá tăng. Cảm xúc (valence) đi trước phân cực và khối lượng. Chiến lược "Combined" đạt Sharpe trên 1,75 và lợi suất trung bình trên 0,3%/ngày trong giai đoạn leave-out.
- **Dùng cho đề tài:** RQ4 (thứ tự trước–sau giữa tín hiệu xã hội và giá) và RQ5 (đánh giá chiến lược sau phí). Lưu ý: leave-out là giai đoạn giá giảm, chỉ một cửa sổ.

## 3. Liu & Tsyvinski (2021) — Risks and Returns of Cryptocurrency
- **Nguồn:** Review of Financial Studies 34(6), 2689–2727. DOI 10.1093/rfs/hhaa113. Đọc NBER WP w24877 (OA).
- **Dữ liệu:** BTC, XRP (08/2013–05/2018), ETH (08/2015–05/2018). Google search, số bài đăng Twitter có chữ "Bitcoin" (Crimson Hexagon).
- **Phương pháp:** Hồi quy dự báo theo ngày/tuần với các nhân tố crypto (momentum, attention, network, production).
- **Kết quả (bản WP):** +1 độ lệch chuẩn tìm kiếm Google "Bitcoin" → lợi suất 2 tuần tới +2,3%. +1 độ lệch chuẩn số tweet "Bitcoin" → lợi suất 1 tuần tới +2,50%. +1 độ lệch chuẩn tỷ lệ tìm kiếm "Bitcoin hack"/"Bitcoin" (attention tiêu cực) → lợi suất tuần sau −2,75%.
- **Dùng cho đề tài:** Biến kiểm soát bắt buộc ở RQ5: momentum và attention thô. Text chỉ có giá trị gia tăng nếu vượt qua các biến này. Attention tiêu cực ("hack") gần với narrative security/hacks của đề tài (RQ3).

## 4. Nasekin & Chen (2020) — Deep learning-based cryptocurrency sentiment construction
- **Nguồn:** Digital Finance 2, 39–67. DOI 10.1007/s42521-020-00018-y. Đọc AAM (Glasgow eprints 214034). Bản WP: IRTG 1792 DP 2018-066.
- **Dữ liệu:** Khoảng 1,22 triệu tin StockTwits về 425 đồng crypto, 03/2013–05/2018.
- **Phương pháp:** Mở rộng từ điển hạt giống bằng word embeddings và mạng nơ-ron hồi quy (recursive NN). So với chỉ số chỉ dùng từ hạt giống. Hồi quy dự báo trong mẫu và ngoài mẫu (cửa sổ ước lượng 1 năm, dự báo đệ quy, R² ngoài mẫu kiểu Welch–Goyal; giai đoạn ngoài mẫu 08/2015–05/2018).
- **Kết quả:** Chỉ số sentiment xây được có thông tin cho dự báo lợi suất và biến động của chỉ số thị trường crypto. Con số R² ngoài mẫu cụ thể: **[không tìm được]** trong phần đã đọc.
- **Dùng cho đề tài:** RQ1 (từ điển gốc vs mở rộng bằng học sâu) và RQ5 (cách đánh giá R² ngoài mẫu đệ quy).

## 5. Ider & Lessmann (2022) — Forecasting cryptocurrency returns from sentiment signals: BERT classifiers and weak supervision
- **Nguồn:** arXiv:2204.05781 (preprint). Bản đăng tạp chí: **[không tìm được]**.
- **Dữ liệu:** BTC và ETH; tin CoinDesk + Cointelegraph (trung bình khoảng 20 bài/ngày/đồng), tweet và bài Reddit, 01/08/2019–15/02/2022.
- **Phương pháp:** Gán nhãn yếu bằng zero-shot BART, rồi fine-tune BERT trên corpus crypto. So với FinBERT trên Financial PhraseBank. Chia theo thời gian: train 01/08/2019–31/07/2021, test 01/08/2021–15/02/2022. Mô phỏng giao dịch phí 0,2%/lệnh, 14 cửa sổ 60 ngày.
- **Kết quả:** Trên test PhraseBank: FinBERT accuracy 0,822, F1 macro 0,805; BART zero-shot 0,790/0,773; BERT fine-tune bằng nhãn yếu 0,789/0,761. Đặc trưng sentiment cải thiện độ chính xác dự báo ở nhiều mô hình; vài mô hình có sentiment cho lợi nhuận dương sau phí.
- **Dùng cho đề tài:** RQ1 (transformer, zero-shot, fine-tune trên miền crypto) và RQ5 (chia mẫu theo thời gian, tính phí). Không so với từ điển LM/Harvard.

## 6. Loginova, Tsang, van Heijningen, Kerkhove & Benoit (2024) — Directional bitcoin returns with aspect-based sentiment
- **Nguồn:** Machine Learning 113(7), 4761–4784. DOI 10.1007/s10994-021-06095-3. Online 18/11/2021. OA bronze.
- **Dữ liệu:** 768 ngày, 20/02/2017–06/04/2019. Reddit 2.637.346 bình luận; Bitcointalk 1.643.314 bình luận; CryptoCompare 79.768 tiêu đề tin. Kèm Google Trends và biến tài chính.
- **Phương pháp:** So đặc trưng text: VADER (polarity), LDA + VADER, và mô hình topic–sentiment đồng thời (JST, TS-LDA). Nhiều bộ phân loại (NB, LR, SVM, RF, MLP, LSTM…). Thước đo chính ROC AUC.
- **Kết quả:** Ghép LDA với polarity VADER không cải thiện. JST cho mức tăng ổn định nhất: AUC từ 0,51 lên 0,58 (MLP, Bitcointalk). Mô hình text nâng cao tăng AUC ít nhất 3 điểm phần trăm so với baseline.
- **Dùng cho đề tài:** RQ1 và RQ3 (topic × sentiment cùng lúc tốt hơn ghép rời). Nhắc phải báo cáo AUC và cân bằng lớp, không chỉ accuracy.

## 7. Ortu, Uras, Conversano, Bartolucci & Destefanis (2022) — Technical trading and social media indicators
- **Nguồn:** Expert Systems with Applications 198, 116804. DOI 10.1016/j.eswa.2022.116804. Đọc preprint arXiv:2102.08189; AAM ở Brunel (BURA 2438/24269).
- **Dữ liệu:** BTC, ETH, Bitfinex, 01/01/2017–01/01/2021 (35.638 quan sát giờ). Sentiment/cảm xúc từ bình luận GitHub và Reddit cùng giai đoạn.
- **Phương pháp:** Mô hình học sâu phân loại hướng giá; so mô hình hạn chế (chỉ biến kỹ thuật) với mô hình đầy đủ (thêm chỉ báo giao dịch và mạng xã hội), tần suất giờ và ngày.
- **Kết quả:** Mô hình đầy đủ tốt hơn mô hình hạn chế một cách nhất quán trên mọi thuật toán. Con số accuracy cụ thể: **[không tìm được]** trong phần đã đọc.
- **Dùng cho đề tài:** RQ5 — đúng thiết kế "market-only vs market+text". Đề tài thêm kiểm định Diebold–Mariano để biến so sánh này thành kiểm định thống kê.

## 8. Critien, Gatt & Ellul (2022) — Bitcoin price change and trend prediction through Twitter sentiment and volume
- **Nguồn:** Financial Innovation 8, 45. DOI 10.1186/s40854-022-00352-7. OA.
- **Dữ liệu:** Bộ tweet Kaggle (hơn 20 triệu tweet, 01/2016–03/2019) lọc "bitcoin"/"btc"; sau làm sạch còn 30/08/2018–23/11/2019.
- **Phương pháp:** Sentiment tweet + số lượng tweet; BiLSTM và CNN dự báo hướng giá; thêm mô hình phân loại nhiều lớp cho độ lớn thay đổi.
- **Kết quả:** Hướng giá: accuracy tối đa 64,18% (BiLSTM 2 lớp, độ trễ 1 ngày, 7 ngày đặc trưng trễ). Độ lớn thay đổi: khoảng 63% theo abstract.
- **Dùng cho đề tài:** RQ5, làm mốc độ chính xác dự báo hướng. Không có kiểm định so với mô hình chỉ có biến thị trường.

## 9. Barjašić & Antulov-Fantulin (2021) — Time-varying volatility in Bitcoin and information flow at minute level
- **Nguồn:** Frontiers in Physics 9, 644102. DOI 10.3389/fphy.2021.644102. OA gold. Đọc arXiv:2004.00550v2.
- **Dữ liệu:** Lợi suất phút BTC (Bitfinex) 18/04/2019–30/05/2019: 58.000 quan sát (50.000 trong mẫu, 8.000 ngoài mẫu); thêm hai giai đoạn kiểm tra (38.000 và 52.000 quan sát). Tín hiệu ngoài: số tweet về Bitcoin, khối lượng giao dịch, spread.
- **Phương pháp:** Họ GARCH với biến ngoại sinh (GARCHX) theo giả thuyết hỗn hợp phân phối (MDH). So log-likelihood ngoài mẫu, kiểm định Kolmogorov–Smirnov.
- **Kết quả:** GARCH(1,1) và cGARCH(1,1) cải thiện rõ nhất khi thêm tín hiệu ngoài, trên dữ liệu ngoài mẫu.
- **Dùng cho đề tài:** RQ3 (volatility là biến mục tiêu) và RQ5 (đánh giá ngoài mẫu). Cùng khung MDH với Chou et al. (2023) và Kao et al. (2024).

## 10. Auer & Claessens (2018) — Regulating cryptocurrencies: assessing market reactions
- **Nguồn:** BIS Quarterly Review, 09/2018, bắt đầu tr. 51 (trang cuối: **[không tìm được]**). OA (bis.org). SSRN 3288097.
- **Dữ liệu:** 151 tin pháp lý (Reuters), 01/2015–06/2018, từ 14 quốc gia/vùng + EU và tổ chức quốc tế. Giá BTC và 6 đồng khác (ETH, BCH, LTC, XMR, ZEC, XRP).
- **Phương pháp:** Event study: cửa sổ 5–120 phút quanh tin, 24 giờ, và 10 ngày (−2 đến +8). Winsorize 5–95%.
- **Kết quả:** Tin thuận lợi: BTC +0,33% (120 phút), +1,52% (24 giờ). Tin bất lợi: −0,32% và −3,12%. Lệnh cấm và xếp vào luật chứng khoán gây giảm mạnh nhất; khuôn khổ pháp lý riêng gây tăng. Cảnh báo chung không có tác động có ý nghĩa.
- **Dùng cho đề tài:** RQ3 (narrative regulation là phân loại con có ý nghĩa: cấm ≠ khuôn khổ) và RQ2 (tin bất lợi 24 giờ khoảng gấp đôi tin thuận lợi về độ lớn). Gợi ý tách narrative regulation theo hướng tác động.

## 11. Lucey, Vigne, Yarovaya & Wang (2022) — The cryptocurrency uncertainty index
- **Nguồn:** Finance Research Letters 45, 102147. DOI 10.1016/j.frl.2021.102147. OA hybrid; AAM ở Southampton (eprints 449566) và Cardiff (ORCA 159764).
- **Dữ liệu:** Tin trên LexisNexis News & Business (theo slide hội nghị AEA 2022 của tác giả). Giai đoạn và số bài: **[không tìm được]** (PDF bị chặn truy cập tự động).
- **Phương pháp:** Chỉ số dạng Baker–Bloom–Davis, đếm bài theo tuần, chuẩn hoá. Hai thành phần: UCRY Price và UCRY Policy.
- **Kết quả:** Chỉ số có biến động rõ quanh các sự kiện lớn của thị trường crypto; tác giả công bố dữ liệu chỉ số.
- **Dùng cho đề tài:** RQ3 — mốc so sánh cho narrative regulation và macro (UCRY Policy) và biến kiểm soát cho độ bất định chung.

## 12. Bybee, Kelly, Manela & Xiu (2024) — Business news and business cycles
- **Nguồn:** Journal of Finance 79(5), 3105–3147. DOI 10.1111/jofi.13377. Đọc NBER WP w29344.
- **Dữ liệu:** Khoảng 800.000 bài Wall Street Journal, 1984–2017.
- **Phương pháp:** LDA; mô hình 180 chủ đề là tối ưu theo tiêu chí Bayes factor. Đo tỷ trọng chú ý của tin theo chủ đề; VAR có thêm text.
- **Kết quả:** Tỷ trọng chú ý theo chủ đề bám sát hoạt động kinh tế và dự báo được lợi suất thị trường cổ phiếu; text đóng góp gia tăng lớn trong dự báo vĩ mô.
- **Dùng cho đề tài:** Khuôn mẫu phương pháp cho "narrative attention" = tỷ trọng chủ đề theo ngày (RQ3) và VAR có text (RQ4/RQ5). Không phải dữ liệu crypto.

## 13. Grootendorst (2022) — BERTopic
- **Nguồn:** arXiv:2203.05794 (preprint). OA.
- **Phương pháp:** Embedding transformer → giảm chiều → phân cụm → biểu diễn chủ đề bằng c-TF-IDF.
- **Kết quả:** Chủ đề mạch lạc, cạnh tranh với mô hình chủ đề cổ điển và mô hình phân cụm trên nhiều bộ benchmark.
- **Dùng cho đề tài:** Phương pháp "advanced" của trích narrative (blueprint 2.4). Với point-in-time: chỉ fit trên dữ liệu trước `split.valid_end`, rồi transform phần test.

---

## Năm bài lõi: tình trạng toàn văn (cập nhật 2026-10-16)

| Bài | OA? (OpenAlex/Unpaywall) | Bản đã đọc | Ghi chú |
|---|---|---|---|
| Chou, Day & Chiu (2023) | Đóng | abstract | Kho TKU (tkuir 987654321/125192) chỉ có metadata |
| Walker (2024) | Có, CC BY (hybrid) | **VoR toàn văn**, QUB Pure | Đã điền đủ |
| Kao, Day & Chou (2024) | Đóng | abstract | Không thấy preprint |
| Gür & Ünal (2026) | Có (hybrid, Wiley) | abstract | PDF Wiley bị captcha; kho Firat (hdl 11508/59850) không có file |
| Khaksar et al. (2026) | Có, CC BY (hybrid) | **Luận văn ThS Brock 2023** của tác giả đầu | Bản in ScienceDirect bị chặn truy cập tự động |

Để điền nốt: tải PDF thủ công vào `paper/sources/` (đã gitignore). Ưu tiên: Gür & Ünal (OA), Khaksar et al. bản in (OA), rồi Chou và Kao nếu có quyền truy cập thư viện.
