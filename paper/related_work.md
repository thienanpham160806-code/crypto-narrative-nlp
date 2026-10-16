# Tổng quan tài liệu (Related work)

Phạm vi: 7 tài liệu ở mục 5 của `docs/blueprint.md`. Mỗi bài tóm tắt theo 4 ý: dữ liệu, phương pháp, kết quả, liên quan RQ nào.
RQ1 transformer vs từ điển · RQ2 bất đối xứng âm/dương · RQ3 narrative nào quan trọng · RQ4 text dẫn hay theo giá · RQ5 cải thiện dự báo out-of-sample.

Mức đọc (để không suy diễn quá dữ liệu):
- Đọc full text: Araci (2019) (bản arXiv), Kraaijeveld & De Smedt (2020) (accepted manuscript R2, kho Edinburgh), Walker (2024) (bản in, CC BY, kho QUB).
- Đọc bản luận văn thay cho bản in: Khaksar et al. (2026), qua luận văn thạc sĩ Brock University 2023 của tác giả đầu. Bản in CC BY có trên ScienceDirect nhưng bị chặn truy cập tự động.
- **Giữ mức abstract-only (quyết định 2026-10-16):** Chou et al. (2023), Kao et al. (2024), Gür & Ünal (2026). Lý do:
  - Chou và Kao: bản đóng (Elsevier), OpenAlex/Unpaywall báo closed, không có preprint hay bản tác giả công khai.
  - Gür & Ünal: Wiley ghi OA nhưng trang PDF chặn bằng captcha, không tải tự động được.
  - Cả ba chỉ dùng làm bằng chứng định tính (hướng tác động, loại mô hình). Không lấy con số của họ làm mốc so sánh định lượng. Kết luận của đề tài không phụ thuộc vào chi tiết chưa đọc.
- Chi tiết không tìm được ghi rõ là **[không tìm được]**. Không có con số nào được ước đoán.
- Tài liệu bổ sung (13 bài open access) ở cuối file; chi tiết từng bài trong `docs/research/PAPERS.md`.

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
- **Toàn văn:** không có bản mở. OpenAlex và Unpaywall ghi "closed"; kho Đại học Tamkang (tkuir 987654321/125192) chỉ có metadata.

## 4. Walker (2024) — Narrative crypto trên báo chí chính thống

- **Dữ liệu (bản in, đọc toàn văn):** LexisNexis, từ khoá "bitcoin", 5 báo: Financial Times (3.464 bài), New York Times (2.395), The Times London (1.765), Daily Mail (400), USA Today (214). Tổng 8.298 bài, 05/2011–06/2022. Sau khi bỏ bài dưới 100 từ, bài trùng và mục không phù hợp, còn 5.775 bài (1.414.959 từ, 6.411 từ riêng) đưa vào mô hình. Giá BTC/USD của Bitfinex lấy qua Investing.com.
- **Phương pháp:** Structural Topic Model (Roberts, Stewart & Tingley), 5 chủ đề, tên báo là covariate. Narrative = tỷ trọng chủ đề trung bình theo ngày. Hồi quy lợi suất log BTC tuần tới theo narrative ngày t−1. Phần chữ ghi kỳ hạn 7 ngày, chú thích Bảng 6–7 ghi 5 ngày. Kiểm soát: lợi suất trễ BTC, vàng, FTSE 100; tỷ giá USD/EUR; lợi suất TPCP Mỹ 5 năm; chỉ số hàng hoá Bloomberg; hiệu ứng cố định năm thuế; sai số chuẩn robust. Bài gán theo ngày đăng. Sentiment LM (tỷ lệ từ tích cực, có xử lý phủ định) chỉ để đối chiếu.
- **Kết quả:** Giai đoạn 2016–2022, narrative tội phạm đi kèm lợi suất tuần sau cao hơn: hệ số 0,088–0,094 (p < 1%) ở cả hai cách xử lý ngày không có tin (Bảng 7). Toàn mẫu 2011–2022, tội phạm không có ý nghĩa. Narrative văn hoá/chính trị cho hệ số âm, từ −0,040 đến −0,062 (p < 5%). Bố cục bảng trong PDF không cho gán chắc từng hệ số vào từng hàng. Số bài thay đổi không dự báo lợi suất. Ngược lại, lợi suất tháng trước dự báo số bài tháng này: lượng tin phản ứng theo giá. Sentiment LM có ý nghĩa ở mẫu chính nhưng mất ý nghĩa khi bỏ hoặc điền ngày không có tin. Kết quả narrative bền khi đổi số chủ đề (4, 6) và dùng dữ liệu tháng. Kiểm định giả: narrative không dự báo lợi suất cổ phiếu hay vàng.
- **Liên quan:** **RQ3** trực tiếp (narrative nào liên quan lợi suất). **RQ4**: lượng tin theo giá, nhưng narrative thì không. **RQ1** gián tiếp: sentiment từ điển kém bền hơn narrative. Là tiền lệ dùng topic model cho narrative, ứng với benchmark LDA của đề tài. Khác biệt: Walker dùng báo in, mỗi narrative đo bằng tỷ trọng chủ đề chứ không kết hợp với sentiment, và không đánh giá ngoài mẫu.

