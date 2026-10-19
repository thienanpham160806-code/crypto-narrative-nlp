---
title_vi: Narrative và cảm xúc trong tin tức tiền mã hóa: Bằng chứng từ tín hiệu văn bản theo thời điểm công bố đối với lợi suất, biến động và khối lượng giao dịch
title_en: News narratives and sentiment in cryptocurrency markets: Evidence from publication-time text signals for returns, volatility, and trading volume
author: Phạm Ngọc Thiên An
affiliation: Trường Đại học Kinh tế - Luật, Đại học Quốc gia Thành phố Hồ Chí Minh, Thành phố Hồ Chí Minh, Việt Nam
email:
doi:
received:
revised:
accepted:
jel: G12; G14; G41; C53
keywords_vi: tiền mã hóa; cảm xúc thị trường; narrative; phân tích văn bản; thời điểm công bố
keywords_en: cryptocurrency; market sentiment; narrative; textual analysis; publication timing
---

## TÓM TẮT

Nghiên cứu này kiểm định liệu tín hiệu văn bản trích từ tin tức tiếng Anh có mang thông tin gia tăng cho lợi suất, biến động thực hiện và khối lượng giao dịch của năm tiền mã hóa lớn (BTC, ETH, SOL, BNB, XRP) giai đoạn 01/2023 - 09/2026 hay không. Mỗi tin được gán ngày theo thời điểm ra công chúng thận trọng (giờ đăng khi hợp lệ, nếu không thì giờ hệ thống thấy tin lần đầu), còn các mô hình văn bản chỉ được ước lượng trên kỳ huấn luyện. Chỉ số cảm xúc, chú ý và 08 câu chuyện thị trường được xây dựng theo ngày từ 142.646 tin bằng hai từ điển tài chính, FinBERT và phân loại zero-shot, rồi kiểm định bằng hồi quy dự báo với sai số HAC, kiểm định Wald, phân tích sự kiện theo giờ, mô hình VAR và so sánh dự báo ngoài mẫu. Kết quả cho thấy FinBERT phân biệt tin tốt và tin xấu tốt hơn từ điển (AUC 0,712 so với 0,612 của Loughran - McDonald). Tin tức không đi kèm lợi suất bất thường có hướng, nhưng khối lượng giao dịch bất thường tăng có ý nghĩa trong giờ đầu sau tin và đã tăng từ trước khi tin xuất hiện; tin tốt đi kèm khối lượng giao dịch và độ lớn biến động giá cao hơn tin xấu. Kiểm định Granger cho thấy lợi suất dẫn trước cảm xúc của tin ở cả 05 tài sản, trong khi chiều ngược lại không có ý nghĩa sau hiệu chỉnh kiểm định bội, và bổ sung văn bản chưa cải thiện dự báo ngoài mẫu một cách có ý nghĩa. Nghiên cứu đóng góp một quy trình dữ liệu văn bản đúng thời điểm cho thị trường tiền mã hóa và hàm ý rằng tin tức chủ yếu phản ánh diễn biến giá hơn là báo trước giá.

## ABSTRACT

This study examines whether text signals extracted from English-language news carry incremental information for the returns, realized volatility, and trading volume of five major cryptocurrencies (BTC, ETH, SOL, BNB, and XRP) over January 2023 - September 2026. Each article is dated by a conservative public release time (the published time when valid, otherwise the first-seen time) and text models are estimated on the training period only. Daily indices of sentiment, attention, and eight market stories are built from 142,646 articles using two financial dictionaries, FinBERT, and zero-shot classification, and are tested with predictive regressions using HAC standard errors, Wald tests, hourly event studies, VAR models, and out-of-sample forecast comparisons. FinBERT separates good from bad news better than the dictionaries (AUC of 0.712 versus 0.612 for Loughran - McDonald). News is not followed by directional abnormal returns, but abnormal trading volume rises significantly in the first hour after news and is already elevated before publication; good news is accompanied by higher volume and larger price moves than bad news. Granger tests show that returns lead news sentiment for all five assets, whereas the reverse direction is not significant after multiple-testing correction, and adding text does not significantly improve out-of-sample forecasts. The study contributes a time-consistent text data pipeline for cryptocurrency markets and implies that news mainly reflects past price movements rather than anticipating them.

## 1. Giới thiệu

Tiền mã hóa (cryptocurrency) là tài sản số được ghi nhận và chuyển giao trên sổ cái phân tán. Khác với cổ phiếu hay trái phiếu, loại tài sản này không gắn với dòng cổ tức hay dòng lãi cố định để định giá, nên giá của nó phụ thuộc nhiều vào niềm tin chung của nhà đầu tư. Cảm xúc thị trường (market sentiment) được hiểu là niềm tin của nhà đầu tư về dòng tiền và rủi ro tương lai mà các dữ kiện cơ bản chưa biện minh đầy đủ (Baker & Wurgler, 2007). Bên cạnh đó, câu chuyện thị trường (narrative) là những câu chuyện phổ biến lan truyền trong công chúng giống như dịch bệnh và có thể làm thay đổi hành vi kinh tế (Shiller, 2017). Sự chú ý của nhà đầu tư (attention) cũng là một kênh quan trọng vì nhà đầu tư chỉ mua những tài sản mà họ đã để ý đến (Da và cộng sự, 2011). Tin tức là kênh chính để cảm xúc, sự chú ý và câu chuyện thị trường lan truyền, nên việc đo lường các đại lượng này từ văn bản là hướng tiếp cận tự nhiên để hiểu giá tiền mã hóa.

Bằng chứng thực nghiệm trước đây ghi nhận rằng thông tin từ văn bản liên hệ với giá tài sản. Tetlock (2007) cho thấy mức độ bi quan trong một chuyên mục báo tài chính dự báo áp lực giảm giá của thị trường cổ phiếu Mỹ, còn Antweiler và Frank (2004) gắn mức bất đồng giữa các bài đăng trên diễn đàn với khối lượng giao dịch. Đối với tiền mã hóa, Kristoufek (2013) ghi nhận quan hệ hai chiều giữa lượt tìm kiếm trên Internet và giá Bitcoin, Garcia và Schweitzer (2015) thấy các tín hiệu từ mạng xã hội đi trước biến động giá, và Liu và Tsyvinski (2021) cho thấy sự chú ý của nhà đầu tư dự báo lợi suất. Kraaijeveld và De Smedt (2020) kết luận rằng cảm xúc trên Twitter dự báo được lợi suất của một số đồng tiền, nhưng với nhiều đồng còn lại thì giá lại dẫn dắt cảm xúc. Về kênh tác động, Chou và cộng sự (2023) và Kao và cộng sự (2024) cho rằng tin tiêu cực và tin tích cực tác động đến biến động theo những cơ chế khác nhau, còn Gür và Ünal (2026) ghi nhận phản ứng của giá Bitcoin đối với tin tiêu cực mạnh hơn so với tin tích cực hoặc trung tính.[^abs]

Thị trường tiền mã hóa vận hành liên tục 24 giờ mỗi ngày, bảy ngày mỗi tuần, nên tin tức được phản ánh vào giá gần như ngay khi xuất hiện và ranh giới giữa các ngày giao dịch không rõ như ở thị trường truyền thống. Giai đoạn 2023 - 2026 ghi nhận nhiều sự kiện về quy định pháp lý, quỹ hoán đổi danh mục (ETF), các vụ tấn công sàn giao dịch, stablecoin, tài chính phi tập trung (DeFi), các token gắn với trí tuệ nhân tạo và chính sách tiền tệ. Chính vì vậy, nghiên cứu chọn năm tài sản có vốn hóa lớn gồm BTC, ETH, SOL, BNB và XRP làm đối tượng quan sát, và dùng dữ liệu tin tức toàn cầu thu theo giờ từ nguồn công khai.

Tuy vậy, các nghiên cứu trước đây còn bỏ ngỏ một số vấn đề. Thứ nhất, thời điểm một tin thực sự ra công chúng ít khi được kiểm chứng, nên chỉ số cảm xúc của ngày t có thể chứa các tin xuất hiện sau khi giá đã phản ứng. Thứ hai, các mô hình văn bản như từ vựng hay chủ đề thường được ước lượng trên toàn bộ mẫu, bao gồm cả kỳ dùng để đánh giá ngoài mẫu. Thứ ba, từ điển và mô hình chuyển đổi (transformer) hiếm khi được so sánh trên cùng một kho tin tiền mã hóa và cùng một biến mục tiêu. Thứ tư, nhiều nghiên cứu chỉ có mẫu ngắn, chẳng hạn hai tháng dữ liệu Twitter trong Kraaijeveld và De Smedt (2020) hay sáu tuần dữ liệu phút trong Barjašić và Antulov-Fantulin (2021), và thường không đánh giá ngoài mẫu. Thứ năm, các câu chuyện thị trường ít khi được kết hợp đồng thời với cảm xúc, sự chú ý và khối lượng giao dịch.

Dựa trên những khoảng trống nghiên cứu được giải thích ở trên, nghiên cứu này nhằm trả lời 05 câu hỏi. Câu hỏi thứ nhất (RQ1) là liệu cảm xúc đo bằng mô hình chuyển đổi có phân biệt tin tốt và tin xấu, và giải thích kết quả thị trường, tốt hơn từ điển hay không. Câu hỏi thứ hai (RQ2) là tin xấu có tác động khác với tin tốt hay không. Câu hỏi thứ ba (RQ3) là câu chuyện thị trường nào liên hệ mạnh nhất với lợi suất, biến động và khối lượng giao dịch. Câu hỏi thứ tư (RQ4) là văn bản dẫn dắt giá hay giá dẫn dắt văn bản. Câu hỏi thứ năm (RQ5) là liệu bổ sung văn bản có cải thiện dự báo ngoài mẫu so với mô hình chỉ có biến thị trường hay không.

Nghiên cứu đóng góp vào các nghiên cứu hiện có ở những điểm mới sau. Trước hết, nghiên cứu xác định thời điểm ra công chúng của từng tin từ nhiều đồng hồ dữ liệu, đo độ lệch giữa các đồng hồ theo nguồn và không cho phép văn bản bị lùi sang ngày trước, qua đó loại bỏ một nguồn rò rỉ thông tin mà các nghiên cứu trước ít kiểm soát. Tiếp theo, toàn bộ bộ vectơ hóa từ vựng, mô hình chủ đề và ngưỡng phân loại chỉ được ước lượng trên kỳ huấn luyện, còn mô hình ngôn ngữ lớn không được dùng làm biến giải thích vì có thể đã biết các sự kiện xảy ra sau ngày của tin. Hơn nữa, nghiên cứu so sánh trên cùng một kho tin hai từ điển với hai mô hình chuyển đổi bằng nhãn yếu từ phiếu bình chọn của người dùng, và đo 08 câu chuyện thị trường định trước cùng với cảm xúc và sự chú ý. Cuối cùng, nghiên cứu kết hợp hồi quy dự báo theo ngày, phân tích sự kiện theo giờ và dự báo ngoài mẫu với hiệu chỉnh kiểm định bội, thay vì chỉ dừng ở các chỉ tiêu độ chính xác.

Bài nghiên cứu được cấu tạo gồm 05 phần. Tiếp theo, nghiên cứu trình bày cơ sở lý thuyết và tổng quan các nghiên cứu trước đây ở mục 2. Phương pháp nghiên cứu và dữ liệu được giới thiệu trong phần 3. Phần 4 trình bày và thảo luận kết quả nghiên cứu thực nghiệm. Kết luận và hàm ý được trình bày ở phần 5.

## 2. Cơ sở lý thuyết và tổng quan các nghiên cứu trước đây

Tín hiệu văn bản (text signal) trong tài chính được hiểu là các đại lượng định lượng trích từ văn bản, gồm mức độ tích cực hoặc tiêu cực của giọng điệu (cảm xúc), mức độ xuất hiện của một chủ đề (sự chú ý) và mức độ phân tán của giọng điệu giữa các văn bản cùng thời điểm (bất đồng). Ba nhóm đại lượng này được dùng để giải thích và dự báo giá tài sản, dựa trên các khung lý thuyết khác nhau về cách thông tin đi vào giá.

Về mặt lý thuyết, giả thuyết thị trường hiệu quả cho rằng thông tin công khai được phản ánh nhanh chóng vào giá, nên chỉ số dựng từ tin đã công bố không thể dự báo lợi suất tương lai một cách có hệ thống (Fama, 1970). Ngược lại, tài chính hành vi lập luận rằng cảm xúc của nhà đầu tư có thể đẩy giá lệch khỏi giá trị nội tại trước khi đảo chiều, đặc biệt đối với những tài sản khó định giá và khó bán khống (Baker & Wurgler, 2007). Tetlock (2007) cung cấp bằng chứng cho lập luận này khi thấy áp lực giảm giá do tin bi quan sau đó được đảo ngược, một dấu hiệu của cảm xúc hơn là thông tin cơ bản. Đối với tiền mã hóa, khó định giá và thiếu dòng tiền cơ bản là đặc điểm nổi bật, do đó vai trò của cảm xúc và câu chuyện thị trường được kỳ vọng rõ hơn.

