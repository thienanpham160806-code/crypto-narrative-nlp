# Tổng quan tài liệu (Related work)

Phạm vi: 7 tài liệu ở mục 5 của `docs/blueprint.md`. Mỗi bài tóm tắt theo 4 ý: dữ liệu, phương pháp, kết quả, liên quan RQ nào.
RQ1 transformer vs từ điển · RQ2 bất đối xứng âm/dương · RQ3 narrative nào quan trọng · RQ4 text dẫn hay theo giá · RQ5 cải thiện dự báo out-of-sample.

Mức đọc (để không suy diễn quá dữ liệu):
- Đọc full text: Araci (2019) (bản arXiv), Kraaijeveld & De Smedt (2020) (accepted manuscript R2, kho Edinburgh).
- Chỉ đọc abstract + metadata (full text bị paywall hoặc chặn truy cập tự động): 5 bài còn lại.
- Chi tiết không tìm được ghi rõ là **[không tìm được]**. Không có con số nào được ước đoán.

---

## 1. Araci (2019) — FinBERT

- **Dữ liệu:** Tiếp tục pre-train BERT trên TRC2-financial (46.143 tài liệu Reuters 2008–2010, khoảng 29 triệu từ). Fine-tune và đánh giá trên Financial PhraseBank (4.845 câu, tập con đồng thuận 100% gồm 2.262 câu) và FiQA Task 1 (1.174 tiêu đề/tweet, điểm sentiment liên tục).
- **Phương pháp:** BERT-base + further pre-training theo miền tài chính, fine-tune phân loại 3 lớp; so với LSTM, ELMo, ULMFit, FinSSLX.
- **Kết quả:** PhraseBank toàn bộ: accuracy 0,86 và F1 0,84 (ULMFit: 0,83 và 0,79). Tập đồng thuận 100%: accuracy 0,97, F1 0,95 (ULMFit: 0,93 và 0,91). FiQA: MSE 0,07, R² 0,55 (baseline tốt nhất R² 0,41). Kết quả FiQA dùng 10-fold CV, baseline dùng test set chính thức, nên so sánh không hoàn toàn tương đương.
- **Liên quan:** Mô hình transformer của nhánh tiếng Anh (đã port sẵn trong repo). Đối chứng trực tiếp với LM/Harvard IV-4 cho **RQ1**. Lưu ý: FinBERT huấn luyện trên tin tài chính truyền thống, không phải tin crypto — sai lệch miền là một phần câu hỏi RQ1.

## 2. Kraaijeveld & De Smedt (2020) — Twitter sentiment và giá crypto

- **Dữ liệu:** 24.035.075 tweet (22.912.039 sau tiền xử lý) về 9 đồng crypto lớn nhất (BTC, ETH, XRP, BCH, EOS, LTC, ADA, XLM, TRX), từ 04/06/2018 đến 04/08/2018. Giá từ CoinMarketCap, tần suất ngày và giờ.
- **Phương pháp:** Từ điển VADER mở rộng bằng từ LM (2016) và 63 từ lóng/viết tắt crypto tự xây. Tính sentiment trung bình, tỷ lệ bullishness, khối lượng tin nhắn. Kiểm định Granger song phương (Toda–Yamamoto, đối chiếu Johansen). Lọc bot bằng heuristic.
- **Kết quả:** Sentiment dự báo được lợi suất BTC, BCH, LTC. Bullishness dự báo được EOS, TRX. Với nhiều đồng còn lại, lợi suất dẫn khối lượng tin nhắn, tức Twitter phản ứng theo giá. Ước tính ít nhất 1–14% tweet do bot đăng.
- **Liên quan:** **RQ4** (Granger hai chiều, bằng chứng chiều ngược giá → text). Baseline từ điển cho **RQ1**. Hạn chế mà đề tài khắc phục: mẫu chỉ 2 tháng, chỉ in-sample, chỉ có từ điển.

## 3. Chou, Day & Chiu (2023) — Luồng tin Bitcoin và biến động (SIAH vs MDH)

