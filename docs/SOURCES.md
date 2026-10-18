# SOURCES.md — thử thật nguồn tin (2026-10-16)

Phạm vi: blueprint mục 3.1 + `config.text.sources` (gdelt, rss, cryptopanic) + nhánh VN. Mẫu cần: 2023-01-01 → 2026-09-30 (`config.sample`).
Cách thử: `curl` từ máy local, file tạm ở scratchpad, không viết code vào `src/`. Mọi con số dưới đây là kết quả gọi thật hôm nay, trừ chỗ ghi "(theo tài liệu)" hoặc "(nguồn thứ ba)".

## Bảng tổng hợp

| Nguồn | API | Key | Lùi được tới | Giờ đăng / timezone | Giới hạn | Điều khoản | Dùng cho 2023–2026 |
|---|---|---|---|---|---|---|---|
| GDELT DOC 2.0 (`mode=artlist`) | Có (REST JSON) | Không | 2017-01-01 (theo tài liệu) | `seendate` = giờ GDELT thấy bài, UTC (`20230115T234500Z`), không phải giờ đăng | 1 req / 5 s; thực tế 3/17 lệnh qua, 429 kể cả khi cách 90 s | Mở, trích dẫn GDELT | **Có — nguồn chính (tiêu đề)** |
| GDELT GKG 2.0 raw (15 phút) | File zip tĩnh | Không | 2015-02 | `DATE` UTC theo lô 15 phút | Không thấy giới hạn; ~2.4 MB/zip, 96 file/ngày | Mở | Dự phòng lấp lỗ khi DOC API 429 |
| RSS CoinDesk | RSS | Không | ~2 ngày (25 item) | `pubDate` +0000 | — | ToS cấm robot/scraper; chỉ dùng cá nhân, phi thương mại | Chỉ thu tiếp từ nay; không có lịch sử |
| RSS Cointelegraph | RSS | Không | ~2 ngày (30 item) | `pubDate` +0000 | — | ToS cấm scraping **và cấm dùng nội dung cho AI/ML** | Không thu thân bài; tiêu đề lấy qua GDELT |
| RSS The Block | RSS | Không | ~2 ngày (20 item) | `pubDate` +0000 | Trang bài bị Cloudflare chặn (403) | robots.txt: `Content-Signal: search=yes, ai-input=yes, ai-train=yes`; trang ToS 403, chưa đọc được | Tiêu đề qua GDELT; sitemap có ngày |
| RSS Decrypt | RSS | Không | 55 item (đa số ~1 ngày, 1 bài ghim 2025-12-29) | `pubDate` +0000 | — | ToS cấm robot/scraper, cấm cache/archive | Tiêu đề qua GDELT |
| CryptoPanic | Có, **chỉ gói trả phí** | Có | Không thử được (cần token trả phí) | — | Gói Growth ~$50/tuần, ~$199/tháng (nguồn thứ ba) | Cấm dùng tên/logo khi chưa xin phép (nguồn thứ ba) | **Không** — bỏ khỏi `config.text.sources` |
| SEC EDGAR full-text search | Có (`efts.sec.gov/LATEST/search-index`) | Không, nhưng bắt buộc `User-Agent` có email | 2001 (theo tài liệu) | `file_date` chỉ có ngày; giờ chính xác = "Accepted" trên trang index, giờ New York (ET) | 10 req/s (SEC fair access) | Dữ liệu công, tự do dùng | **Có — nguồn phụ** (sự kiện pháp lý/ETF) |
| Reddit (API chính thức) | Có | Có (OAuth) | — | `created_utc` | 403 khi không OAuth | Data API terms | Không (ngoài phạm vi, tốn công) |
| Reddit qua Arctic Shift | Có (JSON) | Không | Thử được 2023-01-15 | `created_utc` epoch UTC | Không công bố | Bên thứ ba lưu lại dữ liệu Reddit, rủi ro license | Tùy chọn, chưa dùng |
| Bitcointalk | Không (HTML) | Không | Từ 2009 | Giờ hiển thị theo cài đặt diễn đàn, chưa kiểm | robots.txt chỉ khai sitemap | Không thấy API | Không |
| VN crypto: coin68.com | Không; `/feed/` trả HTML (hỏng) | Không | sitemap 34 file, có bài 2021 | `article:published_time` UTC (`...Z`) | — | Chưa tìm thấy trang điều khoản; © Coin68 | Nhánh VN, cần crawl HTML |
| VN crypto: blogtienao.com | RSS (10 item) + sitemap 35 file | Không | sitemap tới 2021 | `published_time` +00:00 | Có lúc timeout | Trang điều khoản 404 | Nhánh VN, cần crawl HTML |
| VN crypto: tapchibitcoin.io | RSS 1 item (2026-07-31) | Không | sitemap 2018-01 → 2025-09 | `published_time` +00:00 | — | Chưa kiểm | Không — gần như ngừng cập nhật |
| VN tiếng Anh: VnExpress International | RSS (60 item ~8 ngày) | Không | Sitemap trả về trang chủ HTML; tìm kiếm tiếng Anh trả 0 | `pubDate` +0700, `datePublished` +07:00 | robots.txt chặn nhiều bot (cả `archive.org_bot`) | © VnExpress | Thấp — chỉ qua GDELT `domain:` |
| VN tiếng Anh: VIR (vir.com.vn) | RSS 404; sitemap theo tháng từ 2010-08 | Không | 2010 | `published_time` +07:00 | Trang terms 500 | Chưa đọc được | Quá thưa: 2–7 bài crypto/tháng |
| VN tiếng Anh: Tuoi Tre News | RSS (50 item ~2 ngày) | Không | ~2 ngày | `pubDate` dạng `GMT+7` — **không chuẩn RFC 822**, phải parse riêng | — | Chưa kiểm | Thấp |
| VN tiếng Anh: Vietnam News, The Investor | RSS rỗng / 404 | — | — | — | — | — | Không |