## 5. Kao, Day & Chou (2024) — Hợp đồng tương lai Bitcoin: tin đồng thời hay lead-lag

- **Dữ liệu:** 41.040 tin về Bitcoin futures từ 1.408 website. Biến thị trường là chỉ số Bitcoin futures của CME. Giai đoạn mẫu: **[không tìm được]** (có bao gồm COVID-19).
- **Phương pháp:** NLP chấm sentiment tin (mô hình cụ thể **[không tìm được]**). Threshold GJR-GARCH(1,1) với sentiment dương và âm tách riêng, cùng ngày và trễ.
- **Kết quả:** Tin tiêu cực tác động lên lợi suất ngắn hạn, trái với dạng yếu của EMH. Tin tích cực tác động lên biến động cùng ngày (khớp MDH). Cả tin dương và âm tác động lên biến động các ngày sau (khớp SIAH). COVID-19 làm tăng đáng kể nhu cầu futures vì phòng hộ và đầu cơ.
- **Liên quan:** **RQ2** (tách β⁻ và β⁺), **RQ4** (đồng thời vs trễ), volatility trong **RQ3**.
- **Toàn văn:** không có bản mở (OpenAlex, Unpaywall: "closed"); không thấy preprint.

## 6. Gür & Ünal (2026) — Sentiment tin tức và giá Bitcoin bằng ML/DL

- **Dữ liệu:** Hơn 650.000 tiêu đề tin tài chính, kèm giá Bitcoin trễ và biến vĩ mô/tài chính. Giai đoạn mẫu: **[không tìm được]**. Online từ 20/11/2025, in ở vol. 45(3).
- **Phương pháp:** Điểm sentiment FinBERT + đặc trưng ngữ nghĩa, đưa vào mô hình ML và DL. Tinh chỉnh siêu tham số bằng Optuna và RandomizedSearchCV. Phân tích độ quan trọng biến, GARCH, kịch bản what-if.
- **Kết quả:** FinBERT-LSTM dự báo chính xác nhất (metric và giá trị cụ thể: **[không tìm được]**). Giá trễ của chính Bitcoin giải thích phần lớn biến động giá; sentiment tin vẫn có ảnh hưởng đáng kể. Phản ứng với tin tiêu cực mạnh hơn rõ rệt so với tin tích cực hoặc trung tính.
- **Liên quan:** **RQ5** (thêm text vào dự báo), **RQ2** (bất đối xứng), **RQ1** (chỉ dùng FinBERT, không đối chứng từ điển). Cách chia train/test, có walk-forward hay không: **[không tìm được]** — cần kiểm tra trước khi so sánh trực tiếp.
- **Toàn văn:** bài OA (hybrid) trên Wiley, nhưng trang PDF bị captcha. Kho Đại học Firat (hdl 11508/59850) chỉ có metadata. Cần tải tay vào `paper/sources/` để điền các ô còn trống.

## 7. Khaksar, Biktimirov, Ayanso & Sokolyk (2026) — Topic modeling trên Bitcointalk

Tác giả đầy đủ (Crossref): Ehsan Khaksar, Ernest N. Biktimirov, Anteneh Ayanso, Tatyana Sokolyk.