Bên cạnh đó, kinh tế học narrative của Shiller (2017) coi các câu chuyện lan truyền như một nhân tố độc lập tác động lên quyết định kinh tế. Bybee và cộng sự (2024) chuyển ý tưởng này thành phép đo khi tính tỷ trọng chủ đề trong khoảng 800.000 bài báo kinh doanh theo thời gian và cho thấy tỷ trọng này giải thích hoạt động kinh tế và dự báo lợi suất cổ phiếu. Nghiên cứu này áp dụng cùng logic cho tiền mã hóa, trong đó sự chú ý đến một câu chuyện thị trường được đo bằng tỷ trọng tin thuộc câu chuyện đó trong ngày. Walker (2024) áp dụng mô hình chủ đề cấu trúc cho 5.775 bài báo về Bitcoin trên năm tờ báo lớn giai đoạn 2011 - 2022 và ghi nhận một số câu chuyện, chẳng hạn câu chuyện về tội phạm, đi kèm với lợi suất tuần sau trong giai đoạn 2016 - 2022 nhưng không bền vững trong toàn mẫu. Khaksar và cộng sự (2026) dùng mô hình chủ đề LDA trên diễn đàn Bitcointalk để tách cảm xúc và mức độ phân tán của cảm xúc theo từng chủ đề, và ghi nhận các đại lượng này liên hệ với lợi suất và khối lượng giao dịch ở những mức độ khác nhau tùy chủ đề.

Về cơ chế truyền thông tin vào biến động, giả thuyết phân phối hỗn hợp (mixture of distribution hypothesis, MDH) cho rằng biến động và khối lượng cùng phản ứng ngay trong ngày với luồng thông tin, trong khi giả thuyết thông tin đến tuần tự (sequential information arrival hypothesis, SIAH) cho rằng thông tin lan dần nên có quan hệ trễ. Chou và cộng sự (2023) dùng hơn 24.000 tin về Bitcoin từ 64 trang tin để xây dựng luồng thông tin và thấy tin tiêu cực phù hợp với SIAH còn tin tích cực phù hợp với MDH. Kao và cộng sự (2024) mở rộng sang hợp đồng tương lai Bitcoin với hơn 41.000 tin, ghi nhận tin tiêu cực tác động lên lợi suất ngắn hạn, trái với dạng yếu của giả thuyết thị trường hiệu quả, còn tin tích cực tác động lên biến động cùng ngày. Barjašić và Antulov-Fantulin (2021) cũng cho thấy số lượng tweet, khối lượng giao dịch và chênh lệch giá mua bán cải thiện dự báo biến động phút ngoài mẫu trong khung MDH. Những kết quả này là cơ sở cho RQ2 về tính bất đối xứng và RQ4 về quan hệ dẫn dắt. Ngoài ra, Auer và Claessens (2018) dùng phân tích sự kiện trên 151 tin pháp lý và ghi nhận tin bất lợi làm giá giảm mạnh hơn mức tăng của tin thuận lợi, cho thấy tính bất đối xứng cũng xuất hiện quanh các sự kiện cụ thể.

Về phép đo giọng điệu, Loughran và McDonald (2011) cho thấy từ điển tổng quát như Harvard IV-4 (Stone và cộng sự, 1966) phân loại sai nhiều từ trong ngữ cảnh tài chính, và đề xuất một từ điển chuyên ngành. FinBERT (Araci, 2019) tinh chỉnh mô hình ngôn ngữ BERT trên câu tin tài chính nên nắm được ngữ cảnh và phủ định tốt hơn danh sách từ, với độ chính xác 0,86 trên tập Financial PhraseBank. Đối với tiền mã hóa, Nasekin và Chen (2020) mở rộng từ điển bằng mạng nơ-ron trên 1,22 triệu bình luận, còn Ider và Lessmann (2022) dùng nhãn yếu để huấn luyện BERT trên tin và mạng xã hội về Bitcoin và Ethereum. Gür và Ünal (2026) dùng điểm FinBERT trên hơn 650.000 tiêu đề tin tài chính và ghi nhận mô hình FinBERT - LSTM dự báo giá Bitcoin chính xác nhất, trong đó giá trễ của Bitcoin giải thích phần lớn biến động giá nhưng cảm xúc tin vẫn có ảnh hưởng đáng kể. Điều này gợi ý rằng giá trị gia tăng của văn bản nằm ở phần nhỏ của phương sai và cần được kiểm định ngoài mẫu.

Về dự báo, Garcia và Schweitzer (2015), Critien và cộng sự (2022), Ortu và cộng sự (2022) và Loginova và cộng sự (2024) đều cho thấy bổ sung cảm xúc hoặc chủ đề từ mạng xã hội cải thiện dự báo hướng giá của Bitcoin trong một số cấu hình, song kết quả phụ thuộc vào mô hình, thời kỳ và cách chia mẫu. Kraaijeveld và De Smedt (2020) chỉ ra rằng chiều nhân quả có thể ngược lại, khi giá dẫn dắt khối lượng tin nhắn ở nhiều đồng tiền. Cuối cùng, Lucey và cộng sự (2022) xây dựng chỉ số bất định tiền mã hóa từ tin trên LexisNexis và công bố dữ liệu theo tuần, nên chỉ số này được dùng làm biến kiểm soát cho mức bất định chung.

Qua việc lược khảo, nghiên cứu nhận thấy các nghiên cứu hiện có đã ghi nhận sự tồn tại của thông tin trong văn bản, nhưng còn thiếu bốn điều kiện cùng lúc: thời điểm công bố được kiểm chứng, mô hình văn bản không nhìn thấy kỳ đánh giá, so sánh trực tiếp giữa từ điển và mô hình chuyển đổi trên cùng kho tin tiền mã hóa, và đánh giá ngoài mẫu có kiểm định thống kê. Từ các lập luận trên, nghiên cứu kỳ vọng mô hình chuyển đổi phân biệt tin tốt và tin xấu tốt hơn từ điển (RQ1), tin xấu có tác động mạnh hơn tin tốt (RQ2), các câu chuyện về quy định và an ninh liên hệ mạnh hơn các câu chuyện khác (RQ3), mối quan hệ giữa văn bản và giá có thể xảy ra ở cả hai chiều (RQ4), và phần cải thiện dự báo ngoài mẫu từ văn bản, nếu có, sẽ nhỏ vì thị trường phản ứng nhanh với thông tin công khai (RQ5).

## 3. Phương pháp nghiên cứu

Nhằm giải thích vai trò của tín hiệu văn bản đối với lợi suất, biến động và khối lượng giao dịch tiền mã hóa, nghiên cứu xây dựng dữ liệu bảng cho 05 tài sản gồm BTC, ETH, SOL, BNB và XRP theo ngày trong giai đoạn từ 01/01/2023 đến 30/09/2026, tức 1.369 ngày. Ngày t được tính từ 00:00 đến 24:00 theo giờ UTC vì thị trường giao dịch liên tục. Mẫu được chia thành ba kỳ không chồng lấn là huấn luyện (đến 30/06/2025), kiểm tra (đến 31/12/2025) và đánh giá ngoài mẫu (từ 01/01/2026). Kỳ đánh giá ngoài mẫu không được sử dụng khi chọn tham số, chọn số chủ đề, chọn ngưỡng phân loại hay ước lượng bất kỳ mô hình văn bản nào.[^market]

Nguồn văn bản chính là kho tin GKG 2.0 của dự án GDELT (Leetaru & Schrodt, 2013), từ đó nghiên cứu lọc các tiêu đề tiếng Anh có chứa từ khóa tiền mã hóa.[^gkg] Nghiên cứu ưu tiên văn bản tiếng Anh gốc và các thư viện chuẩn quốc tế, nên không dịch giữa tiếng Việt và tiếng Anh để chấm điểm. Các hồ sơ của Ủy ban Chứng khoán và Hối đoái Hoa Kỳ (SEC) liên quan đến quỹ ETF tiền mã hóa được dùng riêng cho phân tích sự kiện, còn tin tiếng Việt chỉ là nhánh phụ chấm bằng từ điển tài chính tiếng Việt.[^viet] Bộ dữ liệu CryptoPanic công khai (Rahsaz, n.d.) chỉ được dùng làm nhãn yếu để kiểm định phép đo cảm xúc vì dữ liệu dừng ở tháng 12/2025, nên không phủ kỳ đánh giá ngoài mẫu.

Điểm mấu chốt của dữ liệu văn bản là thời điểm ra công chúng. Mỗi tin có thể có giờ đăng do nguồn công bố (p_d) và giờ hệ thống thấy tin lần đầu (f_d). Nghiên cứu xây dựng thời điểm ra công chúng của tin d như sau:

$$ T_d = \min\left(\tilde{p}_d,\; f_d\right) \tag{1} $$

Trong đó, p̃_d bằng p_d nếu giờ đăng hợp lệ và bằng f_d nếu ngược lại. Giờ đăng được coi là hợp lệ khi không sau giờ thấy, không sớm hơn giờ thấy quá 48 giờ và cùng ngày UTC với giờ thấy. Điều kiện cuối cùng bảo đảm văn bản mà nghiên cứu có, vốn là bản được thấy tại thời điểm f_d và có thể đã được chỉnh sửa sau giờ đăng, không bị lùi sang ngày trước đó. Tin thuộc ngày t khi T_d nằm trong khoảng [t, t+1), và mọi biến văn bản của ngày t chỉ dùng thông tin trước 00:00 UTC ngày t+1. Hai tin được coi là trùng khi có cùng địa chỉ trang (đã bỏ các tham số theo dõi) hoặc có tiêu đề giống nhau từ 90% trở lên với bản gốc trong ba ngày trước, và chỉ bản có T_d sớm nhất được giữ lại.[^dedup] Độ lệch giữa giờ thấy và giờ đăng được đo trên các tin có giờ đăng hợp lệ, và độ lệch của hồ sơ SEC được đo bằng cách so sánh giờ chấp nhận hồ sơ của SEC quy đổi từ giờ New York với ngày nộp hồ sơ.

Cảm xúc của từng tin được đo bằng ba thước đo. Thước đo thứ nhất là từ điển tài chính của Loughran và McDonald (2011), thước đo thứ hai là từ điển tổng quát Harvard IV-4 (Stone và cộng sự, 1966), và thước đo thứ ba là FinBERT (Araci, 2019).[^lex] Với FinBERT, điểm cảm xúc của tin d là hiệu số xác suất tích cực và tiêu cực:

$$ s_d = P_d^{+} - P_d^{-} \tag{2} $$

Gọi D_{i,t} là tập tin thuộc tài sản i trong ngày t và N_{i,t} là số tin của tập này, trong đó tin không gắn mã tài sản cụ thể được gán cho toàn thị trường. Chỉ số cảm xúc ngày, cùng hai thành phần tách riêng tin xấu và tin tốt để kiểm định tính bất đối xứng, được tính như sau:

$$ \text{Sent}_{i,t} = \frac{1}{N_{i,t}} \sum_{d \in D_{i,t}} s_d \tag{3} $$

$$ \text{NegSent}_{i,t} = \frac{1}{N_{i,t}} \sum_{d \in D_{i,t}} \max\left(-s_d,\, 0\right) \tag{4} $$

$$ \text{PosSent}_{i,t} = \frac{1}{N_{i,t}} \sum_{d \in D_{i,t}} \max\left(s_d,\, 0\right) \tag{5} $$

Các tin được phân loại vào 08 câu chuyện thị trường định trước gồm quy định pháp lý, quỹ ETF và nhà đầu tư tổ chức, an ninh và tấn công, stablecoin, tài chính phi tập trung, token trí tuệ nhân tạo, vĩ mô và tiền tệ, giá và đầu cơ. Phương pháp chính là phân loại zero-shot, trong đó mỗi tin và mô tả của mỗi câu chuyện được biểu diễn bằng vectơ nhúng đa ngữ và xác suất thuộc câu chuyện k được tính từ độ tương đồng cosine.[^zs] Các mô hình chủ đề LDA (Blei và cộng sự, 2003) và BERTopic (Grootendorst, 2022) được ước lượng song song để đối chứng, chỉ trên kỳ huấn luyện.[^topic] Sự chú ý đến câu chuyện k của tài sản i trong ngày t được đo bằng hai cách, tỷ trọng tin theo nhãn cứng và trung bình xác suất theo nhãn mềm:

$$ \text{Att}_{k,i,t} = \frac{N_{k,i,t}}{N_{i,t}} \tag{6} $$

$$ \widetilde{\text{Att}}_{k,i,t} = \frac{1}{N_{i,t}} \sum_{d \in D_{i,t}} \pi_{d,k} \tag{7} $$

Trong đó N_{k,i,t} là số tin được gán nhãn k và π_{d,k} là xác suất tin d thuộc câu chuyện k. Ngoài ra, nghiên cứu đo hai thước đo bất đồng khác nhau, gồm thước đo của Antweiler và Frank (2004) dựa trên nhãn cảm xúc của các tin trong ngày và độ lệch chuẩn của điểm cảm xúc trong ngày, cùng với gia tốc tin xấu bằng chênh lệch NegSent giữa ngày t và ngày t-1.[^dis]

Để trả lời RQ1 đến RQ3, nghiên cứu xây dựng phương trình hồi quy dự báo như sau:

$$ y_{i,t+h} = \alpha_i + \beta\, \text{Sent}_{i,t} + \gamma^{\prime} \text{Att}_{i,t} + \delta^{\prime} X_{i,t} + \varepsilon_{i,t+h} \tag{8} $$