## Chi tiết và bằng chứng

### GDELT DOC 2.0 API
- `GET https://api.gdeltproject.org/api/v2/doc/doc?query=bitcoin sourcelang:english&mode=artlist&format=json&maxrecords=5&startdatetime=20230115000000&enddatetime=20230116000000` → 200, trả `url, title, seendate, domain, language, sourcecountry`. Không có thân bài.
- `seendate` của bài cuối là `20230116T000000Z`, tức đúng biên `enddatetime`: biên có thể bao gồm cả hai đầu. Khi chia cửa sổ ngày phải dùng nửa mở hoặc khử trùng theo `url`.
- `maxrecords` tối đa 250/lệnh → phải chia cửa sổ nhỏ (theo ngày, hoặc vài giờ cho ngày nhiều tin).
- Giới hạn: thông báo khi 429 là `Please limit requests to one every 5 seconds`. Thực tế từ IP này: lệnh đầu tiên đã 429; nhịp 30 s chỉ 1/5 lệnh qua. Bộ thu phải có backoff dài + cache từng cửa sổ đã lấy.
- `mode=timelinevolraw`, `bitcoin sourcelang:english`, 2023-01-01 → 2026-09-30: 1.340 ngày, chỉ 1 ngày bằng 0 (2025-12-06, tổng bài GDELT `norm` = 494 → sự cố GDELT, không phải tin trống).
- **Đứt gãy cấu trúc**: tỷ lệ bài có "bitcoin" trên 10.000 bài GDELT là 30–44 suốt 2023-04 → 2024-07, rồi rơi về 11–14 từ 2025-01 trở đi, trong khi tổng `norm` gần như không đổi (~4,5–5,2 triệu/tháng). 2023-01 thấp bất thường (8,9). Mức rơi này khó là thật (2025-01 BTC vượt 100k) → nghi GDELT đổi tập nguồn/so khớp. Hệ quả: không dùng số lượng bài thô làm biến "attention"; phải chuẩn hóa theo `norm`, cố định tập domain, và thêm dummy/kiểm định đứt gãy quanh 2025-01.
- Kết quả theo domain (`domain:coindesk.com`, `domain:e.vnexpress.net`) và `sourcelang:vietnamese`: xem mục "GDELT theo domain" bên dưới.

