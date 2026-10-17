# Narrative và sentiment tin tức crypto: tín hiệu point-in-time cho lợi suất, biến động và khối lượng

*Bản nháp C4 — 2026-10-18. Các số trong mục 3 là số tạm thời: GDELT mới thu 180/1369 ngày (13%). Mục 4 chờ dữ liệu đầy đủ và kết quả mô hình. Mọi chỗ chưa có kết quả ghi **[chờ]**, không ước đoán.*

## 1. Giới thiệu

Giá crypto phản ứng mạnh với narrative: quy định pháp lý, quỹ ETF và dòng tiền tổ chức, vụ hack, stablecoin, DeFi, token AI và chính sách tiền tệ. Câu hỏi của đề tài: chỉ số sentiment, attention và narrative trích từ tin tức có thêm thông tin cho return, volatility và volume, ngoài những gì biến thị trường đã chứa hay không.

Năm câu hỏi nghiên cứu:
- **RQ1.** Transformer (FinBERT) có đo giọng điệu tin crypto tốt hơn từ điển (Loughran–McDonald, Harvard IV-4) không?
- **RQ2.** Tin xấu có tác động khác tin tốt không?
- **RQ3.** Narrative nào liên hệ mạnh nhất với return, volatility và volume?
- **RQ4.** Text dẫn dắt giá, hay giá dẫn dắt text?
- **RQ5.** Text có cải thiện dự báo ngoài mẫu so với mô hình chỉ có biến thị trường không?

Đóng góp chính là phương pháp dữ liệu. Mỗi tin được gán ngày bằng thời điểm ra công chúng có kiểm chứng (`public_ts_utc`). Độ lệch giữa các đồng hồ được đo và công bố theo nguồn. Mọi mô hình text (vectorizer, LDA, BERTopic, ngưỡng) chỉ fit trên kỳ train. Các khoảng trống so với tài liệu hiện có nằm ở `paper/related_work.md`, mục "Khoảng trống nghiên cứu".

## 2. Dữ liệu

### 2.1. Nguồn tin

| Nguồn | Vai trò | Giờ dùng để gán ngày | Ghi chú |
|---|---|---|---|
| GDELT GKG 2.0, lô :00 mỗi giờ | Nguồn chính, tiêu đề tiếng Anh | `seendate` (giờ GDELT thấy tin); dùng giờ đăng trong HTML meta nếu có và cùng ngày UTC | ≈25% bài (1/4 lô 15 phút); DOC API bị 429 liên tục nên dùng file GKG tĩnh |
| SEC EDGAR full-text search | Sự kiện pháp lý/ETF (S-1, 19b-4, 8-K) | "Accepted" trên trang index (giờ New York → UTC), không dùng `file_date` | Không đưa vào chỉ số ngày (văn bản pháp lý dài); dùng cho event study |
| RSS (CoinDesk, Cointelegraph, The Block, Decrypt) | Chỉ tab Live của dashboard | `pubDate` | Không có lịch sử 2023–2026; ToS của ba trang cấm thu tự động, bản công khai chỉ dùng The Block |
| GDELT translation, `srclc:vie` | Nhánh phụ tiếng Việt | `seendate` | Chấm bằng `dict/fin_vn.csv` + `dict/crypto_vn.csv`, không dịch |
| CryptoPanic dataset (CC0, 2017-09 → 2025-12-03) | Chỉ làm nhãn yếu cho RQ1 | `newsDatetime`, kiểm là UTC (mục 3.1) | Không phủ kỳ test, nên không đưa vào chỉ số |
| UCRY Policy/Price (Lucey et al., 2022) | Biến kiểm soát bất định chung | Tuần kết thúc Chủ nhật; dùng từ thứ Hai | Có đến 2024-12 |

Giá: Binance qua ccxt, nến ngày và nến giờ cho BTC, ETH, SOL, BNB, XRP (do Codex thu). Mẫu: 2023-01-01 → 2026-09-30. Train đến 2025-06-30, valid đến 2025-12-31, test sau đó.

### 2.2. Thời điểm ra công chúng

`public_ts_utc = min(giờ đăng hợp lệ, giờ thấy)`. Giờ đăng hợp lệ phải thỏa cả ba điều kiện:
- không sau giờ thấy;
- không sớm hơn giờ thấy quá 48 giờ;
- **cùng ngày UTC với giờ thấy.**