Trong đó, i đại diện cho tài sản trong mẫu quan sát, t là ngày quan sát, h ∈ {1, 3, 7} là độ trễ dự báo tính theo ngày, y_{i,t+h} là biến mục tiêu và ε_{i,t+h} là sai số trong mô hình. Biến phụ thuộc là một trong ba đại lượng, gồm lợi suất log của ngày t+h, biến động thực hiện (realized volatility, RV) bằng tổng bình phương lợi suất log theo giờ trong ngày t+h (Andersen & Bollerslev, 1998), và logarit khối lượng giao dịch tính theo USD. Biến giải thích chính là cảm xúc Sent_{i,t} đo lần lượt bằng từng thước đo trong ba thước đo ở trên, kèm vectơ chú ý Att_{i,t} gồm 07 câu chuyện, trong đó câu chuyện giá và đầu cơ làm nhóm tham chiếu vì tổng các tỷ trọng bằng một. Vectơ biến kiểm soát X_{i,t} gồm lợi suất của ngày t và bảy ngày trước, RV và logarit khối lượng của ngày t, logarit số tin trong ngày, các thước đo bất đồng, chú ý theo nhãn mềm và chỉ số bất định tiền mã hóa theo tuần của Lucey và cộng sự (2022) khi chỉ số này có dữ liệu. Các biến được mô tả chi tiết trong Bảng 1 và số liệu thống kê mô tả được trình bày trong Bảng 2. Nghiên cứu ước lượng bình phương nhỏ nhất thông thường theo từng tài sản, với sai số chuẩn Newey và West (1987) có độ trễ bằng giá trị lớn hơn giữa 7 và h-1, chỉ trên các quan sát có biến mục tiêu nằm trong kỳ huấn luyện và kiểm tra.

Để kiểm định tính bất đối xứng ở RQ2, nghiên cứu thay Sent trong phương trình (8) bằng NegSent và PosSent và dùng RV làm biến mục tiêu:

$$ \text{RV}_{i,t+h} = \alpha_i + \beta^{-} \text{NegSent}_{i,t} + \beta^{+} \text{PosSent}_{i,t} + \gamma^{\prime} \text{Att}_{i,t} + \delta^{\prime} X_{i,t} + \varepsilon_{i,t+h} \tag{9} $$

Giả thuyết không là tin xấu và tin tốt có tác động như nhau, và được kiểm định bằng thống kê Wald:

$$ H_0:\ \beta^{-} = \beta^{+}, \qquad W = \frac{\left(\hat{\beta}^{-} - \hat{\beta}^{+}\right)^{2}}{\widehat{\text{Var}}\left(\hat{\beta}^{-} - \hat{\beta}^{+}\right)} \sim \chi^{2}(1) \tag{10} $$

Vì tác động của tin có thể khác nhau giữa ngày biến động thấp và ngày biến động cao, nghiên cứu cũng ước lượng phương trình (9) bằng hồi quy phân vị (Koenker & Bassett, 1978) của RV tại các phân vị τ = 0,1, 0,5 và 0,9 và kiểm định cùng giả thuyết β⁻ = β⁺ ở từng phân vị. Sai số chuẩn của hồi quy phân vị chỉ vững với phương sai thay đổi, chưa hiệu chỉnh tự tương quan.

Để trả lời RQ4, nghiên cứu ước lượng mô hình tự hồi quy vectơ (VAR) hai chiều giữa cảm xúc và biến thị trường, trong đó độ trễ p được chọn theo tiêu chí AIC và quan hệ dẫn dắt được kiểm định theo Granger (1969):

$$ Z_t = c + \sum_{j=1}^{p} A_j Z_{t-j} + u_t, \qquad Z_t = \left(\text{Sent}_t,\, y_t\right)^{\prime} \tag{11} $$

Kiểm định Granger yêu cầu một chuỗi ngày liên tục ít nhất 30 quan sát, nên số kiểm định thực hiện được phụ thuộc vào độ phủ tin. Bên cạnh hồi quy theo ngày, nghiên cứu dùng phân tích sự kiện theo giờ quanh thời điểm T_d. Gọi T_0 là nến giờ đầu tiên mở sau T_d. Lợi suất bất thường của tài sản i ở giờ τ được tính từ mô hình thị trường với BTC làm đại diện thị trường (riêng BTC dùng trung bình), ước lượng trên 144 nến giờ trước tin, và lợi suất bất thường tích lũy (CAR) trong cửa sổ [a, b] giờ là:

$$ \text{AR}_{i,\tau} = r_{i,\tau} - \hat{\alpha}_i - \hat{\beta}_i\, r_{\text{BTC},\tau} \tag{12} $$

$$ \text{CAR}_{e}[a,b] = \sum_{\tau=a}^{b} \text{AR}_{e,\tau} \tag{13} $$

Các cửa sổ gồm [0, 1], [0, 4] và [0, 24] giờ sau tin, cửa sổ [-4, -2] giờ trước tin để kiểm tra giá có chạy trước tin hay không, và nghiên cứu cũng đo độ lớn tuyệt đối của lợi suất và khối lượng giao dịch bất thường. Vì nhiều tin xuất hiện cùng giờ, các sự kiện được gộp theo ngày trước khi kiểm định bằng kiểm định t, kiểm định Wilcoxon và kiểm định của Boehmer và cộng sự (1991), và mọi p-value được hiệu chỉnh theo Holm (1979) trong từng họ kiểm định.[^event]

Để trả lời RQ5, nghiên cứu so sánh dự báo ngoài mẫu của ba phiên bản đặc trưng, gồm chỉ biến thị trường, thêm sự chú ý thô (logarit số tin), và thêm toàn bộ tín hiệu văn bản, trên ba mô hình là Elastic Net, XGBoost và LightGBM. Các mô hình được ước lượng theo cửa sổ mở rộng, tái ước lượng mỗi 30 ngày và chỉ dùng các nhãn đã đáo hạn tại thời điểm dự báo, còn siêu tham số được chọn trên kỳ kiểm tra. Độ chính xác ngoài mẫu được đo bằng R² ngoài mẫu so với trung bình lịch sử (Campbell & Thompson, 2008), và chênh lệch giữa hai mô hình được kiểm định bằng thống kê Diebold và Mariano (1995) có hiệu chỉnh mẫu nhỏ của Harvey và cộng sự (1997), đồng thời đối chiếu với kiểm định Clark và West (2007) vì mô hình chỉ có biến thị trường lồng trong mô hình có văn bản:

$$ R^{2}_{OS} = 1 - \frac{\sum_{t}\left(y_t - \hat{y}_t\right)^{2}}{\sum_{t}\left(y_t - \overline{y}_{t}\right)^{2}} \tag{14} $$

$$ d_t = e_{M,t}^{2} - e_{T,t}^{2}, \qquad \text{DM} = \frac{\overline{d}}{\sqrt{\widehat{\text{LRV}}(d)/T}} \tag{15} $$

Trong đó ȳ_t là trung bình lịch sử của biến mục tiêu tại thời điểm dự báo, e_{M,t} và e_{T,t} là sai số dự báo của mô hình chỉ có biến thị trường và mô hình có văn bản, và LRV là phương sai dài hạn. Các kiểm định về giá trị dự báo có điều kiện (Giacomini & White, 2006) và tập mô hình tin cậy (Hansen và cộng sự, 2011) chỉ thực hiện được khi chuỗi kiểm tra đủ dài. Ngoài ra, phép đo cảm xúc được kiểm định bằng 300 tiêu đề chọn ngẫu nhiên trước kỳ đánh giá và được gán nhãn thủ công, và bằng nhãn yếu từ phiếu bình chọn tích cực và tiêu cực của người dùng CryptoPanic, với các chỉ tiêu độ chính xác, F1 trung bình và diện tích dưới đường cong ROC (AUC). Cuối cùng, độ vững của kết quả được kiểm tra bằng cách chia mẫu theo thời gian và bằng việc thêm biến bất định tiền mã hóa làm biến kiểm soát.

**Bảng 1**

*Mô Tả Biến*

| Loại biến | Tên biến | Ký hiệu | Đo lường | Nguồn |
|---|---|---|---|---|
| Biến phụ thuộc | Lợi suất | r | Hiệu số logarit giá đóng cửa ngày | Binance |
| Biến phụ thuộc | Biến động thực hiện | RV | Tổng bình phương 24 lợi suất log theo giờ trong ngày UTC | Binance |
| Biến phụ thuộc | Khối lượng giao dịch | logVol | Logarit của (1 + khối lượng giao dịch tính bằng USD) | Binance |
| Biến phụ thuộc | Lợi suất bất thường tích lũy | CAR | Tổng lợi suất bất thường theo giờ trong cửa sổ [a, b] quanh T_0 | Tính toán từ Binance và GDELT |
| Biến giải thích | Cảm xúc ngày | Sent | Trung bình điểm cảm xúc của các tin trong ngày (FinBERT, Loughran - McDonald hoặc Harvard IV-4) | GDELT; mô hình văn bản |
| Biến giải thích | Tin xấu, tin tốt | NegSent, PosSent | Trung bình phần âm và phần dương của điểm cảm xúc | GDELT; FinBERT |
| Biến giải thích | Chú ý đến câu chuyện thị trường | Att | Tỷ trọng tin thuộc câu chuyện k (nhãn cứng) hoặc trung bình xác suất (nhãn mềm) | GDELT; zero-shot |
| Biến giải thích | Bất đồng | DisAF, DisSD | Thước đo Antweiler - Frank; độ lệch chuẩn của điểm cảm xúc trong ngày | GDELT; FinBERT |
| Biến kiểm soát | Thị trường trễ | X | Lợi suất của ngày t và 07 ngày trước, RV và logVol của ngày t | Binance |
| Biến kiểm soát | Số tin | logN | Logarit của số tin trong ngày | GDELT |
| Biến kiểm soát | Bất định tiền mã hóa | UCRY | Chỉ số UCRY Policy và UCRY Price theo tuần | Lucey và cộng sự (2022) |

*Ghi chú.* Tổng hợp của nhóm tác giả. Cảm xúc chỉ dùng tin tiếng Anh của GDELT, không gồm hồ sơ SEC. Biến văn bản của ngày t chỉ dùng tin ra công chúng trước 00:00 UTC ngày t+1.

**Bảng 2**

*Thống Kê Mô Tả Các Biến Trong Mô Hình*

| Biến | Số quan sát | Trung bình | Độ lệch chuẩn | Nhỏ nhất | Lớn nhất |
|---|---:|---:|---:|---:|---:|
| **Panel A. Biến thị trường (tài sản - ngày)** |  |  |  |  |  |
| Lợi suất log ngày (%) | 6.760 | 0,112 | 3,464 | −22,881 | 54,870 |
| Biến động thực hiện RV (×10⁴) | 6.755 | 12,348 | 24,341 | 0,096 | 948,512 |
| Log khối lượng USD | 6.760 | 19,859 | 1,223 | 16,346 | 23,571 |
| **Panel B. Biến văn bản (tài sản - ngày có tin)** |  |  |  |  |  |
| Log số tin trong ngày | 6.760 | 2,142 | 1,338 | 0,000 | 5,919 |
| Cảm xúc FinBERT (Sent) | 6.760 | 0,1088 | 0,2859 | −0,9663 | 0,9347 |
| Cảm xúc Loughran - McDonald | 6.760 | −0,0213 | 0,2646 | −1,0000 | 1,0000 |
| Cảm xúc Harvard IV-4 | 6.760 | 0,1102 | 0,3256 | −1,0000 | 1,0000 |
| Tin xấu (NegSent) | 6.760 | 0,1506 | 0,1587 | 0,0000 | 0,9663 |
| Tin tốt (PosSent) | 6.760 | 0,2594 | 0,1785 | 0,0000 | 0,9347 |
| Bất đồng Antweiler - Frank | 6.017 | 0,6017 | 0,4478 | 0,0000 | 1,0000 |
| Độ lệch chuẩn cảm xúc trong ngày | 6.011 | 0,4843 | 0,1696 | 0,0007 | 1,3406 |
| Chú ý: Quy định pháp lý | 6.760 | 0,0219 | 0,0625 | 0,0000 | 1,0000 |
| Chú ý: ETF và tổ chức | 6.760 | 0,2631 | 0,2425 | 0,0000 | 1,0000 |
| Chú ý: An ninh và tấn công | 6.760 | 0,0499 | 0,1151 | 0,0000 | 1,0000 |
| Chú ý: Stablecoin | 6.760 | 0,0104 | 0,0517 | 0,0000 | 1,0000 |
| Chú ý: DeFi | 6.760 | 0,0076 | 0,0543 | 0,0000 | 1,0000 |
| Chú ý: Token AI | 6.760 | 0,0384 | 0,0990 | 0,0000 | 1,0000 |
| Chú ý: Vĩ mô và tiền tệ | 6.760 | 0,0157 | 0,0698 | 0,0000 | 1,0000 |
| Chú ý: Giá và đầu cơ | 6.760 | 0,2672 | 0,2354 | 0,0000 | 1,0000 |
| UCRY Policy (chỉ số) | 3.685 | 105,07 | 6,67 | 100,90 | 131,04 |
| UCRY Price (chỉ số) | 3.685 | 105,84 | 4,87 | 101,74 | 123,06 |
| **Panel C. Mẫu sự kiện theo giờ (cặp tin - tài sản)** |  |  |  |  |  |
| Điểm FinBERT của tin | 148.066 | 0,0435 | 0,5189 | −0,9692 | 0,9445 |
| Điểm Loughran - McDonald của tin | 150.160 | −0,0761 | 0,5434 | −1,0000 | 1,0000 |
| CAR [0, 4] giờ (%) | 150.104 | −0,010 | 1,233 | −12,443 | 44,116 |
| Độ lớn lợi suất bất thường [0, 4] giờ (%) | 150.104 | 0,193 | 1,389 | −7,326 | 44,312 |
| Khối lượng bất thường [0, 4] giờ (log) | 150.104 | 0,150 | 0,624 | −2,336 | 4,068 |