### GDELT GKG 2.0 raw
- `https://data.gdeltproject.org/gdeltv2/20230115120000.gkg.csv.zip` → 200, 2,4 MB zip, 583 dòng/15 phút; 2 dòng chứa "bitcoin". File 2026-09-30 cũng có.
- Có URL + `<PAGE_TITLE>` trong trường Extras, mốc thời gian UTC.
- Cả mẫu ≈ 1.369 ngày × 96 file × 2,4 MB ≈ 315 GB nén → chỉ dùng lấp lỗ cho ngày DOC API thất bại, không tải toàn bộ.

### RSS bốn báo crypto tiếng Anh
- Feed: `coindesk.com/arc/outboundfeeds/rss/`, `cointelegraph.com/rss`, `theblock.co/rss.xml`, `decrypt.co/feed`. Tất cả 200, `pubDate` +0000.
- RSS chỉ phủ 1–2 ngày gần nhất → **không có lịch sử 2023–2026**. Chỉ dùng thu tiếp cho dashboard live.
- Lịch sử qua sitemap (chỉ kiểm tra, không crawl):
  - Cointelegraph: `sitemap/articles/YYYY-MM.xml` từ 2013-08; 2023-06: 755, 2024-06: 829, 2025-06: 855, 2026-06: 622 bài. `lastmod` là ngày sửa (2026-08-17), không phải ngày đăng. Trang bài có `datePublished` UTC (`2023-01-03T19:27:45.000Z`).
  - CoinDesk: `sitemaps/articles-1..16.xml` chỉ ~8.000 bài, lùi tới ~2025-10. Bài 2023 tìm lại được qua Wayback CDX (`coindesk.com/markets/2023/01/` prefix → 2.779 URL); trang bài vẫn sống, có `datePublished` UTC (`2023-01-10T11:53:25.948Z`).
  - Decrypt: `post-sitemapN.xml` (70 file) từ 2018; trang bài có `<time dateTime="...Z">` UTC.
  - The Block: `sitemap_tbco_post_type_post_N.xml`, 1.000 URL/file, URL chứa ngày (`/2023-10-11-...`), `lastmod` UTC. Trang bài bị Cloudflare challenge (403).
- Điều khoản (trích nguyên văn):
  - CoinDesk: "You agree that you will not use any robot, spider, scraper, or other automated means to access the Services for any purpose without our express written permission".
  - Cointelegraph: "automated scraping ... is strictly prohibited" và "Use of the Platform Content for training, fine-tuning, validation, benchmarking or operation of artificial intelligence systems, machine learning models ... is strictly prohibited without the prior written ...".
  - Decrypt: cấm "robots, spiders, scripts ... designed to data mine or scrape the Content" và "cache or archive the Content".
  - The Block: robots.txt cho phép AI (`ai-input=yes, ai-train=yes`), ToS chưa đọc được.
- Kết luận: không crawl thân bài bốn báo. Tiêu đề + URL + thời điểm của các domain này lấy qua GDELT (metadata do GDELT công bố).

### CryptoPanic
- `/api/v1/posts/` → trang Cloudflare "Attention Required!". `/api/developer/v2/posts/` → 404 `Unknown API endpoint. Valid paths are /api/{growth|growth_weekly|enterprise}/v2/{posts|portfolio|status}/`. `/api/growth/v2/posts/?auth_token=INVALID` → 400 `Token not found`. RSS `/news/rss/` → 410 Gone.
- Gói Developer miễn phí đã bị bỏ (nguồn thứ ba: dlthub, anygen); chỉ còn Growth (~$50/tuần, ~$199/tháng) và Enterprise. Trang giá render bằng JS, không đọc trực tiếp được.
- Kết luận: loại khỏi mẫu. Đề xuất đổi `config.text.sources` thành `[gdelt, rss, edgar]` (chờ người dùng duyệt; lần này chỉ đọc).

