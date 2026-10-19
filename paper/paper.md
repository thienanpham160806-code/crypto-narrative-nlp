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

Nghiên cứu kiểm định thông tin dự báo của cảm xúc và câu chuyện trong tin tức tiếng Anh đối với lợi suất, biến động thực hiện và khối lượng giao dịch của năm tiền mã hóa giai đoạn 2023–2026. Từ {{n_canon_en}} tin, nghiên cứu xây dựng chỉ số ngày bằng hai từ điển tài chính, FinBERT và phân loại câu chuyện, với mỗi tin gán theo giờ công bố hợp lệ hoặc giờ xuất hiện đầu tiên. Nghiên cứu dùng 300 nhãn độc lập, hồi quy HAC, sự kiện theo giờ, kiểm định Granger và dự báo ngoài mẫu. FinBERT phân biệt tin tốt và xấu tốt hơn hai từ điển (AUC {{hand_auc_fb}} so với {{hand_auc_lm}} và {{hand_auc_hv}}). Sau hiệu chỉnh kiểm định bội, không thấy lợi suất bất thường có hướng, nhưng khối lượng bất thường tăng quanh tin. Lợi suất dẫn trước cảm xúc ở {{#if gr_r2s_holm==5}}cả 05 tài sản{{#else}}{{gr_r2s_holm}} trong 05 tài sản{{/if}} theo nghĩa Granger; chiều ngược lại và lợi ích dự báo ngoài mẫu của văn bản chưa có ý nghĩa. Kết quả chưa ủng hộ dùng cảm xúc tin tức để dự báo lợi suất hằng ngày. Do GKG chỉ cung cấp một lô mỗi giờ và rất ít giờ đăng được xác minh, quan hệ dẫn trước cần diễn giải thận trọng, không chứng minh nhân quả.

## ABSTRACT

This study tests whether sentiment and narratives in English-language news add predictive information for returns, realized volatility, and trading volume of BTC, ETH, SOL, BNB, and XRP in 2023–2026. From {{n_canon_en}} articles, it constructs daily indices using two financial dictionaries, FinBERT, and narrative classification, dating each article by a valid publication time or its first observed time. The analysis uses 300 independently labeled headlines, HAC predictive regressions, hourly event studies, Granger tests, and out-of-sample forecasts. FinBERT distinguishes positive from negative headlines better than both dictionaries (AUC {{hand_auc_fb}} versus {{hand_auc_lm}} and {{hand_auc_hv}}). After multiple-testing correction, news is not associated with directional abnormal returns, although abnormal trading volume rises around news arrivals. Returns Granger-predict sentiment for {{#if gr_r2s_holm==5}}all five assets{{#else}}{{gr_r2s_holm}} of five assets{{/if}}; the reverse direction and out-of-sample forecast gains from text are not statistically significant. The results do not support daily news sentiment as a reliable return forecast signal. Because GKG provides only one batch per hour and very few publication times can be verified, predictive lead-lag relations require caution and do not establish causality.

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

Nhằm giải thích vai trò của tín hiệu văn bản đối với lợi suất, biến động và khối lượng giao dịch tiền mã hóa, nghiên cứu xây dựng dữ liệu bảng cho 05 tài sản gồm BTC, ETH, SOL, BNB và XRP theo ngày trong giai đoạn từ 01/01/2023 đến 30/09/2026, tức {{calendar_days}} ngày. Ngày t được tính từ 00:00 đến 24:00 theo giờ UTC vì thị trường giao dịch liên tục. Mẫu được chia thành ba kỳ không chồng lấn là huấn luyện (đến 30/06/2025), kiểm tra (đến 31/12/2025) và đánh giá ngoài mẫu (từ 01/01/2026). Kỳ đánh giá ngoài mẫu không được sử dụng khi chọn tham số, chọn số chủ đề, chọn ngưỡng phân loại hay ước lượng bất kỳ mô hình văn bản nào.[^market]

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

[[CHỜ_DỮ_LIỆU: bang_mota]]

*Ghi chú.* Panel A và B tính trên các quan sát tài sản - ngày có tin trong giai đoạn 01/2023 - 09/2026; Panel C tính trên các cặp tin - tài sản dùng cho phân tích sự kiện. RV nhân với 10⁴. Tính toán của nhóm tác giả.

## 4. Kết quả nghiên cứu và thảo luận

Trước khi trình bày kết quả theo từng câu hỏi nghiên cứu, cần xem xét độ phủ của dữ liệu. Tính đến thời điểm lập bản này, kho tin có {{news_days}} trong {{calendar_days}} ngày có ít nhất một tin ({{pct_news_days}}%), gồm {{n_canon_en}} tin tiếng Anh canonical và {{n_event_rows}} cặp tin - tài sản dùng cho phân tích sự kiện. Bảng 3 cho thấy số ngày có tin gắn mã của từng tài sản và số ngày dùng được cho mô hình.{{#if pct_news_days_num<90}} Do bộ thu dữ liệu GDELT chưa phủ hết mẫu, các kết quả dưới đây mang tính sơ bộ và sẽ được tính lại khi dữ liệu đầy đủ. [[CHỜ_DỮ_LIỆU: độ phủ đầy đủ của kho tin GDELT]]{{/if}}

**Bảng 3**

*Độ Phủ Tin Và Số Ngày Dùng Cho Mô Hình Theo Tài Sản*

[[CHỜ_DỮ_LIỆU: bang_phu]]

*Ghi chú.* "Ngày có tin gắn mã" là số ngày có ít nhất một tin nhắc đến tài sản. Khi ngày không có tin gắn mã nhưng kho tin chung có tin, mô hình dùng chỉ số tính trên toàn thị trường làm tín hiệu thay thế; cột "Trong đó dùng chỉ số chung" là số ngày như vậy. Ngày không có tin nào vẫn là dữ liệu thiếu. Tính toán của nhóm tác giả.

Bảng 3 có nghĩa là với kho tin đầy đủ, BTC, ETH và XRP có tin gắn mã ở trên 90% số ngày, nên chỉ số của các tài sản này phản ánh tin riêng về chúng. {{#if btc_test<200}}Tuy vậy, với BTC, kỳ đánh giá ngoài mẫu chỉ có {{btc_test}} ngày đủ biến. {{/if}}Ngược lại, BNB chỉ có tin gắn mã ở {{pct_bnb}}% số ngày và phần lớn ngày dùng cho mô hình phải lấy chỉ số chung của thị trường, nên ước lượng cho BNB không thể diễn giải như tác động riêng của tin về BNB. Điều này được lý giải do tin được gắn mã bằng cách tìm tên hoặc ký hiệu tài sản trong tiêu đề, nên tài sản ít được báo chí nhắc đến xuất hiện trong tiêu đề ít thường xuyên hơn.

Kết quả đầu tiên liên quan đến chất lượng của dữ liệu thời gian, vì mọi kết quả sau đó phụ thuộc vào việc tin được gán đúng ngày. Bảng 4 so sánh các đồng hồ dữ liệu.

**Bảng 4**

*Độ Lệch Giữa Các Đồng Hồ Dữ Liệu Thời Gian*

[[CHỜ_DỮ_LIỆU: bang_dongho]]

*Ghi chú.* Độ lệch là giờ so sánh trừ giờ chuẩn, tính bằng phút. "Lệch > 1 giờ" và "Đổi ngày" là tỷ lệ phần trăm số cặp. Với SEC, giờ chuẩn là ngày nộp hồ sơ. Tính toán của nhóm tác giả.

Giờ hệ thống thấy tin của GDELT trễ so với giờ đăng trong trang với độ lệch tuyệt đối trung vị {{ts_med_abs}} phút trên {{ts_pairs}} tin kiểm chứng được, trong đó {{ts_gt1h}}% lệch hơn một giờ và {{ts_shift}}% bị chuyển sang ngày UTC khác. Điều này có nghĩa là nếu dùng đồng hồ thấy tin để gán ngày thì khoảng một phần sáu số tin sẽ thuộc ngày hôm sau so với thời điểm thực sự công bố. Điều này được lý giải do GDELT ghi nhận thời điểm hệ thống thu thập bài viết, vốn sau thời điểm nguồn đăng bài. Với hồ sơ của SEC, giờ chấp nhận đổi sang UTC khác với ngày nộp hồ sơ ở {{sec_shift}}% trong {{sec_pairs}} hồ sơ, vì hồ sơ nộp sau 17:30 giờ New York được tính sang ngày làm việc kế tiếp. Kết quả này phù hợp với quy tắc ở phương trình (1), theo đó tin được gán vào ngày thấy khi giờ đăng không đáng tin cậy, một lựa chọn có thể làm chậm tín hiệu nhưng không đưa thông tin từ tương lai vào chỉ số. Cần lưu ý chỉ {{ts_pairs}} trong {{ts_docs}} tin GDELT có giờ đăng hợp lệ vì nhiều trang không công bố giờ đăng kèm múi giờ hoặc không cho phép truy cập tự động, nên hầu hết tin được gán theo giờ thấy tin lần đầu. Đây là lựa chọn thận trọng vì giờ thấy tin không sớm hơn giờ công bố, song nó làm chậm tín hiệu khoảng {{ts_med_abs_round}} phút so với thời điểm công bố thật, và có thể làm phản ứng ngay sau tin bị ước lượng thấp.

Đối với RQ1, nghiên cứu trước hết so sánh độ chính xác của các thước đo cảm xúc với nhãn yếu từ phiếu bình chọn của người dùng CryptoPanic, trình bày ở Bảng 5.

**Bảng 5**

*Độ Chính Xác Của Các Thước Đo Trên Nhãn Yếu Và Nhãn Thủ Công*

[[CHỜ_DỮ_LIỆU: bang_nhan_yeu]]

*Ghi chú.* Panel A gồm {{weak_n}} tiêu đề CryptoPanic có ít nhất 03 phiếu và chênh lệch phiếu tích cực và tiêu cực từ 02 phiếu trở lên, trong đó {{weak_pos}}% có nhãn tích cực; "Phân định" là tỷ lệ tin mà thước đo cho điểm khác 0, điểm bằng 0 được tính là dự đoán sai. {{#if hand_n>0}}Panel B và C gồm {{hand_n}} tiêu đề chọn ngẫu nhiên trước kỳ đánh giá, gán ba nhãn cảm xúc (tích cực, trung tính, tiêu cực) và một trong 08 câu chuyện thị trường hoặc nhóm khác; AUC tính trên các tiêu đề tích cực và tiêu cực. {{/if}}Tính toán của nhóm tác giả.

{{#if auc_fb>=auc_lm}}Kết quả ở Bảng 5 cho thấy FinBERT đạt AUC {{auc_fb}}, cao hơn từ điển Loughran - McDonald ({{auc_lm}}), Harvard IV-4 ({{auc_hv}}) và CryptoBERT ({{auc_cb}}). Điều này có nghĩa là FinBERT xếp hạng tin tốt cao hơn tin xấu đúng hơn các thước đo còn lại, nên RQ1 được ủng hộ về khả năng phân biệt sắc thái trên tiêu đề tin tiền mã hóa. Điều này được lý giải do hai từ điển chỉ phân định được {{dec_lm}}% và {{dec_hv}}% số tiêu đề, vì tiêu đề ngắn hiếm khi chứa từ thuộc danh sách, còn mô hình chuyển đổi cho điểm mọi tiêu đề.{{#else}}Kết quả ở Bảng 5 cho thấy FinBERT đạt AUC {{auc_fb}}, thấp hơn thước đo tốt nhất là {{auc_best_name}}, nên RQ1 chưa được ủng hộ về khả năng phân biệt sắc thái trên mẫu nhãn yếu hiện có.{{/if}} Độ chính xác cao của CryptoBERT ({{acc_cb}}) chủ yếu phản ánh việc mô hình gần như luôn dự đoán nhãn tích cực trong khi {{weak_pos}}% nhãn là tích cực, và điều này thể hiện ở F1 trung bình ({{f1_cb}}) và AUC ({{auc_cb}}) thấp hơn FinBERT, hàm ý rằng mô hình huấn luyện trên bài đăng mạng xã hội chưa chuyển tốt sang tiêu đề tin. Kết quả này tương đồng với kết luận của Loughran và McDonald (2011) rằng công cụ đo phải phù hợp với loại văn bản, và với Araci (2019) về lợi thế của mô hình chuyển đổi so với danh sách từ. Cần lưu ý nhãn yếu phản ánh kỳ vọng giá của đám đông người dùng chứ không phải đánh giá giọng điệu của chuyên gia. {{#if hand_n>0}}Kết quả trên {{hand_n}} tiêu đề do nhóm tác giả gán nhãn thủ công ở Panel B của Bảng 5 củng cố nhận định này: FinBERT đạt AUC {{hand_auc_fb}}, cao hơn rõ so với Loughran - McDonald ({{hand_auc_lm}}) và Harvard IV-4 ({{hand_auc_hv}}), và có F1 trung bình cao nhất ({{hand_macro_f1_fb}}). Độ chính xác của mọi thước đo chỉ ở mức trung bình (FinBERT {{hand_accuracy_fb}}) vì {{hand_neutral_pct}}% tiêu đề được gán nhãn trung tính, nhóm mà các thước đo khó tách khỏi tin tốt hoặc tin xấu nhẹ. Đối với câu chuyện thị trường, Panel C cho thấy phân loại zero-shot đạt độ chính xác {{hand_accuracy_zs}} và F1 trung bình {{hand_macro_f1_zs}}, cao hơn BERTopic ({{hand_accuracy_bt}}; {{hand_macro_f1_bt}}) và LDA ({{hand_accuracy_lda}}; {{hand_macro_f1_lda}}), nhưng độ chính xác này vẫn thấp hơn tỷ lệ {{hand_other_pct}}% tiêu đề mà người gán xếp vào nhóm khác. Điều này có nghĩa là zero-shot nhận diện các câu chuyện định trước tốt hơn hai mô hình chủ đề, song xếp nhiều tiêu đề không thuộc 08 câu chuyện vào một câu chuyện cụ thể, nên các biến chú ý cần được hiểu là thước đo có nhiễu và kết quả không có ý nghĩa ở RQ3 có thể một phần do sai số đo lường.{{#else}}Kết quả trên 300 tiêu đề gán nhãn thủ công sẽ được bổ sung vào Bảng 5 khi bộ nhãn hoàn thành. [[CHỜ_DỮ_LIỆU: nhãn thủ công 300 tiêu đề]]{{/if}}

Tiếp theo, RQ1 cũng hỏi liệu cảm xúc đo bằng mô hình chuyển đổi giải thích kết quả thị trường tốt hơn từ điển hay không. Bảng 6 trình bày hệ số của ba thước đo cảm xúc trong hồi quy dự báo (8) với độ trễ một ngày.

**Bảng 6**

*Hệ Số Cảm Xúc Trong Hồi Quy Dự Báo Một Ngày*

[[CHỜ_DỮ_LIỆU: bang_hoiquy]]

*Ghi chú.* Hệ số của biến cảm xúc trong phương trình (8) với h = 1, sai số chuẩn Newey - West trong ngoặc. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh. Mẫu là các ngày trong kỳ huấn luyện và kiểm tra. Tính toán của nhóm tác giả.

Trong tổng số {{reg_n}} hệ số cho mỗi thước đo (05 tài sản, 03 biến mục tiêu và 03 độ trễ), có {{reg_fb_sig10}} hệ số của FinBERT, {{reg_lm_sig10}} hệ số của Loughran - McDonald và {{reg_hv_sig10}} hệ số của Harvard IV-4 đạt mức ý nghĩa 10% khi chưa hiệu chỉnh, trong khi nếu không có mối liên hệ nào thì số hệ số kỳ vọng ở mức này chỉ khoảng {{reg_exp}}. Sau khi hiệu chỉnh Holm, còn {{reg_holm_sig}} hệ số đạt mức 10%. {{#if reg_holm_sig==0}}Điều này có nghĩa là nghiên cứu chưa tìm thấy bằng chứng có ý nghĩa thống kê cho thấy cảm xúc của ngày t dự báo lợi suất, biến động hay khối lượng của các ngày tiếp theo khi đã kiểm soát các biến thị trường. Điều này được lý giải do phần lớn phương sai của biến động và khối lượng đã được giải thích bởi giá trị trễ của chính chúng, và thị trường tiền mã hóa phản ứng nhanh với thông tin công khai theo giả thuyết thị trường hiệu quả (Fama, 1970), điều mà Gür và Ünal (2026) cũng ghi nhận khi giá trễ giải thích phần lớn biến động giá Bitcoin.{{#else}}Điều này có nghĩa là một số quan hệ dự báo vẫn đứng vững sau khi hiệu chỉnh kiểm định bội, song chúng tập trung ở số ít tài sản và biến mục tiêu nên cần được kiểm tra lại trên mẫu đầy đủ.{{/if}} Về so sánh giữa các thước đo, FinBERT có {{reg_fb_sig10}} hệ số đạt mức 10% so với {{reg_lm_sig10}} và {{reg_hv_sig10}} của hai từ điển, một chênh lệch nhỏ so với mức nhiễu mẫu, nên hồi quy dự báo chưa đủ để xếp hạng các thước đo và RQ1 chủ yếu dựa vào kết quả ở Bảng 5.

Đối với RQ3, nghiên cứu xét phản ứng của lợi suất, độ lớn lợi suất và khối lượng giao dịch quanh thời điểm công bố theo từng câu chuyện thị trường. Bảng 7 trình bày kết quả trong cửa sổ bốn giờ sau tin.

**Bảng 7**

*Phản Ứng Của Giá Và Khối Lượng Quanh Tin Theo Câu Chuyện Thị Trường*

[[CHỜ_DỮ_LIỆU: bang_narrative]]

*Ghi chú.* Cửa sổ [0, 4] giờ sau T_0. CAR và độ lớn lợi suất bất thường tính bằng điểm phần trăm; khối lượng bất thường là chênh lệch logarit khối lượng USD so với trung bình 144 giờ trước tin. Số ngày là số ngày có sự kiện. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value của kiểm định t chưa hiệu chỉnh; cột cuối là p-value Holm nhỏ nhất trong ba chỉ tiêu. Tính toán của nhóm tác giả.

Trên toàn bộ {{n_event_rows}} cặp tin - tài sản, lợi suất bất thường tích lũy trung bình trong cửa sổ [0, 4] giờ là {{evt(all,all,0_4,car,mean)}} điểm phần trăm (p Holm = {{evt(all,all,0_4,car,p_t_holm)}}), và không câu chuyện nào có CAR khác 0 một cách có ý nghĩa sau hiệu chỉnh Holm. Ngược lại, khối lượng giao dịch bất thường trong giờ đầu sau tin là {{evt(all,all,0_1,volume,mean)}} log điểm (p Holm = {{evt(all,all,0_1,volume,p_t_holm)}}), và trong cửa sổ bốn giờ ở Bảng 7, tin về DeFi, vĩ mô và tiền tệ, stablecoin có khối lượng bất thường lần lượt {{evt(narrative,defi,0_4,volume,mean)}}, {{evt(narrative,macro_monetary,0_4,volume,mean)}} và {{evt(narrative,stablecoins,0_4,volume,mean)}} log điểm, đạt ý nghĩa sau hiệu chỉnh Holm và cao hơn các nhóm tin phổ biến như quy định pháp lý ({{evt(narrative,regulation,0_4,volume,mean)}}) hay ETF và nhà đầu tư tổ chức ({{evt(narrative,etf_institutional,0_4,volume,mean)}}). Điều này có nghĩa là câu chuyện thị trường không quyết định hướng giá sau tin nhưng gắn với mức độ hoạt động giao dịch khác nhau, trong đó các chủ đề chuyên biệt và ít xuất hiện kéo theo khối lượng giao dịch bất thường lớn hơn. Điều này có thể được lý giải do các chủ đề này xuất hiện thưa nên mỗi tin mang nhiều thông tin mới hơn, trong khi tin về quy định hay ETF xuất hiện dày đặc nên phản ứng riêng của từng tin bị pha loãng. Kết quả về giá khác với Auer và Claessens (2018) vốn ghi nhận phản ứng lớn đối với các tin pháp lý, nhưng mẫu của họ là 151 tin được chọn lọc, còn nghiên cứu này dùng toàn bộ dòng tin tự động. Trong mô hình hồi quy theo ngày, sự chú ý đến các câu chuyện thị trường có {{att_sig10}} trong {{att_n}} hệ số đạt mức 10% trước hiệu chỉnh, so với khoảng {{att_exp}} hệ số kỳ vọng nếu không có quan hệ nào, và {{att_holm}} hệ số đạt mức này sau hiệu chỉnh Holm. {{#if att_holm==0}}Do đó, ở tần suất ngày, nghiên cứu chưa thể xếp hạng các câu chuyện theo mức liên hệ với lợi suất, biến động và khối lượng, khác với Walker (2024) vốn ghi nhận câu chuyện về tội phạm đi kèm lợi suất tuần sau trong một giai đoạn nhất định.{{#else}}Các hệ số này cho thấy sự chú ý đến một số câu chuyện có liên hệ với biến mục tiêu ngay cả sau hiệu chỉnh, tương đồng với hướng tiếp cận narrative của Bybee và cộng sự (2024).{{/if}}

Tiếp theo, đối với RQ2, nghiên cứu kiểm định tính bất đối xứng theo hai cách. Bảng 8 trình bày kết quả kiểm định Wald trên hồi quy theo ngày (phương trình (9) và (10)), còn Bảng 9 trình bày chênh lệch phản ứng quanh tin giữa nhóm tin xấu và nhóm tin tốt.

**Bảng 8**

*Kiểm Định Bất Đối Xứng Giữa Tin Xấu Và Tin Tốt Đối Với Biến Động*

[[CHỜ_DỮ_LIỆU: bang_wald]]

*Ghi chú.* β⁻ và β⁺ là hệ số của NegSent và PosSent trong phương trình (9) với biến phụ thuộc là RV; W là thống kê Wald của giả thuyết β⁻ = β⁺ với phân phối χ²(1). ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh; cột cuối là p-value đã hiệu chỉnh Holm. Tính toán của nhóm tác giả.

**Bảng 9**

*Chênh Lệch Phản Ứng Quanh Tin Giữa Nhóm Tin Xấu Và Tin Tốt*

[[CHỜ_DỮ_LIỆU: bang_bat_doi_xung]]

*Ghi chú.* Tin xấu và tin tốt là tam phân vị dưới và trên của điểm FinBERT (ngưỡng tính trên kỳ huấn luyện), hoặc điểm Loughran - McDonald âm và dương. Chênh lệch là giá trị trung bình của nhóm xấu trừ nhóm tốt, tính theo ngày sự kiện. CAR và độ lớn lợi suất tính bằng điểm phần trăm. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value của kiểm định t chưa hiệu chỉnh. Tính toán của nhóm tác giả.

Kiểm định Wald ở Bảng 8 bác bỏ giả thuyết β⁻ = β⁺ ở mức 10% đối với {{wald_sig10_raw}} trong {{wald_n}} cặp tài sản - độ trễ khi chưa hiệu chỉnh, và {{wald_sig10_holm}} cặp sau hiệu chỉnh Holm. {{#if wald_sig10_holm==0}}Điều này có nghĩa là nghiên cứu chưa tìm thấy bằng chứng có ý nghĩa thống kê rằng tin xấu và tin tốt có tác động khác nhau lên biến động theo ngày. {{#else}}Điều này có nghĩa là có bằng chứng về tính bất đối xứng ở một số cặp tài sản - độ trễ ngay cả sau hiệu chỉnh. {{/if}}{{#if quant_sig10_holm<=2}}Hồi quy phân vị cho kết luận gần tương tự, với {{quant_sig10_holm}} trong {{quant_n}} kiểm định (05 tài sản, 03 độ trễ, 03 phân vị) đạt mức 10% sau hiệu chỉnh Holm; vì sai số chuẩn của hồi quy phân vị chưa hiệu chỉnh tự tương quan, kết quả đơn lẻ này chưa đủ để coi là bằng chứng bất đối xứng. {{#else}}Hồi quy phân vị cho kết quả khác hơn, với {{quant_sig10_holm}} trong {{quant_n}} kiểm định (05 tài sản, 03 độ trễ, 03 phân vị) đạt mức 10% sau hiệu chỉnh Holm, song vì sai số chuẩn chưa hiệu chỉnh tự tương quan, mức ý nghĩa này có thể bị đánh giá quá cao và chỉ nên coi là bằng chứng thăm dò. {{/if}}Ở phản ứng quanh tin, Bảng 9 cho thấy trong cửa sổ [0, 1] giờ, chênh lệch giữa nhóm tin xấu và nhóm tin tốt theo FinBERT là {{asym(finbert_tercile,0_1,volume,negative_minus_positive)}} log điểm về khối lượng giao dịch (p Holm = {{asym(finbert_tercile,0_1,volume,p_t_holm)}}) và {{asym(finbert_tercile,0_1,absret,negative_minus_positive)}} điểm phần trăm về độ lớn lợi suất bất thường (p Holm = {{asym(finbert_tercile,0_1,absret,p_t_holm)}}), và phân loại theo từ điển Loughran - McDonald cho kết quả cùng chiều. Dấu âm của các chênh lệch có nghĩa là tin tích cực đi kèm hoạt động giao dịch và biến động giá mạnh hơn tin tiêu cực, trái với kỳ vọng rằng tin xấu có tác động mạnh hơn. Bên cạnh đó, trong cửa sổ [0, 24] giờ, CAR sau tin tốt thấp hơn sau tin xấu {{asym(finbert_tercile,0_24,car,negative_minus_positive)}} điểm phần trăm (p Holm = {{asym(finbert_tercile,0_24,car,p_t_holm)}}), gợi ý giá có xu hướng điều chỉnh giảm sau tin tốt. Điều này có thể được lý giải do tin tích cực thường được đăng sau các đợt tăng giá, thu hút cả nhà đầu tư mới lẫn giao dịch chốt lời, nên hoạt động giao dịch tăng mạnh nhưng giá sau đó điều chỉnh. Kết quả này khác với Gür và Ünal (2026) về phản ứng mạnh hơn với tin tiêu cực, và khác với Chou và cộng sự (2023) và Kao và cộng sự (2024) về vai trò của tin tiêu cực đối với lợi suất. Do đó, RQ2 được ủng hộ theo nghĩa tồn tại bất đối xứng, nhưng theo chiều ngược với kỳ vọng và thể hiện ở hoạt động giao dịch trong ngày hơn là ở biến động theo ngày. Hình 1 minh họa lợi suất bất thường tích lũy theo nhóm cảm xúc của tin ở các cửa sổ sau tin.

**Hình 1**

*Lợi Suất Bất Thường Tích Lũy Theo Nhóm Cảm Xúc Của Tin*

![Lợi suất bất thường tích lũy theo nhóm cảm xúc của tin](../outputs/figures/real/event_car_by_tone.png)

*Ghi chú.* Trung bình theo ngày sự kiện của CAR (đơn vị phần trăm) theo ba nhóm tam phân vị của điểm FinBERT (negative là nhóm tin xấu, middle là nhóm giữa, positive là nhóm tin tốt) ở các cửa sổ sau tin; các điểm không kèm khoảng tin cậy.

Đối với RQ4, nghiên cứu xem xét ba khía cạnh là giá có chạy trước tin hay không, chiều dẫn dắt giữa cảm xúc và giá theo ngày, và liệu kết luận có phụ thuộc vào đồng hồ dùng để gán thời điểm. Về khía cạnh thứ nhất, lợi suất bất thường tích lũy trong cửa sổ [-4, -2] giờ trước tin là {{evt(all,all,-4_-2,car,mean)}} điểm phần trăm (p Holm = {{evt(all,all,-4_-2,car,p_t_holm)}}), {{#if evt_pre_car_sig==0}}nên nghiên cứu chưa ghi nhận dấu hiệu giá đã dịch chuyển có hướng trước khi tin xuất hiện{{#else}}cho thấy giá có thể đã dịch chuyển trước khi tin xuất hiện{{/if}}. {{#if evt_pre_other_sig>0}}Tuy nhiên, độ lớn lợi suất bất thường và khối lượng giao dịch trước tin đều lớn hơn bình thường một cách có ý nghĩa sau hiệu chỉnh (khối lượng bất thường {{evt(all,all,-4_-2,volume,mean)}} log điểm, p Holm = {{evt(all,all,-4_-2,volume,p_t_holm)}}), ở mức tương đương với giờ đầu sau tin. {{/if}}Về khía cạnh thứ hai, Bảng 10 cho thấy lợi suất dẫn trước cảm xúc FinBERT ở {{#if gr_r2s_holm==5}}cả 05 tài sản{{#else}}{{gr_r2s_holm}} trong 05 tài sản{{/if}} sau hiệu chỉnh Holm, trong khi cảm xúc dẫn trước lợi suất ở {{gr_s2r_raw}} tài sản khi chưa hiệu chỉnh và {{gr_s2r_holm}} tài sản sau hiệu chỉnh; với RV, có {{gr_rv_holm}} kiểm định có ý nghĩa sau hiệu chỉnh. Điều này có nghĩa là trong mẫu hiện tại, chiều giá dẫn trước cảm xúc có bằng chứng dự báo mạnh hơn chiều ngược lại. Tuy nhiên, sai số giờ công bố và tin trùng thời điểm không cho phép khẳng định tin chỉ phản ánh giá hoặc giải thích nguyên nhân khối lượng tăng trước mốc công bố. Một cơ chế khả dĩ là các tin mô tả biến động giá lấy chính lợi suất trước đó làm nội dung; nghiên cứu chưa lượng hóa riêng cơ chế này. Kết quả này tương đồng với Kraaijeveld và De Smedt (2020), những người ghi nhận giá dẫn dắt cảm xúc trên Twitter ở nhiều đồng tiền, và hàm ý rằng quan hệ đồng thời giữa tin và giá không nên được diễn giải là tin làm thay đổi giá. Về khía cạnh thứ ba, Bảng 11 so sánh phản ứng khi gán thời điểm theo giờ đăng và theo giờ thấy tin trên các tin có đủ hai đồng hồ.

**Bảng 10**

*Kiểm Định Granger Giữa Cảm Xúc Và Biến Thị Trường*

[[CHỜ_DỮ_LIỆU: bang_granger_ket_qua]]

*Ghi chú.* Mô hình VAR hai chiều theo phương trình (11) trên chuỗi ngày liên tục dài nhất của từng tài sản trong kỳ huấn luyện và kiểm tra; yêu cầu tối thiểu 30 quan sát liên tục. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

**Bảng 11**

*Độ Nhạy Của Phản Ứng Giá Với Đồng Hồ Gán Thời Điểm*

[[CHỜ_DỮ_LIỆU: bang_do_nhay]]

*Ghi chú.* CAR tính bằng điểm phần trăm. Dấu sao ở hai cột CAR biểu thị mức ý nghĩa của p-value đã hiệu chỉnh Holm trong họ ba cửa sổ, đối với giả thuyết CAR khác 0. Cột cuối là p-value Holm của kiểm định t ghép cặp về chênh lệch giữa hai đồng hồ. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

Bảng 11 cho thấy trên {{tim_pairs}} cặp tin - tài sản có đủ hai đồng hồ, CAR trong cửa sổ [0, 24] giờ là {{timing(0_24,mean_car_published)}} điểm phần trăm khi gán theo giờ đăng và {{timing(0_24,mean_car_seen)}} điểm phần trăm khi gán theo giờ thấy tin. {{#if tim_changed_holm}}Kết luận về ý nghĩa thống kê thay đổi theo đồng hồ, vì chỉ khi gán theo giờ thấy tin thì CAR mới đạt ý nghĩa sau hiệu chỉnh Holm (p = {{timing(0_24,p_seen_holm)}}), dù chênh lệch ghép cặp giữa hai đồng hồ không đạt ý nghĩa (p Holm = {{timing(0_24,p_paired_t_holm)}}). Điều này có nghĩa là việc chọn đồng hồ có thể làm thay đổi kết luận về phản ứng giá trong ngày.{{#else}}Kết luận về ý nghĩa thống kê không thay đổi giữa hai đồng hồ ở cả ba cửa sổ sau hiệu chỉnh Holm, nên với mẫu hiện có việc chọn đồng hồ chưa làm đổi kết luận.{{/if}} Cần lưu ý số cặp tin có đủ hai đồng hồ rất nhỏ nên các kiểm định này có độ mạnh thấp. {{#if asym_pre_sig>0}}Ngoài ra, ở cửa sổ [-4, 0] giờ, CAR của nhóm tin xấu và nhóm tin tốt theo FinBERT khác nhau có ý nghĩa sau hiệu chỉnh (Bảng 9), củng cố kết quả Granger rằng sắc thái của tin đi theo biến động giá vừa xảy ra.{{/if}}

Đối với RQ5, Bảng 12 trình bày độ chính xác dự báo ngoài mẫu của BTC theo ba mô hình và ba phiên bản đặc trưng với độ trễ một ngày.

**Bảng 12**

*Dự Báo Ngoài Mẫu Của BTC Với Độ Trễ Một Ngày*

[[CHỜ_DỮ_LIỆU: bang_dubao]]

*Ghi chú.* RMSE của RV nhân với 10⁴. R²OS là R² ngoài mẫu so với trung bình lịch sử theo phương trình (14). p (DM) và p (CW) là p-value của kiểm định Diebold - Mariano có hiệu chỉnh mẫu nhỏ và kiểm định Clark - West khi so mô hình có văn bản với mô hình chỉ có biến thị trường; ký hiệu "—" là không áp dụng. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

Trên toàn bộ {{oos_n}} cặp (05 tài sản, 03 mô hình và 02 biến mục tiêu là lợi suất và RV), mô hình bổ sung văn bản có R² ngoài mẫu cao hơn mô hình chỉ có biến thị trường ở {{oos_better}} cặp, và chênh lệch có ý nghĩa ở mức 10% theo kiểm định Diebold - Mariano hoặc Clark - West trước hiệu chỉnh ở {{oos_sig10}} cặp, còn sau hiệu chỉnh Holm là {{oos_sig_holm}} cặp. Các kiểm định này chỉ dùng những ngày mà mọi phiên bản mô hình đều có dự báo, tối đa {{oos_infer_max}} quan sát chung cho mỗi cặp. {{#if oos_sig_holm==0}}Điều này có nghĩa là nghiên cứu chưa tìm thấy bằng chứng có ý nghĩa thống kê rằng văn bản cải thiện dự báo ngoài mẫu so với mô hình chỉ có biến thị trường, và với chỉ {{oos_better}}/{{oos_n}} cặp có R² ngoài mẫu cao hơn, văn bản thường làm dự báo kém đi do thêm nhiễu. {{#else}}Điều này có nghĩa là ở một số cặp, kiểm định cho thấy chênh lệch giữa hai mô hình có ý nghĩa thống kê, song hướng của chênh lệch không nhất quán giữa các mô hình. {{/if}}Điều này được lý giải do biến động có tính bền cao nên giá trị trễ của chính nó đã chứa phần lớn thông tin, và theo kết quả Granger ở trên, giọng điệu tin chủ yếu đi sau lợi suất nên ít thông tin mới về tương lai, tương tự nhận định của Gür và Ünal (2026) rằng giá trễ giải thích phần lớn biến động giá Bitcoin. Kết quả này khác với Ortu và cộng sự (2022) và Loginova và cộng sự (2024), những nghiên cứu ghi nhận mô hình có văn bản tốt hơn mô hình chỉ có biến kỹ thuật, nhưng các nghiên cứu đó đo độ chính xác phân loại hướng giá và không dùng kiểm định bội cho chênh lệch dự báo. Hình 2 cho thấy sai số bình phương trung bình trượt của dự báo lợi suất BTC theo ba phiên bản đặc trưng.

{{#if gw_n>0}}Bên cạnh đó, Bảng 13 trình bày kiểm định giá trị dự báo có điều kiện của Giacomini và White (2006) giữa mô hình có văn bản và mô hình chỉ có biến thị trường.{{#else}}Các kiểm định về giá trị dự báo có điều kiện chưa thực hiện được vì chuỗi kiểm tra liên tục còn ngắn.{{/if}}

**Bảng 13**

*Kiểm Định Giá Trị Dự Báo Có Điều Kiện Giacomini - White*

[[CHỜ_DỮ_LIỆU: bang_dubao_ben_vung]]

*Ghi chú.* Giá trị trong ô là p-value đã hiệu chỉnh Holm của thống kê Giacomini - White với giả thuyết không là hai mô hình có cùng sai số dự báo có điều kiện; kiểm định không cho biết mô hình nào tốt hơn. Số quan sát là số ngày chung lớn nhất trong cửa sổ cuộn 500 ngày. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10%. Tính toán của nhóm tác giả.

{{#if gw_n>0}}Có {{gw_sig_holm}} trong {{gw_n}} kiểm định bác bỏ giả thuyết không ở mức 10% sau hiệu chỉnh Holm, trong khi số quan sát chung chỉ từ {{gw_nobs_min}} đến {{gw_nobs_max}} ngày. {{#if gw_sig_holm<=gw_n/10}}Điều này có nghĩa là trong phần lớn trường hợp, nghiên cứu chưa tìm thấy bằng chứng rằng văn bản thay đổi độ chính xác dự báo có điều kiện; các trường hợp bác bỏ tập trung ở chuỗi rất ngắn nên dễ là kết quả ngẫu nhiên và không cho biết chiều cải thiện, phù hợp với kết luận rút ra từ Bảng 12.{{#else}}Điều này có nghĩa là độ chính xác dự báo có điều kiện khác nhau giữa hai mô hình ở nhiều trường hợp, song kiểm định không cho biết chiều khác biệt nên cần đọc cùng R² ngoài mẫu ở Bảng 12.{{/if}}{{/if}}

**Hình 2**

*Sai Số Bình Phương Trung Bình Trượt Của Dự Báo Lợi Suất BTC Ngoài Mẫu*

![Sai số dự báo ngoài mẫu của BTC](../outputs/figures/real/oos_loss.png)

*Ghi chú.* Sai số bình phương trung bình trượt 30 quan sát của dự báo lợi suất BTC một ngày, theo ba mô hình (EN là Elastic Net, LGBM là LightGBM, XGB là XGBoost) và ba phiên bản đặc trưng (market là chỉ biến thị trường, attention là thêm số tin, text là thêm toàn bộ tín hiệu văn bản).

Cuối cùng, nghiên cứu kiểm tra độ vững của kết quả bằng cách chia mẫu theo thời gian và thêm chỉ số bất định tiền mã hóa của Lucey và cộng sự (2022) làm biến kiểm soát. Bảng 14 trình bày hệ số của FinBERT trong hồi quy dự báo RV một ngày trên toàn mẫu và trên hai giai đoạn trước và sau năm 2025.

**Bảng 14**

*Độ Vững Theo Giai Đoạn Của Hệ Số FinBERT Đối Với Biến Động*

[[CHỜ_DỮ_LIỆU: bang_do_vung]]

*Ghi chú.* Hệ số của biến cảm xúc FinBERT trong hồi quy dự báo RV với h = 1, sai số chuẩn Newey - West trong ngoặc. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh. Tính toán của nhóm tác giả.

{{#if rob_n>0}}Dấu của hệ số FinBERT giữa hai giai đoạn {{#if rob_same_sign}}nhất quán ở cả {{rob_n}} tài sản{{#else}}trùng nhau ở {{rob_same_n}} trong {{rob_n}} tài sản{{/if}}, và có {{rob_sig10}} hệ số đạt mức 10% trong số các ước lượng ở Bảng 14. {{#if rob_sig10<=1}}Điều này có nghĩa là kết quả không đứng vững ở mức ý nghĩa thống kê theo giai đoạn, phù hợp với kết luận chung rằng cảm xúc ngày chưa có sức dự báo biến động đáng tin cậy. {{#else}}Điều này có nghĩa là có một số ước lượng đạt ý nghĩa ở từng giai đoạn riêng lẻ, nhưng chúng không nhất quán giữa các giai đoạn. {{/if}}{{/if}}Khi thêm chỉ số bất định tiền mã hóa làm biến kiểm soát, số quan sát giảm vì chuỗi này chỉ có đến cuối năm 2024, và có {{ucry_wald_sig_holm}} trong 15 kiểm định Wald đạt mức 10% sau hiệu chỉnh Holm. {{#if rob_sw_n>0}}Bên cạnh đó, nghiên cứu tính lại chỉ số ngày theo hai cách để kiểm tra liệu kết quả có bị chi phối bởi một vài trang tin đăng nhiều bài hay bởi các tin chỉ mô tả diễn biến giá. Cách thứ nhất cho mỗi tên miền một phiếu trong ngày, tức trọng số của mỗi tin bằng nghịch đảo số tin của tên miền đó trong ngày; cách thứ hai loại toàn bộ tin thuộc câu chuyện giá và đầu cơ. Bảng 15 trình bày hệ số của FinBERT trong hồi quy dự báo RV một ngày theo ba phiên bản chỉ số.

**Bảng 15**

*Hệ Số FinBERT Đối Với Biến Động Theo Cách Xây Dựng Chỉ Số*

[[CHỜ_DỮ_LIỆU: bang_do_vung_khac]]

*Ghi chú.* Hệ số của biến cảm xúc FinBERT trong hồi quy dự báo RV với h = 1 trên toàn mẫu, sai số chuẩn Newey - West trong ngoặc. "Trọng số nguồn" cho mỗi tên miền một phiếu trong ngày; "Bỏ tin giá - đầu cơ" loại tin thuộc câu chuyện giá và đầu cơ trước khi tính chỉ số. ***, **, * biểu thị mức ý nghĩa thống kê lần lượt là 1%, 5% và 10% theo p-value chưa hiệu chỉnh. Tính toán của nhóm tác giả.

Trên toàn bộ {{rob_sw_n}} hệ số FinBERT của mỗi biến thể (05 tài sản, 03 biến mục tiêu, 03 độ trễ, toàn mẫu), phiên bản trọng số nguồn có {{rob_sw_sig_raw}} hệ số đạt mức 10% trước hiệu chỉnh và {{rob_sw_sig_holm}} hệ số sau hiệu chỉnh Holm, cùng dấu với chỉ số chính ở {{rob_sw_same_sign}} hệ số; phiên bản bỏ tin giá - đầu cơ có {{rob_ex_sig_raw}} hệ số đạt mức 10% trước hiệu chỉnh và {{rob_ex_sig_holm}} hệ số sau hiệu chỉnh, cùng dấu với chỉ số chính ở {{rob_ex_same_sign}} hệ số. {{#if rob_sw_sig_holm+rob_ex_sig_holm==0}}Điều này có nghĩa là trong hồi quy dự báo theo ngày, việc chưa ghi nhận hệ số cảm xúc FinBERT có ý nghĩa sau hiệu chỉnh Holm không thay đổi khi cho mỗi tên miền một phiếu hoặc khi loại tin giá và đầu cơ khỏi chỉ số.{{#else}}Điều này có nghĩa là một số quan hệ dự báo chỉ xuất hiện khi thay đổi cách xây dựng chỉ số, nên cần thận trọng khi diễn giải chúng.{{/if}} Hai cách dựng chỉ số này chỉ được kiểm tra trong hồi quy dự báo; nghiên cứu không tái ước lượng kiểm định Granger theo từng cách.{{#else}}Các kiểm tra độ vững theo trọng số nguồn tin và theo việc loại câu chuyện giá và đầu cơ chưa thực hiện được. [[CHỜ_DỮ_LIỆU: kiểm tra độ vững theo trọng số nguồn và loại câu chuyện giá - đầu cơ]]{{/if}}

## 5. Kết luận

Nghiên cứu xây dựng một quy trình dữ liệu văn bản đúng thời điểm cho thị trường tiền mã hóa và kiểm định vai trò của cảm xúc, sự chú ý và câu chuyện thị trường trong {{n_canon_en}} tin tức tiếng Anh đối với lợi suất, biến động và khối lượng giao dịch của 05 tài sản lớn giai đoạn 2023 - 2026. Về đo lường, nghiên cứu ghi nhận độ lệch đáng kể giữa các đồng hồ dữ liệu, với giờ thấy tin của GDELT trễ trung vị {{ts_med_abs_round}} phút so với giờ đăng và {{ts_shift}}% tin bị gán sang ngày khác nếu dùng đồng hồ này. {{#if auc_fb>=auc_lm}}FinBERT phân biệt tin tốt và tin xấu tốt hơn hai từ điển và CryptoBERT trên nhãn yếu, nên RQ1 được ủng hộ về khả năng phân biệt sắc thái, dù hồi quy dự báo chưa đủ để xếp hạng các thước đo.{{#else}}FinBERT chưa phân biệt tin tốt và tin xấu tốt hơn mọi thước đo còn lại, nên RQ1 chưa được ủng hộ.{{/if}} Đối với tác động lên giá, tin tức không đi kèm lợi suất bất thường có hướng sau hiệu chỉnh kiểm định bội, nhưng khối lượng giao dịch bất thường tăng có ý nghĩa quanh tin, mạnh hơn ở các chủ đề DeFi, vĩ mô và tiền tệ, stablecoin (RQ3), và mạnh hơn sau tin tốt so với tin xấu (RQ2). Kiểm định Granger cho thấy lợi suất dẫn trước cảm xúc của tin ở {{#if gr_r2s_holm==5}}cả 05 tài sản{{#else}}{{gr_r2s_holm}} trong 05 tài sản{{/if}} trong khi chiều ngược lại không có ý nghĩa sau hiệu chỉnh (RQ4), và bổ sung văn bản chưa cải thiện dự báo ngoài mẫu (RQ5). Trong mẫu và cách đo này, bằng chứng chưa ủng hộ sức dự báo gia tăng của văn bản ở tần suất ngày. Quan hệ Granger chỉ mô tả thứ tự dự báo, không xác định giá gây ra nội dung tin hay loại trừ sai số thời điểm công bố.

Về hàm ý, đối với nhà đầu tư và đơn vị xây dựng chỉ số cảm xúc, kết quả cho thấy ngày của tin trong cơ sở dữ liệu không đồng nghĩa với ngày công bố, nên cần kiểm tra đồng hồ dữ liệu và loại bỏ khả năng văn bản bị chỉnh sửa sau khi công bố trước khi dùng tín hiệu cho giao dịch. Đối với nhà nghiên cứu, việc báo cáo độ lệch giữa các đồng hồ, ước lượng mô hình văn bản chỉ trên kỳ huấn luyện và hiệu chỉnh kiểm định bội giúp tránh kết luận quá mức từ các tín hiệu có kích thước hiệu ứng nhỏ. Đối với cơ quan quản lý, việc theo dõi dòng tin theo câu chuyện thị trường có thể là một nguồn dữ liệu bổ trợ cho giám sát rủi ro, song nghiên cứu chưa tìm thấy bằng chứng rằng một câu chuyện cụ thể báo trước biến động giá.

Nghiên cứu còn một số hạn chế. Thứ nhất, kho tin GDELT chỉ được lấy theo một lô mỗi giờ, khoảng một phần tư số bài, nên cường độ tin trong ngày bị đo thấp hơn thực tế. Thứ hai, chỉ {{ts_pairs}} trong {{ts_docs}} tin GDELT có giờ đăng hợp lệ nên hầu hết tin được gán theo giờ thấy tin lần đầu, làm chậm tín hiệu so với thời điểm công bố. Thứ ba, nhãn yếu phản ánh kỳ vọng giá của người dùng một nền tảng chứ không phải đánh giá giọng điệu độc lập. Thứ tư, 08 câu chuyện thị trường được định trước có thể bỏ sót chủ đề mới, và văn bản dùng để phân loại chủ yếu là tiêu đề vì GKG không cung cấp nội dung bài viết. Thứ năm, chỉ số bất định tiền mã hóa không có phiên bản theo thời điểm công bố và chỉ có đến cuối năm 2024. Cuối cùng, các hồi quy dự báo và kiểm định Granger chỉ cho thấy quan hệ dẫn trước, không chứng minh quan hệ nhân quả. Hướng nghiên cứu tiếp theo là thu toàn bộ các lô tin trong ngày, mở rộng kiểm chứng giờ đăng, dùng nhãn thủ công quy mô lớn hơn để đánh giá mô hình chuyển đổi trên miền tiền mã hóa, và tách tin mô tả biến động giá khỏi tin mang thông tin mới để kiểm định riêng tác động của nhóm tin sau.

## Tài liệu tham khảo

[[REFERENCES]]

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