Chi tiết dưới đây lấy từ **luận văn thạc sĩ** của Khaksar (Brock University, 2023; Biktimirov hướng dẫn, Ayanso và Sokolyk trong hội đồng). Luận văn là bản tiền thân; bản in 2026 có thể khác về mẫu và ước lượng.

- **Dữ liệu:** Mục "Bitcoin Discussion" trên Bitcointalk, thu bằng Scrapy từ 22/11/2009 đến 25/09/2022. Sau làm sạch còn 2.165.505 bình luận; dùng 1.954.166 bình luận sau 04/04/2013. Mẫu ước lượng 18/09/2014–25/09/2022, gồm 2.927 quan sát ngày. Giá và khối lượng lấy từ Yahoo Finance (dữ liệu CoinMarketCap). Biến kiểm soát: S&P 500, vàng, USD/EUR, VIX (Bloomberg) và Google Trends. Số bài và giai đoạn của bản in: **[không tìm được]**.
- **Phương pháp:** LDA, có so với LSA, JST và TSM. Chọn 8 chủ đề trong khoảng 5–15 bằng đọc tay; 2/4 thước đo coherence (C_UCI, C_NPMI) cũng chọn 8. Tám chủ đề: Mining, Regulation, Investment/trading, Public perception, Bitcoin's nature, Wallet, Payment, Other. Sentiment dùng VADER bổ sung từ điển LM. Sentiment theo chủ đề = sentiment của bài × trọng số chủ đề trong bài. Disagreement = độ lệch chuẩn sentiment trong ngày, đại diện độ bất định. Hype đại diện mức chú ý. Ước lượng bằng OLS đồng thời, ARDL và hồi quy phân vị. Ước lượng trong bản in: **[không tìm được xác nhận]**.
- **Kết quả:** Chỉ sentiment và disagreement của chủ đề Investment/trading có quan hệ đồng thời có ý nghĩa với lợi suất. Mining và Wallet chỉ có ý nghĩa ở hai đuôi phân phối lợi suất (thị trường tăng/giảm mạnh); bản in nêu Regulation và Wallet. Sentiment, disagreement và hype của mọi chủ đề liên quan đến khối lượng trên toàn phân phối. Hype tương quan dương với khối lượng khi thị trường ít giao dịch, âm khi khối lượng cao. Quan hệ có thể trễ tới 6 ngày.
- **Liên quan:** **RQ3** (narrative × sentiment × attention với return và volume), **RQ2** (hiệu ứng khác nhau ở đuôi tăng/giảm). Gần nhất với thiết kế chỉ số narrative của đề tài. Khác biệt: chủ đề sinh tự động trên diễn đàn, không có đánh giá ngoài mẫu.

---

## Bảng so sánh

| Bài | Tài sản | Nguồn text | Đo text | Biến mục tiêu | Phương pháp chính | Từ điển vs transformer | Bất đối xứng | Hai chiều text↔giá | Out-of-sample |
|---|---|---|---|---|---|---|---|---|---|
| Araci (2019) | — (cổ phiếu/tài chính) | Reuters, PhraseBank, FiQA | FinBERT | Nhãn sentiment | Phân loại, fine-tune | So với ML/DL, không so với LM | — | — | Có (test set/CV, phân loại) |
| Kraaijeveld & De Smedt (2020) | 9 coin | Twitter | Từ điển VADER+LM+crypto | Return, volume | Granger T&Y | Chỉ từ điển | Không | Có | Không |
| Chou et al. (2023) | BTC spot | 64 website tin | NLP sentiment (không rõ mô hình) | Volatility | VAR, Spearman | Không rõ | Có (âm SIAH, dương MDH) | Lead-lag VAR | Không thấy trong abstract |
| Walker (2024) | BTC | 5 báo chính thống (LexisNexis) | STM, 5 narrative; LM để đối chiếu | Return tuần tới | Hồi quy dự báo, SE robust | Không (LM chỉ để đối chiếu) | Không | Có (lợi suất → lượng tin) | Không |
| Kao et al. (2024) | BTC futures CME | 1.408 website tin | NLP sentiment (không rõ mô hình) | Return, volatility | Threshold GJR-GARCH | Không rõ | Có | Đồng thời vs trễ | Không thấy trong abstract |
| Gür & Ünal (2026) | BTC | 650k+ tiêu đề tin | FinBERT + semantic | Giá | ML/DL, FinBERT-LSTM | Chỉ transformer | Có | Không thấy trong abstract | Có (chi tiết chia mẫu không rõ) |
| Khaksar et al. (2026)* | BTC | Bitcointalk | LDA 8 chủ đề × sentiment (VADER+LM), disagreement, hype | Return, volume | OLS, ARDL, hồi quy phân vị | Chỉ từ điển | Có (đuôi tăng/giảm) | Không rõ | Không |
| **Đề tài này** | BTC, ETH (+ coin lớn) | News EN (GDELT, RSS, SEC…) + tin VN | LM, Harvard IV-4, FinBERT; VietScorer; LDA → BERTopic → zero-shot | Return, RV, volume | OLS HAC, Wald β⁻=β⁺, VAR/Granger 2 chiều, walk-forward + DM, SHAP | **So sánh trực tiếp** | Wald chính thức | Có, theo từng narrative | Walk-forward, point-in-time |