### SEC EDGAR full-text search
- `GET https://efts.sec.gov/LATEST/search-index?q="bitcoin"&dateRange=custom&startdt=2023-01-01&enddt=2023-01-31&forms=8-K` → 200, 52 hit. Trả `adsh, ciks, display_names, form, file_date, root_forms, items, file_type`.
- `q="bitcoin"`, 2023-01-01 → 2026-09-30, `forms=8-K,S-1,19b-4` → 6.058 hit, 100 hit/trang → chia theo khoảng ngày để phân trang.
- **Bẫy point-in-time**: ví dụ `0001193125-23-015309` có "Accepted 2023-01-25 18:04:15" (ET) nhưng `file_date` 2023-01-26 (nộp sau 17:30 ET được tính ngày làm việc kế tiếp). Gán ngày phải dùng Accepted → đổi America/New_York → UTC; 18:04 ET = 23:04 UTC ngày 25.
- Bắt buộc `User-Agent: <tên> <email>` (email lấy từ env `CONTACT_EMAIL`), tối đa 10 req/s.
- SEC press release RSS (`sec.gov/news/pressreleases.rss`) chỉ ~6 tuần gần nhất, `pubDate` -0400.

### Reddit, Bitcointalk
- `reddit.com/r/Bitcoin/new.json` không OAuth → 403. Arctic Shift (`arctic-shift.photon-reddit.com/api/posts/search?subreddit=Bitcoin&after=2023-01-15&before=2023-01-16`) → 200, có `created_utc`, không cần key; đây là kho bên thứ ba, license chưa rõ.
- Bitcointalk: HTML 200, không API, có `sitemap.php`. Diễn đàn nhiễu, không thuộc nhánh chính.

### Tin crypto tiếng Việt
- coin68.com: `/feed/` trả HTML (Next.js), không có RSS. Sitemap 34 file. Trang bài có `article:published_time` UTC (`2021-06-07T02:52:58.000000Z`).
- blogtienao.com: WordPress, RSS 10 item, sitemap 35 file. `published_time` +00:00 (`2024-04-30T16:46:01+00:00`).
- tapchibitcoin.io: RSS chỉ 1 item (2026-07-31), sitemap tin dừng ở 2025-09 → coi như ngừng.
- Timezone: hai nguồn chính ghi giờ có offset UTC, không phải +07. `config.text.vn_source_tz` chỉ áp dụng khi chuỗi giờ không có offset.
- Cả ba không có API; lấy lịch sử = crawl HTML từ sitemap. Chưa tìm thấy điều khoản cho phép → chỉ lưu tiêu đề + URL + giờ, không phân phối lại thân bài.

### Bản tiếng Anh của báo VN
- VnExpress International: RSS `e.vnexpress.net/rss/business.rss` 60 item (~8 ngày), `pubDate` +0700, `datePublished` +07:00. `articles_sitemap.xml.gz` trả trang chủ HTML; tìm kiếm tiếng Anh (`timkiem.vnexpress.net ... lang=en`) trả 0 bài; trang topic trả 0 link. robots.txt chặn nhiều bot.
- VIR: sitemap theo tháng `stores/lookssitemaps/site_1/sitemap-month-YYYY-MM.xml` từ 2010-08; số bài crypto (lọc URL crypto/bitcoin/blockchain/stablecoin): 2023-03: 2, 2023-06: 2, 2024-03: 6, 2025-03: 7. `published_time` +07:00.
- Tuoi Tre News: RSS 50 item, `pubDate` kiểu `Fri, 16 Oct 2026 14:09:00 GMT+7` (không chuẩn).
- Vietnam News `rss/economy.rss`: 0 item. The Investor `rss/home.rss`: 404.
- Tiếng Việt khác: CafeF RSS `pubDate` năm 2 chữ số (`Fri, 16 Oct 26`) → parse riêng.
- Kết luận: tin crypto tiếng Anh của báo VN quá ít cho chuỗi ngày. Chỉ dùng như bộ đếm theo tháng/sự kiện, lấy qua GDELT `domain:`.

