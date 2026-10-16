# Ghi chú toàn văn: Lucey et al. (2022) và Khaksar et al. (2026)

Đọc bản in (VoR, CC BY) do người dùng tải tay ngày 2026-10-16. Dùng file này để điền `paper/related_work.md`, `docs/research/PAPERS.md` (bỏ trạng thái "chỉ abstract"/"đọc qua luận văn").

## Lucey, Vigne, Yarovaya & Wang (2022) — The cryptocurrency uncertainty index
*Finance Research Letters* 45, 102147. DOI 10.1016/j.frl.2021.102147. OA (CC BY).

- **Dữ liệu:** LexisNexis Business (báo + newswire + bản tin), 726,9 triệu bài được quét, 01/2014–01/2021; truy vấn chạy theo tháng, bật "Group Duplicate = MODERATE" để bỏ trùng.
- **Truy vấn (nguyên văn logic):**
  - UCRY Policy: `(uncertain OR uncertainty) AND price AND atl1(Bitcoin OR Ethereum OR ripple OR litecoin OR tether OR cryptocurrency OR cryptocurrencies) AND atl1(regulator OR regulators OR central bank OR government)`.
  - UCRY Price: như trên nhưng bỏ vế regulator/government.
- **Công thức:** `UCRY_t = (N_t − μ)/σ + 100`, N_t = số bài khớp trong tuần t (12/2013–02/2021); μ, σ tính trên **toàn mẫu** → có look-ahead nếu dùng để dự báo.
- **Kinh tế lượng:** VAR 8 biến (UCRY Policy, Global EPU, VIX, giá BTC, US financial stress, US EPU, vàng, UCRY Price). ADF: mọi chuỗi có nghiệm đơn vị (p > 0,05). Lag tối ưu = 4 (AIC, HQ, SC, FPE đồng thuận). Johansen trace r=0: 215,11 > 177,20 (1%) → đồng liên kết → SVECM, nhận dạng Cholesky (UCRY Policy đứng đầu, UCRY Price đứng cuối), phân rã lịch sử.
- **Kết quả:** Chỉ số tăng quanh Brexit, bầu cử Mỹ 2016, Trung Quốc cấm ICO, bong bóng BTC 2017, DeFi 2020, các vụ hack sàn (Bitfinex, MintPal, DAO…) và COVID-19. Tương quan Pearson: UCRY Price–giá BTC 0,86; UCRY Policy–giá BTC 0,83; UCRY Policy–UCRY Price 0,99. Chỉ số "dao động hẹp" (UCRY Policy: min 99,10, max 104,34).
- **Điểm cần nói rõ khi trích:** Bảng thống kê mô tả và phân rã lịch sử có 85 quan sát theo **tháng**, trong khi phần phương pháp nói **tuần** — bài không giải thích. Dữ liệu công bố chỉ tới 01/2021 → **không ghép trực tiếp được** vào mẫu 2023–2026 của mình.

**Áp dụng cho đề tài**
1. Dựng chỉ số kiểu UCRY từ chính tiêu đề GDELT của mình (cùng logic truy vấn, đếm theo ngày), làm biến kiểm soát "bất định" và đối chứng cho narrative `regulation` (RQ3). **Chuẩn hoá μ, σ chỉ trên train** (sửa điểm look-ahead của bài gốc) — đây là điểm phương pháp đáng nêu trong paper.
2. UCRY tương quan 0,83–0,86 với **mức giá** BTC → chỉ số tin tức có thể chỉ phản ánh giá. Đây đúng là lý do RQ4 phải test Granger hai chiều (text → giá và giá → text).
3. Trước VAR: ADF/KPSS và chọn lag bằng nhiều tiêu chí (Codex X4 đã có ADF/KPSS).

## Khaksar, Biktimirov, Ayanso & Sokolyk (2026) — Bitcoin returns and volume: Uncovering investor sentiment through topic modeling
*International Review of Financial Analysis* 116, 105197. DOI 10.1016/j.irfa.2026.105197. OA (CC BY). Nhận 13/09/2024, chấp nhận 01/05/2026.