*Ghi chú.* Panel A và B tính trên các quan sát tài sản - ngày có tin trong giai đoạn 01/2023 - 09/2026; Panel C tính trên các cặp tin - tài sản dùng cho phân tích sự kiện. RV nhân với 10⁴. Tính toán của nhóm tác giả.

## 4. Kết quả nghiên cứu và thảo luận

Trước khi trình bày kết quả theo từng câu hỏi nghiên cứu, cần xem xét độ phủ của dữ liệu. Tính đến thời điểm lập bản này, kho tin có 1.352 trong 1.369 ngày có ít nhất một tin (98,8%), gồm 142.646 tin tiếng Anh canonical và 150.160 cặp tin - tài sản dùng cho phân tích sự kiện. Bảng 3 cho thấy số ngày có tin gắn mã của từng tài sản và số ngày dùng được cho mô hình.

**Bảng 3**

*Độ Phủ Tin Và Số Ngày Dùng Cho Mô Hình Theo Tài Sản*

| Tài sản | Ngày lịch | Ngày có tin gắn mã | Tỷ lệ (%) | Ngày dùng cho mô hình | Trong đó dùng chỉ số chung | Huấn luyện | Kiểm tra | Ngoài mẫu |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC | 1.369 | 1.351 | 98,7 | 1.344 | 1 | 890 | 182 | 272 |
| ETH | 1.369 | 1.321 | 96,5 | 1.253 | 31 | 838 | 173 | 242 |
| SOL | 1.369 | 1.212 | 88,5 | 1.035 | 140 | 716 | 148 | 171 |
| BNB | 1.369 | 801 | 58,5 | 866 | 551 | 556 | 121 | 189 |
| XRP | 1.369 | 1.272 | 92,9 | 1.179 | 80 | 784 | 177 | 218 |

*Ghi chú.* "Ngày có tin gắn mã" là số ngày có ít nhất một tin nhắc đến tài sản. Khi ngày không có tin gắn mã nhưng kho tin chung có tin, mô hình dùng chỉ số tính trên toàn thị trường làm tín hiệu thay thế; cột "Trong đó dùng chỉ số chung" là số ngày như vậy. Ngày không có tin nào vẫn là dữ liệu thiếu. Tính toán của nhóm tác giả.

Bảng 3 có nghĩa là với kho tin đầy đủ, BTC, ETH và XRP có tin gắn mã ở trên 90% số ngày, nên chỉ số của các tài sản này phản ánh tin riêng về chúng. Ngược lại, BNB chỉ có tin gắn mã ở 58,5% số ngày và phần lớn ngày dùng cho mô hình phải lấy chỉ số chung của thị trường, nên ước lượng cho BNB không thể diễn giải như tác động riêng của tin về BNB. Điều này được lý giải do tin được gắn mã bằng cách tìm tên hoặc ký hiệu tài sản trong tiêu đề, nên tài sản ít được báo chí nhắc đến xuất hiện trong tiêu đề ít thường xuyên hơn.

Kết quả đầu tiên liên quan đến chất lượng của dữ liệu thời gian, vì mọi kết quả sau đó phụ thuộc vào việc tin được gán đúng ngày. Bảng 4 so sánh các đồng hồ dữ liệu.

**Bảng 4**

*Độ Lệch Giữa Các Đồng Hồ Dữ Liệu Thời Gian*

| So sánh | Số cặp | Lệch trung vị (phút) | Lệch tuyệt đối trung vị (phút) | Lệch tuyệt đối P90 (phút) | Lệch > 1 giờ (%) | Đổi ngày (%) |
|---|---:|---:|---:|---:|---:|---:|
| GDELT: giờ thấy tin - giờ đăng trong trang | 42 | 128,6 | 141,5 | 885,2 | 78,6 | 16,7 |
| SEC: giờ chấp nhận (UTC) - ngày nộp hồ sơ | 2.053 | — | — | — | — | 6,4 |

*Ghi chú.* Độ lệch là giờ so sánh trừ giờ chuẩn, tính bằng phút. "Lệch > 1 giờ" và "Đổi ngày" là tỷ lệ phần trăm số cặp. Với SEC, giờ chuẩn là ngày nộp hồ sơ. Tính toán của nhóm tác giả.

Giờ hệ thống thấy tin của GDELT trễ so với giờ đăng trong trang với độ lệch tuyệt đối trung vị 141,5 phút trên 42 tin kiểm chứng được, trong đó 78,6% lệch hơn một giờ và 16,7% bị chuyển sang ngày UTC khác. Điều này có nghĩa là nếu dùng đồng hồ thấy tin để gán ngày thì khoảng một phần sáu số tin sẽ thuộc ngày hôm sau so với thời điểm thực sự công bố. Điều này được lý giải do GDELT ghi nhận thời điểm hệ thống thu thập bài viết, vốn sau thời điểm nguồn đăng bài. Với hồ sơ của SEC, giờ chấp nhận đổi sang UTC khác với ngày nộp hồ sơ ở 6,4% trong 2.053 hồ sơ, vì hồ sơ nộp sau 17:30 giờ New York được tính sang ngày làm việc kế tiếp. Kết quả này phù hợp với quy tắc ở phương trình (1), theo đó tin được gán vào ngày thấy khi giờ đăng không đáng tin cậy, một lựa chọn có thể làm chậm tín hiệu nhưng không đưa thông tin từ tương lai vào chỉ số. Cần lưu ý chỉ 42 trong 162.936 tin GDELT có giờ đăng hợp lệ vì nhiều trang không công bố giờ đăng kèm múi giờ hoặc không cho phép truy cập tự động, nên hầu hết tin được gán theo giờ thấy tin lần đầu. Đây là lựa chọn thận trọng vì giờ thấy tin không sớm hơn giờ công bố, song nó làm chậm tín hiệu khoảng 142 phút so với thời điểm công bố thật, và có thể làm phản ứng ngay sau tin bị ước lượng thấp.

Đối với RQ1, nghiên cứu trước hết so sánh độ chính xác của các thước đo cảm xúc với nhãn yếu từ phiếu bình chọn của người dùng CryptoPanic, trình bày ở Bảng 5.

**Bảng 5**

*Độ Chính Xác Của Các Thước Đo Trên Nhãn Yếu Và Nhãn Thủ Công*

| Thước đo | Số tin | Độ chính xác | F1 trung bình | AUC | Phân định (%) |
|---|---:|---:|---:|---:|---:|
| **Panel A. Nhãn yếu CryptoPanic** |  |  |  |  |  |
| Loughran - McDonald | 6.995 | 0,155 | 0,184 | 0,612 | 25,8 |
| Harvard IV-4 | 6.995 | 0,312 | 0,245 | 0,571 | 49,2 |
| FinBERT | 6.995 | 0,748 | 0,637 | 0,712 | 100,0 |
| CryptoBERT | 6.995 | 0,802 | 0,520 | 0,591 | 100,0 |
| **Panel B. Cảm xúc, nhãn thủ công** |  |  |  |  |  |
| Loughran - McDonald | 300 | 0,553 | 0,460 | 0,718 | — |
| Harvard IV-4 | 300 | 0,487 | 0,459 | 0,726 | — |
| FinBERT | 300 | 0,580 | 0,531 | 0,894 | — |
| **Panel C. Câu chuyện thị trường, nhãn thủ công** |  |  |  |  |  |
| LDA | 300 | 0,187 | 0,091 | — | — |
| BERTopic | 300 | 0,370 | 0,229 | — | — |
| Zero-shot (vectơ nhúng) | 300 | 0,377 | 0,333 | — | — |

*Ghi chú.* Panel A gồm 6.995 tiêu đề CryptoPanic có ít nhất 03 phiếu và chênh lệch phiếu tích cực và tiêu cực từ 02 phiếu trở lên, trong đó 81,6% có nhãn tích cực; "Phân định" là tỷ lệ tin mà thước đo cho điểm khác 0, điểm bằng 0 được tính là dự đoán sai. Panel B và C gồm 300 tiêu đề chọn ngẫu nhiên trước kỳ đánh giá, gán ba nhãn cảm xúc (tích cực, trung tính, tiêu cực) và một trong 08 câu chuyện thị trường hoặc nhóm khác; AUC tính trên các tiêu đề tích cực và tiêu cực. Tính toán của nhóm tác giả.

Kết quả ở Bảng 5 cho thấy FinBERT đạt AUC 0,712, cao hơn từ điển Loughran - McDonald (0,612), Harvard IV-4 (0,571) và CryptoBERT (0,591). Điều này có nghĩa là FinBERT xếp hạng tin tốt cao hơn tin xấu đúng hơn các thước đo còn lại, nên RQ1 được ủng hộ về khả năng phân biệt sắc thái trên tiêu đề tin tiền mã hóa. Điều này được lý giải do hai từ điển chỉ phân định được 26% và 49% số tiêu đề, vì tiêu đề ngắn hiếm khi chứa từ thuộc danh sách, còn mô hình chuyển đổi cho điểm mọi tiêu đề. Độ chính xác cao của CryptoBERT (0,802) chủ yếu phản ánh việc mô hình gần như luôn dự đoán nhãn tích cực trong khi 81,6% nhãn là tích cực, và điều này thể hiện ở F1 trung bình (0,520) và AUC (0,591) thấp hơn FinBERT, hàm ý rằng mô hình huấn luyện trên bài đăng mạng xã hội chưa chuyển tốt sang tiêu đề tin. Kết quả này tương đồng với kết luận của Loughran và McDonald (2011) rằng công cụ đo phải phù hợp với loại văn bản, và với Araci (2019) về lợi thế của mô hình chuyển đổi so với danh sách từ. Cần lưu ý nhãn yếu phản ánh kỳ vọng giá của đám đông người dùng chứ không phải đánh giá giọng điệu của chuyên gia. Kết quả trên 300 tiêu đề do nhóm tác giả gán nhãn thủ công ở Panel B của Bảng 5 củng cố nhận định này: FinBERT đạt AUC 0,894, cao hơn rõ so với Loughran - McDonald (0,718) và Harvard IV-4 (0,726), và có F1 trung bình cao nhất (0,531). Độ chính xác của mọi thước đo chỉ ở mức trung bình (FinBERT 0,580) vì 58,0% tiêu đề được gán nhãn trung tính, nhóm mà các thước đo khó tách khỏi tin tốt hoặc tin xấu nhẹ. Đối với câu chuyện thị trường, Panel C cho thấy phân loại zero-shot đạt độ chính xác 0,377 và F1 trung bình 0,333, cao hơn BERTopic (0,370; 0,229) và LDA (0,187; 0,091), nhưng độ chính xác này vẫn thấp hơn tỷ lệ 42,0% tiêu đề mà người gán xếp vào nhóm khác. Điều này có nghĩa là zero-shot nhận diện các câu chuyện định trước tốt hơn hai mô hình chủ đề, song xếp nhiều tiêu đề không thuộc 08 câu chuyện vào một câu chuyện cụ thể, nên các biến chú ý cần được hiểu là thước đo có nhiễu và kết quả không có ý nghĩa ở RQ3 có thể một phần do sai số đo lường.

Tiếp theo, RQ1 cũng hỏi liệu cảm xúc đo bằng mô hình chuyển đổi giải thích kết quả thị trường tốt hơn từ điển hay không. Bảng 6 trình bày hệ số của ba thước đo cảm xúc trong hồi quy dự báo (8) với độ trễ một ngày.

**Bảng 6**

*Hệ Số Cảm Xúc Trong Hồi Quy Dự Báo Một Ngày*

| Tài sản | Loughran - McDonald | Harvard IV-4 | FinBERT |
|---|---:|---:|---:|
| **Panel A. Lợi suất log ngày t + 1** |  |  |  |
| BTC | −0,00042 (0,00548) | 0,00651 (0,00478) | 0,00328 (0,00676) |
| ETH | 0,00269 (0,00622) | 0,00454 (0,00481) | 0,00639 (0,00608) |
| SOL | −0,00624 (0,00622) | −0,00041 (0,00506) | 0,00890 (0,00634) |
| BNB | −0,00239 (0,00529) | 0,00751** (0,00345) | 0,01037** (0,00456) |
| XRP | −0,00563 (0,00546) | 0,00328 (0,00530) | −0,00304 (0,00798) |
| **Panel B. Biến động thực hiện RV ngày t + 1** |  |  |  |
| BTC | 0,00034* (0,00019) | 0,00005 (0,00013) | 0,00000 (0,00020) |
| ETH | 0,00018 (0,00026) | 0,00036* (0,00019) | 0,00056* (0,00031) |
| SOL | −0,00108*** (0,00036) | −0,00067** (0,00029) | −0,00026 (0,00030) |
| BNB | −0,00029 (0,00021) | 0,00024 (0,00018) | −0,00002 (0,00018) |
| XRP | −0,00071 (0,00050) | −0,00005 (0,00052) | −0,00147 (0,00118) |
| **Panel C. Log khối lượng ngày t + 1** |  |  |  |
| BTC | 0,30546** (0,13077) | 0,10663 (0,10495) | 0,26038** (0,11963) |
| ETH | 0,13061 (0,08194) | 0,07246 (0,06176) | 0,19400*** (0,07444) |
| SOL | −0,01337 (0,06231) | −0,10448* (0,05439) | −0,01366 (0,06526) |
| BNB | −0,10293 (0,08584) | 0,12398 (0,07827) | −0,06547 (0,07330) |
| XRP | −0,03243 (0,06965) | −0,03586 (0,05825) | −0,08161 (0,07666) |

*Ghi chú.* Hệ số của biến cảm xúc trong phương trình (8) với h = 1, sai số chuẩn Newey - West trong ngoặc. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh. Mẫu là các ngày trong kỳ huấn luyện và kiểm tra. Tính toán của nhóm tác giả.