"Không thấy trong abstract" nghĩa là chưa đọc được full text, không có nghĩa bài đó chắc chắn không làm. (*) Khaksar et al.: theo luận văn 2023, chưa đối chiếu với bản in.

**Nghĩa là gì:** Bằng chứng hiện có đồng thuận rằng text crypto có thông tin, và tin xấu có tác động khác tin tốt. Nhưng mỗi bài chỉ trả lời một mảnh: hoặc sentiment tổng (Chou, Kao, Gür), hoặc narrative (Walker, Khaksar), hoặc lead-lag in-sample (Kraaijeveld). Chưa bài nào gộp các mảnh này trên cùng một corpus có kiểm soát timestamp.

---

## Khoảng trống nghiên cứu mà đề tài lấp

1. **So sánh từ điển và transformer trên cùng corpus crypto, cùng biến mục tiêu (RQ1).** Kraaijeveld chỉ dùng từ điển. Gür & Ünal chỉ dùng FinBERT. Chou và Kao không nêu mô hình trong abstract. Trong tài liệu bổ sung, các so sánh đã có nằm ngoài khung hồi quy dự báo kinh tế lượng. Nasekin & Chen so từ điển hạt giống với từ điển mở rộng bằng học sâu. Loginova et al. so VADER với mô hình topic–sentiment đồng thời. Ider & Lessmann so FinBERT với BERT fine-tune bằng nhãn yếu. Trong các bài đã đọc, chưa bài nào đặt LM/Harvard và FinBERT cạnh nhau trong cùng hồi quy dự báo trên tin crypto. Đề tài chấm cùng tài liệu bằng LM, Harvard IV-4 và FinBERT, rồi so sức giải thích gia tăng trên return, RV và volume. Kèm 300 tiêu đề gán tay để đo độ chính xác phân loại trên tin crypto.
2. **Kiểm định bất đối xứng chính thức (RQ2).** Chou, Kao, Gür, Khaksar đều ghi nhận tin âm/dương tác động khác nhau, nhưng qua cơ chế GARCH, VAR hoặc độ quan trọng biến. Đề tài tách β⁻ và β⁺ trong cùng hồi quy dự báo và kiểm định Wald β⁻ = β⁺, cho cả từ điển lẫn FinBERT.
3. **Kết hợp narrative với sentiment ở tần suất ngày (RQ3).** Walker đo narrative theo tỷ trọng chủ đề, không có sentiment. Khaksar có sentiment theo chủ đề nhưng dùng diễn đàn và chủ đề sinh tự động. Đề tài dựng chỉ số ngày theo 8 narrative định trước (regulation, ETF/institutional, hacks, stablecoins, DeFi, AI token, macro, price/speculation), kết hợp attention và sentiment. So ba cách trích narrative: LDA, BERTopic, zero-shot.
4. **Hai chiều nhân quả theo từng narrative (RQ4).** Kraaijeveld cho thấy với nhiều coin, giá dẫn Twitter. Chou và Kao kiểm lead-lag cho sentiment tổng. Đề tài chạy VAR/Granger hai chiều cho từng narrative, để tách narrative dẫn thị trường khỏi narrative chỉ phản ứng theo giá.
5. **Dự báo out-of-sample không rò rỉ thông tin (RQ5).** Trong 7 bài lõi, chỉ Gür & Ünal dự báo bằng ML, và cách chia mẫu chưa rõ. Các bài lõi khác chủ yếu in-sample. Tài liệu bổ sung có đánh giá ngoài mẫu: Garcia & Schweitzer, Nasekin & Chen, Ider & Lessmann, Loginova et al., Ortu et al. Nhưng phần lớn chỉ dùng một lần chia train/test hoặc một cửa sổ leave-out. Nasekin & Chen dự báo đệ quy, nhưng so với trung bình lịch sử, không so với mô hình chỉ có biến thị trường. Trong các bài đã đọc, chưa bài nào làm đủ ba việc: walk-forward, khoá mốc thời gian công bố, và kiểm định Diebold–Mariano với mô hình chỉ có biến thị trường. Mô hình chỉ có biến thị trường cũng phải có momentum và attention thô, vì hai biến này đã dự báo được lợi suất (Liu & Tsyvinski). Đề tài dùng walk-forward, gán ngày bằng `public_ts_utc`, khoá test set khỏi mọi bước tuning (kể cả chọn số topic K và fit BERTopic). So mô hình chỉ có biến thị trường với mô hình thêm text bằng kiểm định Diebold–Mariano. Đánh giá thêm chiến lược tín hiệu sau phí.
6. **Đa tài sản và nhánh tiếng Việt.** 5/6 bài về crypto chỉ xét Bitcoin; Kraaijeveld xét 9 coin nhưng chỉ 2 tháng. Không bài nào dùng tin tiếng Việt. Đề tài xét BTC, ETH và các coin lớn trong ít nhất 2–3 năm, thêm nhánh tin Việt chấm bằng từ điển tiếng Việt (không dịch sang tiếng Anh).