- **Dữ liệu:** 1.954.166 bài trong mục "Bitcoin Discussion" của Bitcointalk.org (thu bằng Scrapy), 09/2014–09/2022, chỉ tiếng Anh. Giá/khối lượng BTC từ Yahoo Finance (từ 18/09/2014). Kiểm soát: S&P 500, vàng, USD/EUR, VIX (Bloomberg), Google Trends "Bitcoin". N = 2.018 ngày.
- **Tiền xử lý:** bỏ câu trích dẫn bài trước, giữ tiếng Anh, bỏ URL/số, mở rộng viết tắt, bỏ 7 danh sách stop-word của Loughran–McDonald + "bitcoin/BTC", **chỉ giữ danh từ**, lemmatize.
- **Sentiment:** VADER (compound ∈ [−1, 1]) **bổ sung từ điển LM**: gán cho từ LM dương/âm điểm trung bình của từ dương/âm trong VADER. Dùng điểm liên tục, không dùng nhãn.
- **Topic:** chạy LDA, LSA, TSM, JST; chọn **LDA, K = 8** sau khi xét K = 5–15 bằng 4 điểm coherence (UCI, UMass, NPMI, C_v) + đọc top-20 từ và top-100 bài. Topic: Investment 26,03%, Public Perception 16,45%, Regulation 14,35%, Wallet 12,36%, Bitcoin's Nature 9,15%, Payment 9,14%, Mining 9,10%, Other 3,42%.
- **Ba chiều theo topic j, ngày t:**
  - Sentiment_{j,t} = trung bình (PostSentiment_i × W_{j,i}) trên các bài trong ngày, với W là trọng số topic của bài từ LDA.
  - Disagreement_{j,t} = độ lệch chuẩn của PostSentiment_i × W_{j,i} trong ngày.
  - Attention_{j,t} = Σ_i W_{j,i} (tổng trọng số mềm, không phải đếm nhãn cứng); attention chung = số bài trong ngày.
- **Mô hình:** OLS HAC Newey–West; hồi quy phân vị τ = 0,1…0,9; hồi quy phân vị cửa sổ trượt 500 phiên, bước 20 phiên (76 cửa sổ). **Hồi quy cùng kỳ** (y_t trên biến text ngày t), không phải dự báo.
- **Kết quả chính:**
  - Lợi suất (OLS): chỉ topic Investment có ý nghĩa — sentiment +0,183*** (SE 0,059), disagreement −0,159*** (SE 0,051). Sentiment chung 0,018 (không ý nghĩa). Attention không có ý nghĩa ở mọi topic. R² ≈ 0,054–0,060.
  - Khối lượng (OLS): sentiment và disagreement có ý nghĩa ở hầu hết topic; R² 0,47–0,79.
  - Phân vị: sentiment **dương ở τ = 0,1, âm ở τ = 0,9** với General, Investment, Public Perception, Regulation, Wallet, Other (ví dụ Investment +0,416*** ở τ = 0,1; Regulation +0,321*** ở τ = 0,1 và −0,275** ở τ = 0,9). Attention đổi dấu: âm ở phân vị thấp, dương ở phân vị cao.
  - Cửa sổ trượt: hệ số thay đổi mạnh theo thời gian (vd Wallet âm có ý nghĩa 2019–2021).

**Áp dụng cho đề tài**
1. **Thêm "disagreement"** = độ lệch chuẩn sentiment trong ngày (chung và theo narrative) vào `text_daily` → đổi DATA_CONTRACT (Claude). Bài cho thấy disagreement có ý nghĩa khi sentiment trung bình thì không.
2. **Attention mềm** = Σ xác suất narrative / N_t, làm robustness cho attention cứng N_k/N_t hiện tại (Claude).
3. **Hồi quy phân vị** τ = 0,1/0,5/0,9 cho RQ2 (bất đối xứng), bổ sung cho Wald β⁻ = β⁺; **cửa sổ trượt 500 ngày, bước 20** cho robustness theo thời gian (Codex X4).
4. Chọn K của LDA/BERTopic bằng coherence (UCI, UMass, NPMI, C_v) **chỉ trên train**, kèm đọc top từ (Claude).
5. Stop-word LM khi làm topic (Claude).
6. Khoảng trống mình lấp: bài này hồi quy **cùng kỳ** và chỉ BTC/Bitcointalk; đề tài mình **dự báo t → t+h, point-in-time, out-of-sample (DM)**, 5 coin, nguồn tin tức có giờ công bố. Ghi rõ điều này ở related_work (RQ5).
7. Biến kiểm soát của bài (S&P 500, vàng, VIX, USD, Google Trends) — cân nhắc thêm (Codex, P2; dữ liệu FRED/Yahoo).