Trong tổng số 45 hệ số cho mỗi thước đo (05 tài sản, 03 biến mục tiêu và 03 độ trễ), có 7 hệ số của FinBERT, 5 hệ số của Loughran - McDonald và 6 hệ số của Harvard IV-4 đạt mức ý nghĩa 10% khi chưa hiệu chỉnh, trong khi nếu không có mối liên hệ nào thì số hệ số kỳ vọng ở mức này chỉ khoảng 4,5. Sau khi hiệu chỉnh Holm, còn 0 hệ số đạt mức 10%. Điều này có nghĩa là nghiên cứu chưa tìm thấy bằng chứng có ý nghĩa thống kê cho thấy cảm xúc của ngày t dự báo lợi suất, biến động hay khối lượng của các ngày tiếp theo khi đã kiểm soát các biến thị trường. Điều này được lý giải do phần lớn phương sai của biến động và khối lượng đã được giải thích bởi giá trị trễ của chính chúng, và thị trường tiền mã hóa phản ứng nhanh với thông tin công khai theo giả thuyết thị trường hiệu quả (Fama, 1970), điều mà Gür và Ünal (2026) cũng ghi nhận khi giá trễ giải thích phần lớn biến động giá Bitcoin. Về so sánh giữa các thước đo, FinBERT có 7 hệ số đạt mức 10% so với 5 và 6 của hai từ điển, một chênh lệch nhỏ so với mức nhiễu mẫu, nên hồi quy dự báo chưa đủ để xếp hạng các thước đo và RQ1 chủ yếu dựa vào kết quả ở Bảng 5.

Đối với RQ3, nghiên cứu xét phản ứng của lợi suất, độ lớn lợi suất và khối lượng giao dịch quanh thời điểm công bố theo từng câu chuyện thị trường. Bảng 7 trình bày kết quả trong cửa sổ bốn giờ sau tin.

**Bảng 7**

*Phản Ứng Của Giá Và Khối Lượng Quanh Tin Theo Câu Chuyện Thị Trường*

| Nhóm tin | Cặp tin - tài sản | Số ngày | CAR (%) | Độ lớn lợi suất bất thường (%) | Khối lượng bất thường (log) | p Holm nhỏ nhất |
|---|---:|---:|---:|---:|---:|---:|
| Toàn bộ | 150.104 | 1.363 | −0,007 | 0,054** | 0,033** | 1,000 |
| Quy định pháp lý | 14.123 | 1.333 | −0,005 | 0,018 | 0,013 | 1,000 |
| ETF và tổ chức | 40.425 | 1.352 | −0,017 | 0,055** | 0,035** | 1,000 |
| An ninh và tấn công | 17.235 | 1.350 | −0,011 | 0,059** | 0,028** | 1,000 |
| Stablecoin | 3.474 | 1.105 | 0,011 | 0,069** | 0,071*** | 0,008 |
| DeFi | 1.405 | 769 | 0,051 | 0,202*** | 0,122*** | < 0,001 |
| Token AI | 11.878 | 1.325 | −0,005 | 0,072*** | 0,045*** | 0,496 |
| Vĩ mô và tiền tệ | 3.479 | 1.131 | 0,022 | 0,119*** | 0,093*** | < 0,001 |
| Giá và đầu cơ | 28.711 | 1.348 | −0,012 | 0,056** | 0,039*** | 0,989 |
| Nhóm khác | 29.374 | 1.357 | 0,009 | 0,065** | 0,038*** | 0,989 |

*Ghi chú.* Cửa sổ [0, 4] giờ sau T_0. CAR và độ lớn lợi suất bất thường tính bằng điểm phần trăm; khối lượng bất thường là chênh lệch logarit khối lượng USD so với trung bình 144 giờ trước tin. Số ngày là số ngày có sự kiện. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value của kiểm định t chưa hiệu chỉnh; cột cuối là p-value Holm nhỏ nhất trong ba chỉ tiêu. Tính toán của nhóm tác giả.

Trên toàn bộ 150.160 cặp tin - tài sản, lợi suất bất thường tích lũy trung bình trong cửa sổ [0, 4] giờ là −0,007 điểm phần trăm (p Holm = 1,000), và không câu chuyện nào có CAR khác 0 một cách có ý nghĩa sau hiệu chỉnh Holm. Ngược lại, khối lượng giao dịch bất thường trong giờ đầu sau tin là 0,059 log điểm (p Holm = 0,005), và trong cửa sổ bốn giờ ở Bảng 7, tin về DeFi, vĩ mô và tiền tệ, stablecoin có khối lượng bất thường lần lượt 0,122, 0,093 và 0,071 log điểm, đạt ý nghĩa sau hiệu chỉnh Holm và cao hơn các nhóm tin phổ biến như quy định pháp lý (0,013) hay ETF và nhà đầu tư tổ chức (0,035). Điều này có nghĩa là câu chuyện thị trường không quyết định hướng giá sau tin nhưng gắn với mức độ hoạt động giao dịch khác nhau, trong đó các chủ đề chuyên biệt và ít xuất hiện kéo theo khối lượng giao dịch bất thường lớn hơn. Điều này có thể được lý giải do các chủ đề này xuất hiện thưa nên mỗi tin mang nhiều thông tin mới hơn, trong khi tin về quy định hay ETF xuất hiện dày đặc nên phản ứng riêng của từng tin bị pha loãng. Kết quả về giá khác với Auer và Claessens (2018) vốn ghi nhận phản ứng lớn đối với các tin pháp lý, nhưng mẫu của họ là 151 tin được chọn lọc, còn nghiên cứu này dùng toàn bộ dòng tin tự động. Trong mô hình hồi quy theo ngày, sự chú ý đến các câu chuyện thị trường có 45 trong 315 hệ số đạt mức 10% trước hiệu chỉnh, so với khoảng 31,5 hệ số kỳ vọng nếu không có quan hệ nào, và 0 hệ số đạt mức này sau hiệu chỉnh Holm. Do đó, ở tần suất ngày, nghiên cứu chưa thể xếp hạng các câu chuyện theo mức liên hệ với lợi suất, biến động và khối lượng, khác với Walker (2024) vốn ghi nhận câu chuyện về tội phạm đi kèm lợi suất tuần sau trong một giai đoạn nhất định.

Tiếp theo, đối với RQ2, nghiên cứu kiểm định tính bất đối xứng theo hai cách. Bảng 8 trình bày kết quả kiểm định Wald trên hồi quy theo ngày (phương trình (9) và (10)), còn Bảng 9 trình bày chênh lệch phản ứng quanh tin giữa nhóm tin xấu và nhóm tin tốt.

**Bảng 8**

*Kiểm Định Bất Đối Xứng Giữa Tin Xấu Và Tin Tốt Đối Với Biến Động*

| Tài sản | Độ trễ h (ngày) | β⁻ | β⁺ | Số quan sát | W | p | p Holm |
|---|---:|---:|---:|---:|---:|---:|---:|
| BTC | 1 | −0,00126 | −0,00108 | 1.072 | 0,152 | 0,696 | 1,000 |
| ETH | 1 | 0,00066 | 0,00139 | 1.011 | 3,049 | 0,081* | 1,000 |
| SOL | 1 | 0,00064 | 0,00004 | 864 | 0,522 | 0,470 | 1,000 |
| BNB | 1 | 0,00007 | −0,00004 | 677 | 0,087 | 0,767 | 1,000 |
| XRP | 1 | 0,00233 | −0,00083 | 961 | 0,957 | 0,328 | 1,000 |
| BTC | 3 | 0,00053 | 0,00055 | 1.070 | 0,001 | 0,972 | 1,000 |
| ETH | 3 | −0,00108 | −0,00015 | 1.009 | 3,267 | 0,071* | 0,990 |
| SOL | 3 | 0,00408 | 0,00102 | 861 | 6,498 | 0,011** | 0,162 |
| BNB | 3 | −0,00023 | −0,00028 | 675 | 0,033 | 0,855 | 1,000 |
| XRP | 3 | −0,00192 | −0,00199 | 959 | 0,008 | 0,927 | 1,000 |
| BTC | 7 | −0,00059 | −0,00089 | 1.066 | 0,494 | 0,482 | 1,000 |
| ETH | 7 | 0,00100 | 0,00038 | 1.005 | 0,947 | 0,330 | 1,000 |
| SOL | 7 | 0,00133 | 0,00045 | 860 | 1,127 | 0,288 | 1,000 |
| BNB | 7 | 0,00098 | 0,00104 | 673 | 0,019 | 0,889 | 1,000 |
| XRP | 7 | −0,00095 | −0,00071 | 956 | 0,030 | 0,863 | 1,000 |

*Ghi chú.* β⁻ và β⁺ là hệ số của NegSent và PosSent trong phương trình (9) với biến phụ thuộc là RV; W là thống kê Wald của giả thuyết β⁻ = β⁺ với phân phối χ²(1). ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh; cột cuối là p-value đã hiệu chỉnh Holm. Tính toán của nhóm tác giả.

**Bảng 9**

*Chênh Lệch Phản Ứng Quanh Tin Giữa Nhóm Tin Xấu Và Tin Tốt*

| Thước đo cảm xúc | Cửa sổ (giờ) | Chỉ tiêu | Số ngày | Tin xấu | Tin tốt | Chênh lệch | p Holm |
|---|---|---|---:|---:|---:|---:|---:|
| FinBERT | [0,1] | CAR (%) | 1.352 | 0,004 | −0,008 | 0,012** | 0,197 |
| FinBERT | [0,1] | Độ lớn lợi suất (%) | 1.352 | 0,030 | 0,046 | −0,016*** | 0,013 |
| FinBERT | [0,1] | Khối lượng (log) | 1.352 | 0,042 | 0,073 | −0,031*** | < 0,001 |
| FinBERT | [0,4] | CAR (%) | 1.352 | −0,002 | −0,016 | 0,014* | 0,431 |
| FinBERT | [0,4] | Độ lớn lợi suất (%) | 1.352 | 0,047 | 0,071 | −0,024*** | 0,054 |
| FinBERT | [0,4] | Khối lượng (log) | 1.352 | 0,022 | 0,051 | −0,028*** | < 0,001 |
| FinBERT | [0,24] | CAR (%) | 1.351 | −0,015 | −0,064 | 0,048*** | 0,049 |
| FinBERT | [0,24] | Độ lớn lợi suất (%) | 1.351 | 0,041 | 0,073 | −0,032 | 0,431 |
| FinBERT | [0,24] | Khối lượng (log) | 1.351 | 0,003 | 0,012 | −0,009*** | < 0,001 |
| Loughran - McDonald | [0,1] | CAR (%) | 1.343 | 0,003 | −0,011 | 0,014 | 0,431 |
| Loughran - McDonald | [0,1] | Độ lớn lợi suất (%) | 1.343 | 0,021 | 0,048 | −0,027*** | 0,011 |
| Loughran - McDonald | [0,1] | Khối lượng (log) | 1.343 | 0,033 | 0,083 | −0,050*** | < 0,001 |
| Loughran - McDonald | [0,4] | CAR (%) | 1.343 | −0,001 | −0,024 | 0,023* | 0,431 |
| Loughran - McDonald | [0,4] | Độ lớn lợi suất (%) | 1.343 | 0,038 | 0,086 | −0,048*** | 0,011 |
| Loughran - McDonald | [0,4] | Khối lượng (log) | 1.343 | 0,014 | 0,058 | −0,044*** | < 0,001 |
| Loughran - McDonald | [0,24] | CAR (%) | 1.342 | −0,009 | −0,046 | 0,036 | 0,431 |
| Loughran - McDonald | [0,24] | Độ lớn lợi suất (%) | 1.342 | 0,034 | 0,112 | −0,078** | 0,184 |
| Loughran - McDonald | [0,24] | Khối lượng (log) | 1.342 | 0,002 | 0,013 | −0,012*** | 0,002 |

*Ghi chú.* Tin xấu và tin tốt là tam phân vị dưới và trên của điểm FinBERT (ngưỡng tính trên kỳ huấn luyện), hoặc điểm Loughran - McDonald âm và dương. Chênh lệch là giá trị trung bình của nhóm xấu trừ nhóm tốt, tính theo ngày sự kiện. CAR và độ lớn lợi suất tính bằng điểm phần trăm. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value của kiểm định t chưa hiệu chỉnh. Tính toán của nhóm tác giả.