**Nghĩa là gì:** Nếu text chỉ có giá trị in-sample hoặc chỉ phản ứng theo giá, nhà đầu tư không khai thác được nó. Đóng góp chính của đề tài là trả lời câu hỏi đó trên dữ liệu point-in-time, ở cấp từng narrative.

---

## Tài liệu bổ sung theo RQ (open access)

13 bài có toàn văn mở, chọn vì liên quan trực tiếp tới một RQ hoặc tới phương pháp đề tài dùng. Dữ liệu, phương pháp, số liệu và phiên bản đã đọc của từng bài: `docs/research/PAPERS.md`. Một bài có thể phục vụ nhiều RQ; dưới đây xếp theo RQ chính.

**RQ1 — từ điển vs transformer**
- Nasekin & Chen (2020): 1,22 triệu tin StockTwits (425 đồng, 2013–2018). Mở rộng từ điển hạt giống bằng word embeddings và mạng nơ-ron; chỉ số mới có thông tin cho lợi suất và biến động, cả ngoài mẫu.
- Ider & Lessmann (2022, preprint): tin CoinDesk/Cointelegraph, tweet, Reddit cho BTC/ETH (2019–2022). BERT fine-tune bằng nhãn yếu từ zero-shot gần bằng FinBERT trên PhraseBank (accuracy 0,789 so với 0,822), và sentiment cải thiện dự báo.
- Loginova et al. (2024): Reddit, Bitcointalk, CryptoCompare (2017–2019). Topic–sentiment đồng thời (JST) nâng ROC AUC từ 0,51 lên 0,58; ghép LDA với VADER thì không cải thiện.

**RQ2 — bất đối xứng**
- Auer & Claessens (2018): 151 tin pháp lý (2015–2018). Trong 24 giờ, tin bất lợi làm BTC giảm 3,12%, tin thuận lợi làm tăng 1,52%. Lệnh cấm gây giảm mạnh nhất; cảnh báo chung không có tác động.
- Kristoufek (2013): tác động của mức quan tâm (Google, Wikipedia) lên giá khác nhau tuỳ giá đang trên hay dưới xu hướng.