- **Dữ liệu:** 24.316 tin Bitcoin từ 64 website tin tức. Giai đoạn mẫu: **[không tìm được]**.
- **Phương pháp:** Dùng NLP chấm sentiment để tạo "luồng thông tin" thay cho khối lượng giao dịch (proxy truyền thống). VAR cho quan hệ lead-lag, tương quan Spearman cho quan hệ đồng thời. Mô hình sentiment cụ thể: **[không tìm được]**.
- **Kết quả:** Luồng tin tiêu cực tác động lên biến động lợi suất theo giả thuyết thông tin tuần tự (SIAH, tác động trễ). Luồng tin tích cực khớp giả thuyết hỗn hợp phân phối (MDH, tác động đồng thời). Hệ số cụ thể: **[không tìm được]**.
- **Liên quan:** **RQ2** (tin âm và dương có cơ chế khác nhau), **RQ4** (lead-lag bằng VAR), biến mục tiêu volatility của **RQ3**.

## 4. Walker (2024) — Narrative crypto trên báo chí chính thống

- **Dữ liệu:** Bài báo chính thống viết về Bitcoin, 2011–2022. Tên báo, cơ sở dữ liệu nguồn, số bài: **[không tìm được]**.
- **Phương pháp:** Structural Topic Model (Roberts, Stewart & Tingley) để nhận diện narrative, sau đó hồi quy lợi suất kế tiếp theo tỷ trọng narrative. Tần suất và kỳ hạn hồi quy: **[không tìm được]**.
- **Kết quả:** Tìm được 5 narrative: tội phạm, văn hoá, chính trị, giá, công nghệ. Theo thời gian, giá/chính trị/văn hoá tăng tỷ trọng, công nghệ giảm. Tin mang màu chính trị hoặc văn hoá đi kèm lợi suất sau đó thấp hơn. Narrative tội phạm đi kèm lợi suất cao hơn. Độ lớn hệ số: **[không tìm được]**.
- **Liên quan:** **RQ3** trực tiếp (narrative nào liên quan lợi suất). Là tiền lệ dùng topic model cho narrative, ứng với benchmark LDA của đề tài. Khác biệt: Walker dùng báo in, mỗi narrative đo bằng tỷ trọng chủ đề chứ không kết hợp với sentiment.

## 5. Kao, Day & Chou (2024) — Hợp đồng tương lai Bitcoin: tin đồng thời hay lead-lag

- **Dữ liệu:** 41.040 tin về Bitcoin futures từ 1.408 website. Biến thị trường là chỉ số Bitcoin futures của CME. Giai đoạn mẫu: **[không tìm được]** (có bao gồm COVID-19).
- **Phương pháp:** NLP chấm sentiment tin (mô hình cụ thể **[không tìm được]**). Threshold GJR-GARCH(1,1) với sentiment dương và âm tách riêng, cùng ngày và trễ.
- **Kết quả:** Tin tiêu cực tác động lên lợi suất ngắn hạn, trái với dạng yếu của EMH. Tin tích cực tác động lên biến động cùng ngày (khớp MDH). Cả tin dương và âm tác động lên biến động các ngày sau (khớp SIAH). COVID-19 làm tăng đáng kể nhu cầu futures vì phòng hộ và đầu cơ.
- **Liên quan:** **RQ2** (tách β⁻ và β⁺), **RQ4** (đồng thời vs trễ), volatility trong **RQ3**.

## 6. Gür & Ünal (2026) — Sentiment tin tức và giá Bitcoin bằng ML/DL

- **Dữ liệu:** Hơn 650.000 tiêu đề tin tài chính, kèm giá Bitcoin trễ và biến vĩ mô/tài chính. Giai đoạn mẫu: **[không tìm được]**. Online từ 20/11/2025, in ở vol. 45(3).
- **Phương pháp:** Điểm sentiment FinBERT + đặc trưng ngữ nghĩa, đưa vào mô hình ML và DL. Tinh chỉnh siêu tham số bằng Optuna và RandomizedSearchCV. Phân tích độ quan trọng biến, GARCH, kịch bản what-if.
- **Kết quả:** FinBERT-LSTM dự báo chính xác nhất (metric và giá trị cụ thể: **[không tìm được]**). Giá trễ của chính Bitcoin giải thích phần lớn biến động giá; sentiment tin vẫn có ảnh hưởng đáng kể. Phản ứng với tin tiêu cực mạnh hơn rõ rệt so với tin tích cực hoặc trung tính.
- **Liên quan:** **RQ5** (thêm text vào dự báo), **RQ2** (bất đối xứng), **RQ1** (chỉ dùng FinBERT, không đối chứng từ điển). Cách chia train/test, có walk-forward hay không: **[không tìm được]** — cần kiểm tra trước khi so sánh trực tiếp.

## 7. Khaksar, Biktimirov, Ayanso & Sokolyk (2026) — Topic modeling trên Bitcointalk