Kiểm định Wald ở Bảng 8 bác bỏ giả thuyết β⁻ = β⁺ ở mức 10% đối với 3 trong 15 cặp tài sản - độ trễ khi chưa hiệu chỉnh, và 0 cặp sau hiệu chỉnh Holm. Điều này có nghĩa là nghiên cứu chưa tìm thấy bằng chứng có ý nghĩa thống kê rằng tin xấu và tin tốt có tác động khác nhau lên biến động theo ngày. Hồi quy phân vị cho kết luận gần tương tự, với 1 trong 45 kiểm định (05 tài sản, 03 độ trễ, 03 phân vị) đạt mức 10% sau hiệu chỉnh Holm; vì sai số chuẩn của hồi quy phân vị chưa hiệu chỉnh tự tương quan, kết quả đơn lẻ này chưa đủ để coi là bằng chứng bất đối xứng. Ở phản ứng quanh tin, Bảng 9 cho thấy trong cửa sổ [0, 1] giờ, chênh lệch giữa nhóm tin xấu và nhóm tin tốt theo FinBERT là −0,031 log điểm về khối lượng giao dịch (p Holm < 0,001) và −0,016 điểm phần trăm về độ lớn lợi suất bất thường (p Holm = 0,013), và phân loại theo từ điển Loughran - McDonald cho kết quả cùng chiều. Dấu âm của các chênh lệch có nghĩa là tin tích cực đi kèm hoạt động giao dịch và biến động giá mạnh hơn tin tiêu cực, trái với kỳ vọng rằng tin xấu có tác động mạnh hơn. Bên cạnh đó, trong cửa sổ [0, 24] giờ, CAR sau tin tốt thấp hơn sau tin xấu 0,048 điểm phần trăm (p Holm = 0,049), gợi ý giá có xu hướng điều chỉnh giảm sau tin tốt. Điều này có thể được lý giải do tin tích cực thường được đăng sau các đợt tăng giá, thu hút cả nhà đầu tư mới lẫn giao dịch chốt lời, nên hoạt động giao dịch tăng mạnh nhưng giá sau đó điều chỉnh. Kết quả này khác với Gür và Ünal (2026) về phản ứng mạnh hơn với tin tiêu cực, và khác với Chou và cộng sự (2023) và Kao và cộng sự (2024) về vai trò của tin tiêu cực đối với lợi suất. Do đó, RQ2 được ủng hộ theo nghĩa tồn tại bất đối xứng, nhưng theo chiều ngược với kỳ vọng và thể hiện ở hoạt động giao dịch trong ngày hơn là ở biến động theo ngày. Hình 1 minh họa lợi suất bất thường tích lũy theo nhóm cảm xúc của tin ở các cửa sổ sau tin.

**Hình 1**

*Lợi Suất Bất Thường Tích Lũy Theo Nhóm Cảm Xúc Của Tin*

![Lợi suất bất thường tích lũy theo nhóm cảm xúc của tin](../outputs/figures/real/event_car_by_tone.png)

*Ghi chú.* Trung bình theo ngày sự kiện của CAR (đơn vị phần trăm) theo ba nhóm tam phân vị của điểm FinBERT (negative là nhóm tin xấu, middle là nhóm giữa, positive là nhóm tin tốt) ở các cửa sổ sau tin; các điểm không kèm khoảng tin cậy.

Đối với RQ4, nghiên cứu xem xét ba khía cạnh là giá có chạy trước tin hay không, chiều dẫn dắt giữa cảm xúc và giá theo ngày, và liệu kết luận có phụ thuộc vào đồng hồ dùng để gán thời điểm. Về khía cạnh thứ nhất, lợi suất bất thường tích lũy trong cửa sổ [-4, -2] giờ trước tin là −0,002 điểm phần trăm (p Holm = 1,000), nên nghiên cứu chưa ghi nhận dấu hiệu giá đã dịch chuyển có hướng trước khi tin xuất hiện. Tuy nhiên, độ lớn lợi suất bất thường và khối lượng giao dịch trước tin đều lớn hơn bình thường một cách có ý nghĩa sau hiệu chỉnh (khối lượng bất thường 0,075 log điểm, p Holm < 0,001), ở mức tương đương với giờ đầu sau tin. Về khía cạnh thứ hai, Bảng 10 cho thấy lợi suất dẫn trước cảm xúc FinBERT ở cả 05 tài sản sau hiệu chỉnh Holm, trong khi cảm xúc dẫn trước lợi suất ở 2 tài sản khi chưa hiệu chỉnh và 0 tài sản sau hiệu chỉnh; với RV, có 0 kiểm định có ý nghĩa sau hiệu chỉnh. Điều này có nghĩa là văn bản tin tức chủ yếu phản ánh diễn biến giá đã xảy ra hơn là báo trước giá, và giải thích vì sao hoạt động giao dịch đã tăng từ trước mốc công bố. Điều này được lý giải do một phần đáng kể tin tiền mã hóa mô tả chính biến động giá, nên giọng điệu của tin đi theo lợi suất của các ngày trước. Kết quả này tương đồng với Kraaijeveld và De Smedt (2020), những người ghi nhận giá dẫn dắt cảm xúc trên Twitter ở nhiều đồng tiền, và hàm ý rằng quan hệ đồng thời giữa tin và giá không nên được diễn giải là tin làm thay đổi giá. Về khía cạnh thứ ba, Bảng 11 so sánh phản ứng khi gán thời điểm theo giờ đăng và theo giờ thấy tin trên các tin có đủ hai đồng hồ.

**Bảng 10**

*Kiểm Định Granger Giữa Cảm Xúc Và Biến Thị Trường*

| Tài sản | Biến thị trường | Chiều kiểm định | Số quan sát | Độ trễ | p | p Holm |
|---|---|---|---|---:|---:|---:|
| BNB | ret | sent_finbert → ret | 896 | 1 | 0,008*** | 0,120 |
| BNB | ret | ret → sent_finbert | 896 | 1 | < 0,001*** | < 0,001 |
| BNB | rv | sent_finbert → rv | 813 | 7 | 0,476 | 1,000 |
| BNB | rv | rv → sent_finbert | 813 | 7 | 0,388 | 1,000 |
| BTC | ret | sent_finbert → ret | 896 | 7 | 0,102 | 1,000 |
| BTC | ret | ret → sent_finbert | 896 | 7 | < 0,001*** | < 0,001 |
| BTC | rv | sent_finbert → rv | 813 | 7 | 0,433 | 1,000 |
| BTC | rv | rv → sent_finbert | 813 | 7 | 0,274 | 1,000 |
| ETH | ret | sent_finbert → ret | 896 | 3 | 0,878 | 1,000 |
| ETH | ret | ret → sent_finbert | 896 | 3 | < 0,001*** | < 0,001 |
| ETH | rv | sent_finbert → rv | 813 | 3 | 0,238 | 1,000 |
| ETH | rv | rv → sent_finbert | 813 | 3 | 0,025** | 0,347 |
| SOL | ret | sent_finbert → ret | 896 | 4 | 0,025** | 0,347 |
| SOL | ret | ret → sent_finbert | 896 | 4 | < 0,001*** | < 0,001 |
| SOL | rv | sent_finbert → rv | 813 | 1 | 0,459 | 1,000 |
| SOL | rv | rv → sent_finbert | 813 | 1 | 0,668 | 1,000 |
| XRP | ret | sent_finbert → ret | 896 | 2 | 0,307 | 1,000 |
| XRP | ret | ret → sent_finbert | 896 | 2 | < 0,001*** | < 0,001 |
| XRP | rv | sent_finbert → rv | 813 | 4 | 0,139 | 1,000 |
| XRP | rv | rv → sent_finbert | 813 | 4 | 0,104 | 1,000 |

*Ghi chú.* Mô hình VAR hai chiều theo phương trình (11) trên chuỗi ngày liên tục dài nhất của từng tài sản trong kỳ huấn luyện và kiểm tra; yêu cầu tối thiểu 30 quan sát liên tục. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

**Bảng 11**

*Độ Nhạy Của Phản Ứng Giá Với Đồng Hồ Gán Thời Điểm*

| Cửa sổ (giờ) | Cặp / ngày | CAR theo giờ đăng (%) | CAR theo giờ thấy (%) | p Holm (giờ đăng) | p Holm (giờ thấy) | p Holm (chênh lệch ghép cặp) |
|---|---:|---:|---:|---:|---:|---:|
| [0,1] | 38 / 31 | −0,008 | −0,127 | 0,951 | 0,199 | 0,725 |
| [0,4] | 38 / 31 | −0,247 | −0,199 | 0,431 | 0,221 | 0,821 |
| [0,24] | 38 / 31 | −0,503 | −0,866* | 0,431 | 0,078 | 0,363 |

*Ghi chú.* CAR tính bằng điểm phần trăm. Dấu sao ở hai cột CAR biểu thị mức ý nghĩa của p-value đã hiệu chỉnh Holm trong họ ba cửa sổ, đối với giả thuyết CAR khác 0. Cột cuối là p-value Holm của kiểm định t ghép cặp về chênh lệch giữa hai đồng hồ. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

Bảng 11 cho thấy trên 38 cặp tin - tài sản có đủ hai đồng hồ, CAR trong cửa sổ [0, 24] giờ là −0,503 điểm phần trăm khi gán theo giờ đăng và −0,866 điểm phần trăm khi gán theo giờ thấy tin. Kết luận về ý nghĩa thống kê không thay đổi giữa hai đồng hồ ở cả ba cửa sổ sau hiệu chỉnh Holm, nên với mẫu hiện có việc chọn đồng hồ chưa làm đổi kết luận. Cần lưu ý số cặp tin có đủ hai đồng hồ rất nhỏ nên các kiểm định này có độ mạnh thấp. Ngoài ra, ở cửa sổ [-4, 0] giờ, CAR của nhóm tin xấu và nhóm tin tốt theo FinBERT khác nhau có ý nghĩa sau hiệu chỉnh (Bảng 9), củng cố kết quả Granger rằng sắc thái của tin đi theo biến động giá vừa xảy ra.

Đối với RQ5, Bảng 12 trình bày độ chính xác dự báo ngoài mẫu của BTC theo ba mô hình và ba phiên bản đặc trưng với độ trễ một ngày.

**Bảng 12**

*Dự Báo Ngoài Mẫu Của BTC Với Độ Trễ Một Ngày*

| Mô hình | Phiên bản đặc trưng | Số ngày | RMSE | R²OS | p (DM) | p (CW) |
|---|---|---:|---:|---:|---:|---:|
| **Panel A. Biến động thực hiện RV ngày t + 1** |  |  |  |  |  |  |
| Elastic Net | Chỉ thị trường | 272 | 5,413 | 0,2465 | — | — |
| Elastic Net | + số tin thô | 272 | 5,430 | 0,2420 | — | — |
| Elastic Net | + văn bản | 272 | 5,552 | 0,2073 | 0,161 | 0,785 |
| XGBoost | Chỉ thị trường | 272 | 5,722 | 0,1581 | — | — |
| XGBoost | + số tin thô | 272 | 5,561 | 0,2048 | — | — |
| XGBoost | + văn bản | 272 | 5,375 | 0,2571 | 0,020** | 0,006*** |
| LightGBM | Chỉ thị trường | 272 | 5,321 | 0,2720 | — | — |
| LightGBM | + số tin thô | 272 | 5,384 | 0,2546 | — | — |
| LightGBM | + văn bản | 272 | 5,405 | 0,2489 | 0,669 | 0,235 |
| **Panel B. Lợi suất log ngày t + 1** |  |  |  |  |  |  |
| Elastic Net | Chỉ thị trường | 272 | 0,02416 | −0,0006 | — | — |
| Elastic Net | + số tin thô | 272 | 0,02416 | −0,0006 | — | — |
| Elastic Net | + văn bản | 272 | 0,02416 | −0,0005 | 0,994 | 0,434 |
| XGBoost | Chỉ thị trường | 272 | 0,02432 | −0,0141 | — | — |
| XGBoost | + số tin thô | 272 | 0,02430 | −0,0121 | — | — |
| XGBoost | + văn bản | 272 | 0,02442 | −0,0224 | 0,540 | 0,388 |
| LightGBM | Chỉ thị trường | 272 | 0,02441 | −0,0216 | — | — |
| LightGBM | + số tin thô | 272 | 0,02445 | −0,0247 | — | — |
| LightGBM | + văn bản | 272 | 0,02430 | −0,0122 | 0,776 | 0,111 |

*Ghi chú.* RMSE của RV nhân với 10⁴. R²OS là R² ngoài mẫu so với trung bình lịch sử theo phương trình (14). p (DM) và p (CW) là p-value của kiểm định Diebold - Mariano có hiệu chỉnh mẫu nhỏ và kiểm định Clark - West khi so mô hình có văn bản với mô hình chỉ có biến thị trường; ký hiệu "—" là không áp dụng. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

Trên toàn bộ 30 cặp (05 tài sản, 03 mô hình và 02 biến mục tiêu là lợi suất và RV), mô hình bổ sung văn bản có R² ngoài mẫu cao hơn mô hình chỉ có biến thị trường ở 9 cặp, và chênh lệch có ý nghĩa ở mức 10% theo kiểm định Diebold - Mariano hoặc Clark - West trước hiệu chỉnh ở 7 cặp, còn sau hiệu chỉnh Holm là 0 cặp. Các kiểm định này chỉ dùng những ngày mà mọi phiên bản mô hình đều có dự báo, tối đa 235 quan sát chung cho mỗi cặp. Điều này có nghĩa là nghiên cứu chưa tìm thấy bằng chứng có ý nghĩa thống kê rằng văn bản cải thiện dự báo ngoài mẫu so với mô hình chỉ có biến thị trường, và với chỉ 9/30 cặp có R² ngoài mẫu cao hơn, văn bản thường làm dự báo kém đi do thêm nhiễu. Điều này được lý giải do biến động có tính bền cao nên giá trị trễ của chính nó đã chứa phần lớn thông tin, và theo kết quả Granger ở trên, giọng điệu tin chủ yếu đi sau lợi suất nên ít thông tin mới về tương lai, tương tự nhận định của Gür và Ünal (2026) rằng giá trễ giải thích phần lớn biến động giá Bitcoin. Kết quả này khác với Ortu và cộng sự (2022) và Loginova và cộng sự (2024), những nghiên cứu ghi nhận mô hình có văn bản tốt hơn mô hình chỉ có biến kỹ thuật, nhưng các nghiên cứu đó đo độ chính xác phân loại hướng giá và không dùng kiểm định bội cho chênh lệch dự báo. Hình 2 cho thấy sai số bình phương trung bình trượt của dự báo lợi suất BTC theo ba phiên bản đặc trưng.