**RQ3 — narrative nào quan trọng, với return, volatility, volume**
- Auer & Claessens (2018): narrative regulation cần tách theo hướng: cấm và luật chứng khoán khác hẳn khuôn khổ pháp lý riêng.
- Liu & Tsyvinski (2021): attention tiêu cực (tỷ lệ tìm kiếm "Bitcoin hack") dự báo lợi suất tuần sau thấp hơn 2,75% cho mỗi độ lệch chuẩn. Kết quả này gần với narrative security/hacks.
- Lucey et al. (2022, chỉ abstract): chỉ số bất định crypto từ tin LexisNexis, tách UCRY Price và UCRY Policy. Là mốc đối chiếu cho narrative regulation/macro.
- Barjašić & Antulov-Fantulin (2021): số tweet, khối lượng và spread cải thiện dự báo biến động phút ngoài mẫu của GARCH(1,1), cGARCH(1,1). Cùng khung MDH với Chou và Kao.
- Bybee et al. (2024): tỷ trọng chú ý theo chủ đề (LDA 180 chủ đề, 800.000 bài WSJ) dự báo lợi suất thị trường. Khuôn mẫu cho cách đo narrative attention.
- Grootendorst (2022, preprint): BERTopic, phương pháp "advanced" của bước trích narrative.

**RQ4 — text dẫn hay theo giá**
- Kristoufek (2013): VAR/VECM cho thấy giá BTC và lượt tìm kiếm tác động hai chiều.
- Garcia & Schweitzer (2015): VAR(1) đa biến; phân cực ý kiến trên Twitter và khối lượng giao dịch đi trước giá tăng, valence đi trước phân cực.

**RQ5 — dự báo out-of-sample**
- Liu & Tsyvinski (2021): momentum và attention thô đã dự báo được lợi suất. Mô hình chỉ có biến thị trường phải gồm hai biến này.
- Ortu et al. (2022): thêm chỉ báo mạng xã hội (GitHub, Reddit) vào biến kỹ thuật cải thiện phân loại hướng giá BTC/ETH ở mọi thuật toán (2017–2021, theo giờ và ngày).
- Garcia & Schweitzer (2015): chiến lược dựa trên tín hiệu xã hội đạt Sharpe trên 1,75 sau phí trong khoảng 1 năm leave-out.
- Ider & Lessmann (2022): chia theo thời gian, mô phỏng giao dịch phí 0,2%; vài mô hình có sentiment có lãi sau phí.
- Critien et al. (2022): BiLSTM trên sentiment và số tweet đạt accuracy hướng giá tối đa 64,18%.

**Nghĩa là gì:** Tài liệu bổ sung củng cố hai điểm. Một: tin bất lợi và tin pháp lý tác động mạnh hơn và khác loại, nên narrative cần tách theo hướng chứ không gộp. Hai: lợi thế dự báo của text thường được đo bằng một lần chia mẫu và so với baseline yếu. Đề tài phải so với baseline mạnh (momentum, attention) bằng kiểm định chính thức.

---

## Nguồn đã tra

- Araci (2019): arXiv:1908.10063 (full text qua ar5iv).
- Kraaijeveld & De Smedt (2020): accepted manuscript, https://www.pure.ed.ac.uk/ws/files/138685006/INTFIN_2018_414_R2.pdf; abstract RePEc. Số liệu có thể lệch nhỏ so với bản in.
- Chou et al. (2023): abstract RePEc `eee/reveco/v88`. OpenAlex/Unpaywall: closed.
- Walker (2024): bản in toàn văn (CC BY), https://pureadmin.qub.ac.uk/ws/files/586392177/Going_mainstream.pdf.
- Kao et al. (2024): abstract RePEc `eee/ecofin/v72`. OpenAlex/Unpaywall: closed.
- Gür & Ünal (2026): abstract RePEc `wly/jforec/v45`, Wiley Online Library. OA nhưng PDF bị captcha.
- Khaksar et al. (2026): highlights ScienceDirect; luận văn thạc sĩ toàn văn, Brock University 2023, https://brocku.scholaris.ca/handle/10464/17762.
- DOI, số trang và tên tác giả của 7 bài lõi đã đối chiếu với Crossref API (`api.crossref.org/works/<DOI>`) ngày 2026-10-16. Gür & Ünal: Crossref ghi ngày online 20/11/2025, in vol. 45(3) năm 2026.

Các ô **[không tìm được]** của Chou, Kao, Gür & Ünal được giữ nguyên có chủ đích (xem mục "Mức đọc"). Còn mở: đối chiếu Khaksar với bản in.