## GDELT theo domain

- `bitcoin sourcelang:vietnamese`, 2023-01: 250 bài (chạm trần `maxrecords`), domain nhiều nhất: baomoi.com 58, cafef.vn 47, laodong.vn 33, genk.vn 11, voh.com.vn 10. GDELT phủ tin tiếng Việt đủ dày → dùng được để tìm URL + tiêu đề cho nhánh VN, thay cho crawl sitemap.
- `domain:coindesk.com` (2023-03-01, 1 ngày) và `domain:e.vnexpress.net` (2023): **chưa có kết quả** — 6 lần thử (nhịp 30 s, 90 s, nghỉ 10 phút) đều 429. Trong cùng thời gian, truy vấn không có `domain:` thì qua được 2/2 lần sau khi nghỉ. Chưa rõ GDELT có throttle riêng cho `domain:` hay chỉ trùng hợp; bước thu phải thử lại trước khi chốt danh sách domain.
- Tổng cộng hôm nay: 3/17 lệnh DOC API thành công.

## Kết luận cho mẫu 2023–2026

1. **Nhánh chính (EN)**: GDELT DOC 2.0 `artlist`, tiêu đề tiếng Anh, truy vấn theo tài sản (BTC/ETH/SOL/BNB/XRP) và theo `domain:` các báo crypto (coindesk.com, cointelegraph.com, theblock.co, decrypt.co) + báo tài chính lớn. Chấm sentiment trên **tiêu đề** (LM, Harvard IV-4, FinBERT). Không lấy thân bài vì ToS ba trên bốn báo cấm scraping.
2. **Mốc thời gian**: `public_ts_utc = seendate` của GDELT. Giờ này luôn ≥ giờ đăng, nên an toàn cho point-in-time (không nhìn trước). Nếu có `datePublished` thật thì giữ để đo độ trễ, không dùng thay.
3. **Nguồn phụ**: SEC EDGAR FTS (8-K, S-1 nhắc crypto) cho narrative `regulation`/`etf_institutional`, gán ngày theo giờ Accepted đổi sang UTC.
4. **RSS 4 báo**: chỉ thu tiếp từ 2026-10 cho dashboard live; không thuộc mẫu nghiên cứu.
5. **Loại**: CryptoPanic (trả phí), Reddit/Bitcointalk (license/nhiễu), tapchibitcoin (ngừng), VnExpress Intl/VIR/Tuoi Tre News làm chuỗi ngày (quá thưa).
6. **Nhánh VN (phụ)**: GDELT `sourcelang:vietnamese` (baomoi, cafef, laodong…) + coin68/blogtienao, chỉ tiêu đề + giờ, chấm bằng `VietScorer`; không dịch.
7. **Rủi ro cần xử lý ở bước thu**: GDELT 429 (backoff + cache theo cửa sổ), đứt gãy volume quanh 2025-01 (chuẩn hóa `norm`, panel domain cố định, dummy), ngày lỗi 2025-12-06, biên `enddatetime` bao gồm (khử trùng `url`).

Nghĩa là gì: mẫu 2023–2026 khả thi với chi phí 0 nếu chấp nhận corpus là tiêu đề. Biến "lượng tin" thô từ GDELT không so sánh được trước/sau 2025, nên kết luận kinh tế phải dựa trên tỷ lệ/tone đã chuẩn hóa chứ không dựa vào số bài.