Bên cạnh đó, Bảng 13 trình bày kiểm định giá trị dự báo có điều kiện của Giacomini và White (2006) giữa mô hình có văn bản và mô hình chỉ có biến thị trường.

**Bảng 13**

*Kiểm Định Giá Trị Dự Báo Có Điều Kiện Giacomini - White*

| Tài sản | Biến mục tiêu | Độ trễ h | Số quan sát | Elastic Net | XGBoost | LightGBM |
|---|---|---|---:|---:|---:|---:|
| BNB | Lợi suất | 1 | 16 | 1,000 | 1,000 | 1,000 |
| BNB | RV | 1 | 16 | 1,000 | 1,000 | 1,000 |
| BTC | Lợi suất | 1 | 235 | 1,000 | 1,000 | 1,000 |
| BTC | RV | 1 | 235 | 1,000 | 1,000 | 1,000 |
| ETH | Lợi suất | 1 | 60 | 1,000 | 1,000 | 1,000 |
| ETH | RV | 1 | 60 | 1,000 | 1,000 | 1,000 |
| SOL | Lợi suất | 1 | 13 | 1,000 | 1,000 | 1,000 |
| SOL | RV | 1 | 13 | 1,000 | 1,000 | 1,000 |
| XRP | Lợi suất | 1 | 19 | 1,000 | 1,000 | 1,000 |
| XRP | RV | 1 | 19 | 1,000 | 1,000 | 1,000 |
| BNB | Lợi suất | 3 | 16 | 1,000 | 1,000 | 1,000 |
| BNB | RV | 3 | 16 | 1,000 | 1,000 | 1,000 |
| BTC | Lợi suất | 3 | 235 | 1,000 | 1,000 | 1,000 |
| BTC | RV | 3 | 235 | 1,000 | 1,000 | 1,000 |
| ETH | Lợi suất | 3 | 60 | 1,000 | 1,000 | 1,000 |
| ETH | RV | 3 | 60 | 1,000 | 1,000 | 1,000 |
| SOL | Lợi suất | 3 | 13 | 1,000 | 1,000 | 1,000 |
| SOL | RV | 3 | 13 | < 0,001*** | 0,767 | 0,001*** |
| XRP | Lợi suất | 3 | 19 | 1,000 | 1,000 | 1,000 |
| XRP | RV | 3 | 19 | 1,000 | 1,000 | 1,000 |
| BNB | Lợi suất | 7 | 16 | 1,000 | 1,000 | 1,000 |
| BNB | RV | 7 | 16 | 0,575 | 0,150 | 1,000 |
| BTC | Lợi suất | 7 | 235 | 1,000 | 1,000 | 1,000 |
| BTC | RV | 7 | 235 | 1,000 | 1,000 | 1,000 |
| ETH | Lợi suất | 7 | 60 | 0,472 | 1,000 | 1,000 |
| ETH | RV | 7 | 60 | < 0,001*** | 1,000 | 1,000 |
| SOL | Lợi suất | 7 | 13 | 1,000 | 1,000 | 1,000 |
| SOL | RV | 7 | 13 | < 0,001*** | 1,000 | 1,000 |
| XRP | Lợi suất | 7 | 19 | 1,000 | 0,647 | 1,000 |
| XRP | RV | 7 | 19 | 0,142 | 0,902 | 1,000 |

*Ghi chú.* Giá trị trong ô là p-value đã hiệu chỉnh Holm của thống kê Giacomini - White với giả thuyết không là hai mô hình có cùng sai số dự báo có điều kiện; kiểm định không cho biết mô hình nào tốt hơn. Số quan sát là số ngày chung lớn nhất trong cửa sổ cuộn 500 ngày. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

Có 4 trong 90 kiểm định bác bỏ giả thuyết không ở mức 10% sau hiệu chỉnh Holm, trong khi số quan sát chung chỉ từ 13 đến 235 ngày. Điều này có nghĩa là trong phần lớn trường hợp, nghiên cứu chưa tìm thấy bằng chứng rằng văn bản thay đổi độ chính xác dự báo có điều kiện; các trường hợp bác bỏ tập trung ở chuỗi rất ngắn nên dễ là kết quả ngẫu nhiên và không cho biết chiều cải thiện, phù hợp với kết luận rút ra từ Bảng 12.

**Hình 2**

*Sai Số Bình Phương Trung Bình Trượt Của Dự Báo Lợi Suất BTC Ngoài Mẫu*

![Sai số dự báo ngoài mẫu của BTC](../outputs/figures/real/oos_loss.png)

*Ghi chú.* Sai số bình phương trung bình trượt 30 quan sát của dự báo lợi suất BTC một ngày, theo ba mô hình (EN là Elastic Net, LGBM là LightGBM, XGB là XGBoost) và ba phiên bản đặc trưng (market là chỉ biến thị trường, attention là thêm số tin, text là thêm toàn bộ tín hiệu văn bản).

Cuối cùng, nghiên cứu kiểm tra độ vững của kết quả bằng cách chia mẫu theo thời gian và thêm chỉ số bất định tiền mã hóa của Lucey và cộng sự (2022) làm biến kiểm soát. Bảng 14 trình bày hệ số của FinBERT trong hồi quy dự báo RV một ngày trên toàn mẫu và trên hai giai đoạn trước và sau năm 2025.

**Bảng 14**

*Độ Vững Theo Giai Đoạn Của Hệ Số FinBERT Đối Với Biến Động*

| Tài sản | Toàn mẫu | Trước 2025 | Từ 2025 |
|---|---:|---:|---:|
| BTC | 0,00000 (0,00015) | 0,00020 (0,00018) | −0,00026 (0,00032) |
| ETH | 0,00040 (0,00030) | 0,00050 (0,00045) | 0,00025 (0,00029) |
| SOL | −0,00053** (0,00026) | −0,00055** (0,00026) | −0,00033 (0,00057) |
| BNB | 0,00003 (0,00009) | 0,00014 (0,00011) | −0,00022 (0,00015) |
| XRP | −0,00085 (0,00081) | −0,00101 (0,00112) | 0,00000 (0,00041) |

*Ghi chú.* Hệ số của biến cảm xúc FinBERT trong hồi quy dự báo RV với h = 1, sai số chuẩn Newey - West trong ngoặc. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh. Tính toán của nhóm tác giả.

Dấu của hệ số FinBERT giữa hai giai đoạn trùng nhau ở 2 trong 5 tài sản, và có 2 hệ số đạt mức 10% trong số các ước lượng ở Bảng 14. Điều này có nghĩa là có một số ước lượng đạt ý nghĩa ở từng giai đoạn riêng lẻ, nhưng chúng không nhất quán giữa các giai đoạn. Khi thêm chỉ số bất định tiền mã hóa làm biến kiểm soát, số quan sát giảm vì chuỗi này chỉ có đến cuối năm 2024, và có 0 trong 15 kiểm định Wald đạt mức 10% sau hiệu chỉnh Holm. Bên cạnh đó, nghiên cứu tính lại chỉ số ngày theo hai cách để kiểm tra liệu kết quả có bị chi phối bởi một vài trang tin đăng nhiều bài hay bởi các tin chỉ mô tả diễn biến giá. Cách thứ nhất cho mỗi tên miền một phiếu trong ngày, tức trọng số của mỗi tin bằng nghịch đảo số tin của tên miền đó trong ngày; cách thứ hai loại toàn bộ tin thuộc câu chuyện giá và đầu cơ. Bảng 15 trình bày hệ số của FinBERT trong hồi quy dự báo RV một ngày theo ba phiên bản chỉ số.

**Bảng 15**

*Hệ Số FinBERT Đối Với Biến Động Theo Cách Xây Dựng Chỉ Số*

| Tài sản | Chỉ số chính | Trọng số nguồn | Bỏ tin giá - đầu cơ |
|---|---:|---:|---:|
| BTC | 0,00000 (0,00015) | −0,00009 (0,00012) | 0,00002 (0,00014) |
| ETH | 0,00040 (0,00030) | 0,00032 (0,00021) | 0,00047* (0,00028) |
| SOL | −0,00053** (0,00026) | −0,00037** (0,00019) | −0,00031 (0,00024) |
| BNB | 0,00003 (0,00009) | 0,00004 (0,00009) | −0,00003 (0,00011) |
| XRP | −0,00085 (0,00081) | −0,00067 (0,00052) | −0,00072 (0,00085) |

*Ghi chú.* Hệ số của biến cảm xúc FinBERT trong hồi quy dự báo RV với h = 1 trên toàn mẫu, sai số chuẩn Newey - West trong ngoặc. "Trọng số nguồn" cho mỗi tên miền một phiếu trong ngày; "Bỏ tin giá - đầu cơ" loại tin thuộc câu chuyện giá và đầu cơ trước khi tính chỉ số. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh. Tính toán của nhóm tác giả.

Trên toàn bộ 45 hệ số FinBERT của mỗi biến thể (05 tài sản, 03 biến mục tiêu, 03 độ trễ, toàn mẫu), phiên bản trọng số nguồn có 6 hệ số đạt mức 10% trước hiệu chỉnh và 0 hệ số sau hiệu chỉnh Holm, cùng dấu với chỉ số chính ở 39 hệ số; phiên bản bỏ tin giá - đầu cơ có 9 hệ số đạt mức 10% trước hiệu chỉnh và 0 hệ số sau hiệu chỉnh, cùng dấu với chỉ số chính ở 36 hệ số. Điều này có nghĩa là trong hồi quy dự báo theo ngày, việc chưa ghi nhận hệ số cảm xúc FinBERT có ý nghĩa sau hiệu chỉnh Holm không thay đổi khi cho mỗi tên miền một phiếu hoặc khi loại tin giá và đầu cơ khỏi chỉ số.

## 5. Kết luận

Nghiên cứu xây dựng một quy trình dữ liệu văn bản đúng thời điểm cho thị trường tiền mã hóa và kiểm định vai trò của cảm xúc, sự chú ý và câu chuyện thị trường trong 142.646 tin tức tiếng Anh đối với lợi suất, biến động và khối lượng giao dịch của 05 tài sản lớn giai đoạn 2023 - 2026. Về đo lường, nghiên cứu ghi nhận độ lệch đáng kể giữa các đồng hồ dữ liệu, với giờ thấy tin của GDELT trễ trung vị 142 phút so với giờ đăng và 16,7% tin bị gán sang ngày khác nếu dùng đồng hồ này. FinBERT phân biệt tin tốt và tin xấu tốt hơn hai từ điển và CryptoBERT trên nhãn yếu, nên RQ1 được ủng hộ về khả năng phân biệt sắc thái, dù hồi quy dự báo chưa đủ để xếp hạng các thước đo. Đối với tác động lên giá, tin tức không đi kèm lợi suất bất thường có hướng sau hiệu chỉnh kiểm định bội, nhưng khối lượng giao dịch bất thường tăng có ý nghĩa quanh tin, mạnh hơn ở các chủ đề DeFi, vĩ mô và tiền tệ, stablecoin (RQ3), và mạnh hơn sau tin tốt so với tin xấu (RQ2). Kiểm định Granger cho thấy lợi suất dẫn trước cảm xúc của tin ở cả 05 tài sản trong khi chiều ngược lại không có ý nghĩa sau hiệu chỉnh (RQ4), và bổ sung văn bản chưa cải thiện dự báo ngoài mẫu (RQ5). Những kết quả này phù hợp với giả thuyết thị trường hiệu quả ở tần suất ngày và cho thấy tin tức tiền mã hóa chủ yếu phản ánh diễn biến giá hơn là báo trước giá.

Về hàm ý, đối với nhà đầu tư và đơn vị xây dựng chỉ số cảm xúc, kết quả cho thấy ngày của tin trong cơ sở dữ liệu không đồng nghĩa với ngày công bố, nên cần kiểm tra đồng hồ dữ liệu và loại bỏ khả năng văn bản bị chỉnh sửa sau khi công bố trước khi dùng tín hiệu cho giao dịch. Đối với nhà nghiên cứu, việc báo cáo độ lệch giữa các đồng hồ, ước lượng mô hình văn bản chỉ trên kỳ huấn luyện và hiệu chỉnh kiểm định bội giúp tránh kết luận quá mức từ các tín hiệu có kích thước hiệu ứng nhỏ. Đối với cơ quan quản lý, việc theo dõi dòng tin theo câu chuyện thị trường có thể là một nguồn dữ liệu bổ trợ cho giám sát rủi ro, song nghiên cứu chưa tìm thấy bằng chứng rằng một câu chuyện cụ thể báo trước biến động giá.

Nghiên cứu còn một số hạn chế. Thứ nhất, kho tin GDELT chỉ được lấy theo một lô mỗi giờ, khoảng một phần tư số bài, nên cường độ tin trong ngày bị đo thấp hơn thực tế. Thứ hai, chỉ 42 trong 162.936 tin GDELT có giờ đăng hợp lệ nên hầu hết tin được gán theo giờ thấy tin lần đầu, làm chậm tín hiệu so với thời điểm công bố. Thứ ba, nhãn yếu phản ánh kỳ vọng giá của người dùng một nền tảng chứ không phải đánh giá giọng điệu độc lập. Thứ tư, 08 câu chuyện thị trường được định trước có thể bỏ sót chủ đề mới, và văn bản dùng để phân loại chủ yếu là tiêu đề vì GKG không cung cấp nội dung bài viết. Thứ năm, chỉ số bất định tiền mã hóa không có phiên bản theo thời điểm công bố và chỉ có đến cuối năm 2024. Cuối cùng, các hồi quy dự báo và kiểm định Granger chỉ cho thấy quan hệ dẫn trước, không chứng minh quan hệ nhân quả. Hướng nghiên cứu tiếp theo là thu toàn bộ các lô tin trong ngày, mở rộng kiểm chứng giờ đăng, dùng nhãn thủ công quy mô lớn hơn để đánh giá mô hình chuyển đổi trên miền tiền mã hóa, và tách tin mô tả biến động giá khỏi tin mang thông tin mới để kiểm định riêng tác động của nhóm tin sau.