Điều kiện thứ ba bổ sung sau adversarial review. Chữ ta có là bản thấy lúc `first_seen`, mà bài có thể đã được sửa sau giờ đăng. Nếu lùi chữ đó qua nửa đêm, tin của ngày t+1 sẽ lọt vào feature của ngày t. Tin vào ngày t khi `public_ts_utc ∈ [t, t+1)` UTC. Feature ngày t chỉ dùng thông tin trước t+1 00:00 UTC.

### 2.3. Trùng lặp và gắn mã coin

Hai tin coi là trùng khi:
- cùng URL chuẩn hóa (giữ path và query định danh, chỉ bỏ tham số tracking); hoặc
- tiêu đề giống nhau ≥ 90% (rapidfuzz) với bản gốc trong vòng 3 ngày trước.

Bản gốc là bản có `public_ts_utc` sớm nhất. Không nối chuỗi: tin chỉ so với bản gốc, không so với bản trùng. Mã coin gắn bằng regex ticker/tên, phân biệt chữ hoa cho ticker (SOL, ETH).

## 3. Độ tin cậy của dữ liệu (tạm thời)

### 3.1. Độ chính xác timestamp

| So sánh | n cặp | Trung vị lệch | % lệch > 1 giờ | % đổi ngày UTC |
|---|---|---|---|---|
| GDELT `seendate` so với giờ đăng trong HTML meta | 42 | +142 phút | 78,6 | 16,7 |
| SEC "Accepted" (UTC) so với `file_date` | 2.053 | — | — | 6,4 |
| CryptoPanic `newsDatetime` so với GDELT `seendate`, tiêu đề trùng | 695 | GDELT chậm hơn 1,3 giờ | — | — |

**Nghĩa là gì:** GDELT thấy tin trễ khoảng 2 giờ so với giờ đăng. Cứ 6 tin thì có 1 tin bị đẩy sang ngày UTC hôm sau. Quy tắc 2.2 chọn phía an toàn: những tin này gán vào ngày *thấy*, không phải ngày *đăng*. Cách làm này có thể làm trễ tín hiệu, nhưng không tạo look-ahead. Với SEC, dùng `file_date` sẽ gán sai ngày cho 6,4% hồ sơ, vì hồ sơ nộp sau 17:30 giờ New York được tính sang ngày làm việc kế tiếp. Audit HTML mới có 42 cặp, vì phần lớn trang không công bố giờ đăng có múi giờ hoặc chặn robot. **[chờ]** mở rộng mẫu audit.

### 3.2. Thống kê corpus

**[chờ]** dữ liệu đầy đủ: `outputs/tables/corpus_stats.csv`. Tạm thời có 18.748 tin tiếng Anh canonical trên 180 ngày, và 2.053 hồ sơ SEC.

## 4. Phương pháp

### 4.1. Sentiment từng tin

- **Loughran–McDonald** (Loughran & McDonald, 2011): từ điển tài chính. Mẫu số là số từ thuộc LM master. Bỏ từ tích cực có phủ định trong 3 từ trước. Net = (P − N)/(P + N).
- **Harvard IV-4**: từ điển tổng quát, dùng làm đối chứng.
- **FinBERT** (Araci, 2019): sentiment = P(positive) − P(negative) ∈ [−1, 1], trung bình trên ≤ 20 câu đầu.
- **Tin tiếng Việt**: VietScorer, khớp cụm dài nhất, xử lý phủ định "không/chưa/chẳng".
- **CryptoBERT**: chỉ dùng ở bảng kiểm định, vì chưa rõ dữ liệu huấn luyện của model có chồng lên giai đoạn mẫu không.

### 4.2. Narrative

Tám narrative định trước: regulation, ETF/institutional, security/hacks, stablecoins, DeFi, AI tokens, macro/monetary, price/speculation.
- **LDA** (benchmark): chọn K ∈ {8, 12, 16, 20} bằng perplexity trên kỳ valid.
- **BERTopic** (Grootendorst, 2022).
- **Zero-shot**: cosine giữa embedding đa ngữ của tin và mô tả narrative. Tin có độ tương đồng dưới phân vị 20% của train được gán "other".

Cả ba phương pháp chỉ fit trên train. Topic của LDA và BERTopic được ánh xạ sang narrative bằng embedding của 10 từ đặc trưng. Zero-shot là phương pháp chính, vì hai phương pháp không giám sát dồn tin vào vài narrative (`narrative_taxonomy.csv`).

