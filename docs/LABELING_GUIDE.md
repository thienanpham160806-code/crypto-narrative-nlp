# Hướng dẫn gán nhãn 300 tiêu đề (validation_sample.csv)

Mục đích: đo độ chính xác của LM, Harvard IV-4, FinBERT, CryptoBERT (cảm xúc) và zero-shot/LDA/BERTopic (narrative) trên nhãn người (RQ1). Mẫu 300 tiêu đề chọn ngẫu nhiên trước `split.valid_end`, sinh bởi `PYTHONPATH=src python -m features.validation sample`.

## Cách làm
1. Mở `dashboard/labeler.html` bằng trình duyệt (bấm đúp), chọn `data/interim/validation_sample.csv`.
2. Mỗi tiêu đề gán **đúng một** nhãn cảm xúc và **đúng một** nhãn narrative. Phím: `1/2/3` cảm xúc, `Q W E R T Y U I O` narrative, `←/→` chuyển câu, `Enter` câu chưa gán kế tiếp, `Backspace` xóa nhãn câu hiện tại.
3. Nhãn lưu tạm trong trình duyệt; xong thì bấm **Xuất CSV** và ghi đè `data/interim/validation_sample.csv` (giữ nguyên các cột khác).
4. Chỉ đọc **tiêu đề** và ngày; không mở bài, không tra giá sau ngày đăng (tránh nhìn trước tương lai).

## Cảm xúc (`label_sentiment`)
Hỏi: *với người nắm giữ tài sản tiền mã hóa được nhắc đến, tại thời điểm đăng, tin này là tốt, xấu hay không rõ?*

| Nhãn | Khi nào | Ví dụ |
|---|---|---|
| `positive` | Tin có lợi cho giá hoặc cho thị trường: tăng giá, dòng tiền vào, được phê duyệt, chấp nhận rộng rãi, quy định thuận lợi. | "SEC approves spot bitcoin ETFs" |
| `negative` | Tin bất lợi: giảm giá, bị hack/lừa đảo, kiện tụng, cấm, phá sản, rút vốn. | "Exchange hacked, $200M stolen" |
| `neutral` | Mô tả, giải thích, hướng dẫn, dự báo hai chiều, câu hỏi, hoặc không xác định được tốt/xấu. | "What is a crypto wallet?" |

Quy tắc phân xử:
- Phủ định đảo nghĩa: "SEC **does not** appeal ruling" là `positive`.
- Tin xấu cho một bên nhưng tốt cho thị trường (vd. "regulator fines scam operator"): theo tác động lên tài sản được nhắc; không rõ thì `neutral`.
- Câu hỏi/dự báo ("Will bitcoin hit $100K?"): `neutral`, trừ khi tiêu đề khẳng định rõ chiều.
- Không chắc giữa hai nhãn → chọn `neutral`.

## Câu chuyện thị trường (`label_narrative`)
Chọn chủ đề **chính** của tiêu đề (cái mà tin đang nói về), không phải từ khóa phụ.

| Phím | Nhãn | Bao gồm |
|---|---|---|
| Q | `regulation` | Luật, cơ quan quản lý (SEC, CFTC…), kiện tụng, lệnh cấm, thuế, chính sách nhà nước về tiền mã hóa |
| W | `etf_institutional` | ETF, dòng tiền vào/ra quỹ, nhà đầu tư tổ chức, ngân hàng, quỹ quản lý tài sản, doanh nghiệp nắm giữ |
| E | `security_hacks` | Hack, exploit, đánh cắp, lừa đảo, rug pull, lỗ hổng bảo mật |
| R | `stablecoins` | USDT, USDC và stablecoin khác: neo giá, mất neo, dự trữ, tổ chức phát hành |
| T | `defi` | Giao thức DeFi: cho vay, sàn phi tập trung, pool thanh khoản, staking, lợi suất |
| Y | `ai_tokens` | Token/dự án AI, AI agent trên blockchain |
| U | `macro_monetary` | Fed, lãi suất, lạm phát, suy thoái, USD, chứng khoán, địa chính trị ảnh hưởng thị trường |
| I | `price_speculation` | Diễn biến giá, dự báo giá, phân tích kỹ thuật, trader, tăng/giảm mạnh, thanh lý |
| O | `other` | Không thuộc 8 nhóm trên (công nghệ chung, NFT, game, nhân sự, quảng cáo…) |

Quy tắc phân xử:
- Tin về giá **kèm nguyên nhân** thuộc nhóm khác → chọn nhóm nguyên nhân ("Bitcoin jumps after ETF approval" → `etf_institutional`). Chỉ chọn `price_speculation` khi tiêu đề chủ yếu nói về giá.
- Vụ hack trên giao thức DeFi → `security_hacks` (sự kiện là hack).
- Kiện tụng sàn vì lừa đảo → `regulation` nếu chủ thể là cơ quan quản lý/tòa án; `security_hacks` nếu là vụ lừa đảo/đánh cắp.
- Viết đúng chữ thường, đúng tên như bảng (labeler tự làm việc này).

## Sau khi gán
`PYTHONPATH=src python -m features.validation` để tính bảng độ chính xác trên nhãn tay; `python paper/fill_results.py` tự đưa kết quả vào Panel B của Bảng 5.