## Tài liệu tham khảo

Andersen, T. G., & Bollerslev, T. (1998). Answering the skeptics: Yes, standard volatility models do provide accurate forecasts. *International Economic Review, 39*(4), 885–905. https://doi.org/10.2307/2527343

Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. *The Journal of Finance, 59*(3), 1259–1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x

Araci, D. (2019). *FinBERT: Financial sentiment analysis with pre-trained language models* (arXiv:1908.10063). arXiv. https://doi.org/10.48550/arXiv.1908.10063

Auer, R., & Claessens, S. (2018). Regulating cryptocurrencies: Assessing market reactions. *BIS Quarterly Review*. https://www.bis.org/publ/qtrpdf/r_qt1809f.htm

Baker, M., & Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives, 21*(2), 129–151. https://doi.org/10.1257/jep.21.2.129

Barjašić, I., & Antulov-Fantulin, N. (2021). Time-varying volatility in Bitcoin market and information flow at minute-level frequency. *Frontiers in Physics, 9*, Article 644102. https://doi.org/10.3389/fphy.2021.644102

Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet allocation. *Journal of Machine Learning Research, 3*, 993–1022. https://jmlr.org/papers/v3/blei03a.html

Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-study methodology under conditions of event-induced variance. *Journal of Financial Economics, 30*(2), 253–272. https://doi.org/10.1016/0304-405X(91)90032-F

Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. *The Journal of Finance, 79*(5), 3105–3147. https://doi.org/10.1111/jofi.13377

Campbell, J. Y., & Thompson, S. B. (2008). Predicting excess stock returns out of sample: Can anything beat the historical average?. *The Review of Financial Studies, 21*(4), 1509–1531. https://doi.org/10.1093/rfs/hhm055

Chou, K.-H., Day, M.-Y., & Chiu, C.-L. (2023). Do bitcoin news information flow and return volatility fit the sequential information arrival hypothesis and the mixture of distribution hypothesis?. *International Review of Economics & Finance, 88*, 365–385. https://doi.org/10.1016/j.iref.2023.06.021

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics, 138*(1), 291–311. https://doi.org/10.1016/j.jeconom.2006.05.023

Critien, J. V., Gatt, A., & Ellul, J. (2022). Bitcoin price change and trend prediction through Twitter sentiment and data volume. *Financial Innovation, 8*(1), Article 45. https://doi.org/10.1186/s40854-022-00352-7

Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *The Journal of Finance, 66*(5), 1461–1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *The Journal of Finance, 25*(2), 383–417. https://doi.org/10.2307/2325486

Garcia, D., & Schweitzer, F. (2015). Social signals and algorithmic trading of Bitcoin. *Royal Society Open Science, 2*(9), Article 150288. https://doi.org/10.1098/rsos.150288

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica, 74*(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica, 37*(3), 424–438. https://doi.org/10.2307/1912791

Grootendorst, M. (2022). *BERTopic: Neural topic modeling with a class-based TF-IDF procedure* (arXiv:2203.05794). arXiv. https://doi.org/10.48550/arXiv.2203.05794

Gür, Y. E., & Ünal, E. (2026). The impact of news sentiment on the Bitcoin price via machine learning and deep learning-based NLP models. *Journal of Forecasting, 45*(3), 895–923. https://doi.org/10.1002/for.70068

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D., Leybourne, S., & Newbold, P. (1997). Testing the equality of prediction mean squared errors. *International Journal of Forecasting, 13*(2), 281–291. https://doi.org/10.1016/S0169-2070(96)00719-4

Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. https://www.jstor.org/stable/4615733

Ider, D., & Lessmann, S. (2022). *Forecasting cryptocurrency returns from sentiment signals: An analysis of BERT classifiers and weak supervision* (arXiv:2204.05781). arXiv. https://doi.org/10.48550/arXiv.2204.05781

Kao, Y.-S., Day, M.-Y., & Chou, K.-H. (2024). A comparison of bitcoin futures return and return volatility based on news sentiment contemporaneously or lead-lag. *The North American Journal of Economics and Finance, 72*, Article 102159. https://doi.org/10.1016/j.najef.2024.102159

Khaksar, E., Biktimirov, E. N., Ayanso, A., & Sokolyk, T. (2026). Bitcoin returns and volume: Uncovering investor sentiment through topic modeling. *International Review of Financial Analysis, 116*, Article 105197. https://doi.org/10.1016/j.irfa.2026.105197

Koenker, R., & Bassett, G. (1978). Regression quantiles. *Econometrica, 46*(1), 33–50. https://doi.org/10.2307/1913643

Kraaijeveld, O., & De Smedt, J. (2020). The predictive power of public Twitter sentiment for forecasting cryptocurrency prices. *Journal of International Financial Markets, Institutions and Money, 65*, Article 101188. https://doi.org/10.1016/j.intfin.2020.101188

Kristoufek, L. (2013). BitCoin meets Google Trends and Wikipedia: Quantifying the relationship between phenomena of the Internet era. *Scientific Reports, 3*, Article 3415. https://doi.org/10.1038/srep03415

Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global data on events, location, and tone, 1979–2012. In *ISA Annual Convention*. http://data.gdeltproject.org/documentation/ISA.2013.GDELT.pdf

Liu, Y., & Tsyvinski, A. (2021). Risks and returns of cryptocurrency. *The Review of Financial Studies, 34*(6), 2689–2727. https://doi.org/10.1093/rfs/hhaa113

Loginova, E., Tsang, W. K., van Heijningen, G., Kerkhove, L.-P., & Benoit, D. F. (2024). Forecasting directional bitcoin price returns using aspect-based sentiment analysis on online text data. *Machine Learning, 113*(7), 4761–4784. https://doi.org/10.1007/s10994-021-06095-3

Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance, 66*(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x

Lucey, B. M., Vigne, S. A., Yarovaya, L., & Wang, Y. (2022). The cryptocurrency uncertainty index. *Finance Research Letters, 45*, Article 102147. https://doi.org/10.1016/j.frl.2021.102147

Nasekin, S., & Chen, C. Y.-H. (2020). Deep learning-based cryptocurrency sentiment construction. *Digital Finance, 2*(1–2), 39–67. https://doi.org/10.1007/s42521-020-00018-y

Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica, 55*(3), 703–708. https://doi.org/10.2307/1913610

Ortu, M., Uras, N., Conversano, C., Bartolucci, S., & Destefanis, G. (2022). On technical trading and social media indicators for cryptocurrency price classification through deep learning. *Expert Systems with Applications, 198*, Article 116804. https://doi.org/10.1016/j.eswa.2022.116804

Rahsaz, S. (n.d.). *Crypto news dataset: 248k cryptocurrency news from CryptoPanic* [Data set]. GitHub repository. https://github.com/soheilrahsaz/cryptoNewsDataset

Reimers, N., & Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge distillation. In *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 4512–4525). Association for Computational Linguistics. https://doi.org/10.18653/v1/2020.emnlp-main.365

Shiller, R. J. (2017). Narrative economics. *American Economic Review, 107*(4), 967–1004. https://doi.org/10.1257/aer.107.4.967

Stone, P. J., Dunphy, D. C., Smith, M. S., & Ogilvie, D. M. (1966). *The General Inquirer: A computer approach to content analysis*. MIT Press.

Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *The Journal of Finance, 62*(3), 1139–1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x

Walker, C. B. (2024). Going mainstream: Cryptocurrency narratives in newspapers. *International Review of Financial Analysis, 94*, Article 103305. https://doi.org/10.1016/j.irfa.2024.103305

[^abs]: Nội dung nêu về Chou và cộng sự (2023), Kao và cộng sự (2024) và Gür và Ünal (2026) dựa trên phần tóm tắt công bố của các nghiên cứu này.
[^market]: Dữ liệu giá lấy từ sàn Binance qua thư viện ccxt, gồm nến ngày và nến giờ của năm cặp giao dịch với USDT. Lợi suất là hiệu số logarit giá đóng cửa. Khối lượng giao dịch tính bằng USD, xấp xỉ bằng giá đóng cửa nhân khối lượng cơ sở. RV của ngày t là tổng bình phương 24 lợi suất log theo giờ trong ngày UTC, và ngày thiếu một nến giờ được để trống thay vì nội suy.
[^gkg]: GKG 2.0 là các tệp tĩnh được cập nhật mỗi 15 phút. Vì mỗi ngày có 96 tệp, nghiên cứu chỉ lấy lô phút 00 của mỗi giờ, tương đương khoảng một phần tư số bài, và thu các ngày theo thứ tự rải đều thời gian để mọi giai đoạn của mẫu đều được phủ. Giờ của lô là thời điểm GDELT thấy bài viết lần đầu. Tiêu đề lấy từ trường tiêu đề trang và được lọc bằng biểu thức chính quy theo các từ khóa như bitcoin, ethereum, crypto và stablecoin.
[^viet]: Nhánh tiếng Việt dùng từ điển tài chính tiếng Việt do nhóm tác giả Việt hóa theo logic của Loughran và McDonald (2011) cùng từ điển bổ sung cho tiền mã hóa, khớp cụm từ dài nhất và xử lý phủ định bằng các từ không, chưa, chẳng. Do số tin tiếng Việt rất ít, nhánh này không được đưa vào chỉ số ngày và không được báo cáo trong phần kết quả.
[^dedup]: Độ tương đồng tiêu đề tính bằng khoảng cách chuỗi chuẩn hóa. Mỗi tin chỉ được so với bản gốc, không so với bản trùng, để tránh nối chuỗi các tiêu đề khác nhau dần. Địa chỉ trang chỉ bị loại các tham số theo dõi như utm và fbclid; các tham số định danh bài viết được giữ nguyên để hai bài khác nhau không bị coi là một.
[^lex]: Với từ điển Loughran và McDonald, mẫu số là số từ thuộc danh sách gốc của từ điển và từ tích cực bị bỏ nếu có từ phủ định trong ba từ đứng trước; điểm là (tích cực - tiêu cực) chia cho (tích cực + tiêu cực). Từ điển Harvard IV-4 được tính tương tự. FinBERT được chạy trên tối đa 20 câu đầu của mỗi tin và lấy trung bình xác suất, và với tiêu đề tin thì mỗi tin thường chỉ có một câu. Mô hình CryptoBERT chỉ được dùng ở bước kiểm định vì không rõ dữ liệu huấn luyện của mô hình có trùng giai đoạn mẫu hay không.
[^zs]: Vectơ nhúng dùng mô hình đa ngữ paraphrase-multilingual-MiniLM-L12-v2 (Reimers & Gurevych, 2020). Xác suất là softmax của độ tương đồng cosine với nhiệt độ cố định 0,05. Tin có độ tương đồng cao nhất thấp hơn phân vị 20% của kỳ huấn luyện được xếp vào nhóm khác. Nghiên cứu không dùng mô hình ngôn ngữ lớn để gán nhãn làm biến giải thích vì mô hình có thể đã biết các sự kiện xảy ra sau ngày của tin; mô hình này chỉ được dùng cho bước kiểm định trên tin trước kỳ đánh giá.
[^topic]: BERTopic kết hợp vectơ nhúng, giảm chiều UMAP và phân cụm HDBSCAN, được ước lượng trên tin của kỳ huấn luyện rồi áp dụng cho các kỳ sau. Với LDA, bộ vectơ hóa từ vựng cũng chỉ được ước lượng trên kỳ huấn luyện, và số chủ đề được chọn theo độ phức tạp (perplexity) trên kỳ kiểm tra. Chủ đề được ánh xạ sang câu chuyện thị trường bằng vectơ nhúng của mười từ đặc trưng. Văn bản đưa vào phân loại là tiêu đề, cộng tối đa 500 ký tự đầu của thân bài với nguồn có thân bài; với tin GDELT chỉ có tiêu đề, nên sự kiện chính nằm sâu trong bài có thể bị bỏ sót.
[^dis]: Thước đo của Antweiler và Frank (2004) là căn bậc hai của (1 - A²), với A là hiệu số tin tích cực và tin tiêu cực chia cho tổng hai loại tin theo nhãn FinBERT; giá trị bằng 0 là đồng thuận hoàn toàn và bằng 1 là chia đều. Độ lệch chuẩn của điểm cảm xúc trong ngày là thước đo phân tán theo tinh thần của Khaksar và cộng sự (2026), nhưng nghiên cứu này không tái lập nguyên văn đặc tả của họ vì họ tính cảm xúc theo từng chủ đề. Hai thước đo được báo cáo riêng rẽ.
[^event]: Cửa sổ ước lượng gồm 144 nến giờ từ 168 đến 25 giờ trước T_0, bỏ 24 giờ ngay trước sự kiện. Khối lượng bất thường là chênh lệch logarit khối lượng USD so với trung bình của cửa sổ ước lượng. Lợi suất bất thường được chuẩn hóa bằng độ lệch chuẩn phần dư của cửa sổ ước lượng để tính thống kê của Boehmer và cộng sự (1991). Kiểm định giả (placebo) dịch cửa sổ lùi 24 giờ để kiểm tra phản ứng không do thời điểm trong ngày.