- **Dữ liệu:** Thảo luận trên diễn đàn Bitcointalk. Bản luận văn/hội thảo trước đó (Brock University; EFMA 2024) dùng giai đoạn 2013–2022. Giai đoạn của bản đăng tạp chí và số bài viết: **[không tìm được]**.
- **Phương pháp:** Topic modeling tìm 8 chủ đề (bản luận văn ghi LDA, gồm Mining, Regulation, Investment/trading, Public perception, Bitcoin's nature, Wallet, Payment, Other). Mỗi chủ đề có sentiment, độ bất đồng (disagreement), mức chú ý (attention). Kết quả được báo cáo theo từng phần của phân phối lợi suất/khối lượng; tên ước lượng (khả năng là hồi quy phân vị) **[không tìm được xác nhận]**.
- **Kết quả:** Chỉ sentiment và disagreement của chủ đề Investment có quan hệ có ý nghĩa với lợi suất trên toàn mẫu. Regulation, Wallet chỉ có ý nghĩa ở đuôi phân phối lợi suất (thị trường tăng/giảm mạnh). Mọi chủ đề đều liên quan đến khối lượng giao dịch trên toàn phân phối.
- **Liên quan:** **RQ3** (narrative × sentiment × attention với return và volume), **RQ2** (hiệu ứng khác nhau ở đuôi tăng/giảm). Gần nhất với thiết kế chỉ số narrative của đề tài.

---

## Bảng so sánh

| Bài | Tài sản | Nguồn text | Đo text | Biến mục tiêu | Phương pháp chính | Từ điển vs transformer | Bất đối xứng | Hai chiều text↔giá | Out-of-sample |
|---|---|---|---|---|---|---|---|---|---|
| Araci (2019) | — (cổ phiếu/tài chính) | Reuters, PhraseBank, FiQA | FinBERT | Nhãn sentiment | Phân loại, fine-tune | So với ML/DL, không so với LM | — | — | Có (test set/CV, phân loại) |
| Kraaijeveld & De Smedt (2020) | 9 coin | Twitter | Từ điển VADER+LM+crypto | Return, volume | Granger T&Y | Chỉ từ điển | Không | Có | Không |
| Chou et al. (2023) | BTC spot | 64 website tin | NLP sentiment (không rõ mô hình) | Volatility | VAR, Spearman | Không rõ | Có (âm SIAH, dương MDH) | Lead-lag VAR | Không thấy trong abstract |
| Walker (2024) | BTC | Báo chính thống | STM, 5 narrative | Return | Hồi quy | Không | Không | Không thấy trong abstract | Không thấy trong abstract |
| Kao et al. (2024) | BTC futures CME | 1.408 website tin | NLP sentiment (không rõ mô hình) | Return, volatility | Threshold GJR-GARCH | Không rõ | Có | Đồng thời vs trễ | Không thấy trong abstract |
| Gür & Ünal (2026) | BTC | 650k+ tiêu đề tin | FinBERT + semantic | Giá | ML/DL, FinBERT-LSTM | Chỉ transformer | Có | Không thấy trong abstract | Có (chi tiết chia mẫu không rõ) |
| Khaksar et al. (2026) | BTC | Bitcointalk | Topic (LDA) × sentiment/disagreement/attention | Return, volume | Theo phân phối (có thể phân vị) | Không rõ | Có (đuôi tăng/giảm) | Không thấy trong abstract | Không thấy trong abstract |
| **Đề tài này** | BTC, ETH (+ coin lớn) | News EN (GDELT, RSS, SEC…) + tin VN | LM, Harvard IV-4, FinBERT; VietScorer; LDA → BERTopic → zero-shot | Return, RV, volume | OLS HAC, Wald β⁻=β⁺, VAR/Granger 2 chiều, walk-forward + DM, SHAP | **So sánh trực tiếp** | Wald chính thức | Có, theo từng narrative | Walk-forward, point-in-time |

"Không thấy trong abstract" nghĩa là chưa đọc được full text, không có nghĩa bài đó chắc chắn không làm.

**Nghĩa là gì:** Bằng chứng hiện có đồng thuận rằng text crypto có thông tin, và tin xấu có tác động khác tin tốt. Nhưng mỗi bài chỉ trả lời một mảnh: hoặc sentiment tổng (Chou, Kao, Gür), hoặc narrative (Walker, Khaksar), hoặc lead-lag in-sample (Kraaijeveld). Chưa bài nào gộp các mảnh này trên cùng một corpus có kiểm soát timestamp.

---

## Khoảng trống nghiên cứu mà đề tài lấp

1. **So sánh từ điển và transformer trên cùng corpus crypto, cùng biến mục tiêu (RQ1).** Kraaijeveld chỉ dùng từ điển. Gür & Ünal chỉ dùng FinBERT. Chou và Kao không nêu mô hình trong abstract. Đề tài chấm cùng tài liệu bằng LM, Harvard IV-4 và FinBERT, rồi so sức giải thích gia tăng trên return, RV và volume. Kèm 300 tiêu đề gán tay để đo độ chính xác phân loại trên tin crypto.
2. **Kiểm định bất đối xứng chính thức (RQ2).** Chou, Kao, Gür, Khaksar đều ghi nhận tin âm/dương tác động khác nhau, nhưng qua cơ chế GARCH, VAR hoặc độ quan trọng biến. Đề tài tách β⁻ và β⁺ trong cùng hồi quy dự báo và kiểm định Wald β⁻ = β⁺, cho cả từ điển lẫn FinBERT.
3. **Kết hợp narrative với sentiment ở tần suất ngày (RQ3).** Walker đo narrative theo tỷ trọng chủ đề, không có sentiment. Khaksar có sentiment theo chủ đề nhưng dùng diễn đàn và chủ đề sinh tự động. Đề tài dựng chỉ số ngày theo 8 narrative định trước (regulation, ETF/institutional, hacks, stablecoins, DeFi, AI token, macro, price/speculation), kết hợp attention và sentiment. So ba cách trích narrative: LDA, BERTopic, zero-shot.
4. **Hai chiều nhân quả theo từng narrative (RQ4).** Kraaijeveld cho thấy với nhiều coin, giá dẫn Twitter. Chou và Kao kiểm lead-lag cho sentiment tổng. Đề tài chạy VAR/Granger hai chiều cho từng narrative, để tách narrative dẫn thị trường khỏi narrative chỉ phản ứng theo giá.
5. **Dự báo out-of-sample không rò rỉ thông tin (RQ5).** Chỉ Gür & Ünal dự báo bằng ML, nhưng cách chia mẫu chưa rõ. Các bài khác chủ yếu in-sample. Đề tài dùng walk-forward, gán ngày bằng `public_ts_utc`, khoá test set khỏi mọi bước tuning (kể cả chọn số topic K và fit BERTopic). So mô hình chỉ có biến thị trường với mô hình thêm text bằng kiểm định Diebold–Mariano. Đánh giá thêm chiến lược tín hiệu sau phí.
6. **Đa tài sản và nhánh tiếng Việt.** 5/6 bài về crypto chỉ xét Bitcoin; Kraaijeveld xét 9 coin nhưng chỉ 2 tháng. Không bài nào dùng tin tiếng Việt. Đề tài xét BTC, ETH và các coin lớn trong ít nhất 2–3 năm, thêm nhánh tin Việt chấm bằng từ điển tiếng Việt (không dịch sang tiếng Anh).

**Nghĩa là gì:** Nếu text chỉ có giá trị in-sample hoặc chỉ phản ứng theo giá, nhà đầu tư không khai thác được nó. Đóng góp chính của đề tài là trả lời câu hỏi đó trên dữ liệu point-in-time, ở cấp từng narrative.

---

## Nguồn đã tra

- Araci (2019): arXiv:1908.10063 (full text qua ar5iv).
- Kraaijeveld & De Smedt (2020): accepted manuscript, https://www.pure.ed.ac.uk/ws/files/138685006/INTFIN_2018_414_R2.pdf; abstract RePEc. Số liệu có thể lệch nhỏ so với bản in.
- Chou et al. (2023): abstract RePEc `eee/reveco/v88`.
- Walker (2024): abstract Queen's University Belfast Pure, RePEc; phương pháp STM theo đoạn trích ScienceDirect. Full text CC BY có tại QUB nhưng bị chặn truy cập tự động.
- Kao et al. (2024): abstract RePEc `eee/ecofin/v72`.
- Gür & Ünal (2026): abstract RePEc `wly/jforec/v45`, Wiley Online Library.
- Khaksar et al. (2026): highlights ScienceDirect; luận văn Brock University (handle 10464/17762); EFMA 2024 working paper.

Việc cần làm khi có quyền truy cập full text: điền các ô **[không tìm được]** (giai đoạn mẫu, mô hình sentiment, độ lớn hệ số, cách chia train/test).