### 4.3. Chỉ số ngày

Cho mỗi ngày t và mỗi tài sản (ALL hoặc từng mã):
- **Sentiment**: Sent_t = trung bình sentiment của tin trong ngày (w_d = 1). Tách pos_sent = mean(max(s, 0)) và neg_sent = mean(max(−s, 0)).
- **Attention**: cứng, Attention_k,t = N_k,t / N_t; và mềm, trung bình xác suất zero-shot.
- **Disagreement** (Antweiler & Frank, 2004): √(1 − A²), với A = (N⁺ − N⁻)/(N⁺ + N⁻).
- **Gia tốc tin xấu**: neg_accel_t = neg_sent_t − neg_sent_{t−1}.

Chỉ dùng tin báo tiếng Anh.

### 4.4. Kinh tế lượng và dự báo (phần của Codex)

- Hồi quy dự báo với sai số HAC Newey–West. Kiểm định Wald β⁻ = β⁺ cho RQ2.
- VAR/Granger hai chiều cho RQ4.
- Walk-forward Elastic Net, XGBoost, LightGBM, so market-only với market+text. Kiểm định Diebold & Mariano (1995) và hiệu chỉnh Holm/BH cho RQ5.

Mô hình market-only lồng trong market+text, nên đề xuất báo thêm Clark–West (`docs/research/ADOPT.md`, P1).

## 5. Kết quả

- **RQ1.** **[chờ]** 300 nhãn tay (`data/interim/validation_sample.csv`) và bảng nhãn yếu CryptoPanic (`outputs/tables/sentiment_validation_weak.csv`).
- **RQ2–RQ5.** **[chờ]** `outputs/tables/real/*` trên `text_daily` đầy đủ. Bản chụp hiện tại có 177 ngày tin, nên chưa đủ chuỗi liên tục cho VAR và chưa đủ kỳ test cho so sánh ngoài mẫu.

## 6. Hạn chế

- GDELT chỉ lấy lô :00 mỗi giờ, khoảng 25% bài. Thứ tự lấy mẫu rải đều thời gian, không chọn theo nội dung.
- Giờ đăng chỉ kiểm được cho một mẫu nhỏ. Phần còn lại dùng `seendate`, là đồng hồ trễ hơn nhưng không gây look-ahead.
- Nhãn yếu CryptoPanic là phiếu của đám đông về kỳ vọng giá, không phải nhãn giọng điệu của chuyên gia. Nguồn dừng ở 2025-12-03.
- UCRY là chuỗi tính hồi cứu, không có các phiên bản công bố theo thời gian thực (vintage), và chỉ phủ đến 2024-12.
- Có thể có độ chệch do narrative định trước. LDA và BERTopic được báo cáo song song để đối chứng.

## 7. Đối chiếu checklist (blueprint mục 6)

| Mục | Trạng thái |
|---|---|
| RQ rõ, nhất quán với model | Có (mục 1, 4) |
| Data dictionary + source log | Có: `docs/DATA_CONTRACT.md`, `docs/SOURCES.md` |
| Script tải và chuẩn hóa chạy lại được | Có: `src/data/*`, cache và resume |
| Không look-ahead/leakage | Đã qua adversarial review; 2 lỗi [high] đã sửa có test (mục 2.2, 2.3) |
| Benchmark kinh tế lượng | Có code (Codex); **[chờ]** dữ liệu đầy đủ |
| Ít nhất một model nâng cao | FinBERT, BERTopic, XGBoost/LightGBM |
| Kiểm định ngoài mẫu chưa chạm tới | Có quy tắc chia mẫu; **[chờ]** kết quả |
| Robustness | X4 của Codex; **[chờ]** |
| README hướng dẫn chạy | **[chờ]** cập nhật ở C4 |
| Dashboard demo | Có: https://crypto-narrative-report.vercel.app |
| Báo cáo giải thích ý nghĩa kinh tế | Bản nháp này; mỗi bảng có câu "Nghĩa là gì" |

## Tài liệu tham khảo

Xem `paper/references.bib`. Các trích dẫn trong bản nháp: Araci (2019); Antweiler & Frank (2004); Diebold & Mariano (1995); Grootendorst (2022); Loughran & McDonald (2011); Lucey, Vigne, Yarovaya & Wang (2022). Bảy bài lõi của blueprint được tổng quan ở `paper/related_work.md`.
