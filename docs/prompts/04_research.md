# Prompt nghiên cứu (chạy ở Claude CLI, song song với 2 agent chính)

Chỉ ghi file trong `docs/research/` và `paper/`; commit bằng `git add <đúng file>` — không `add -A`.

## R1 — Mã nguồn GitHub đáng học
```text
/caveman lite
Repo crypto-narrative-nlp (Blueprint 10). Đọc docs/blueprint.md, docs/PLAN.md, docs/PORTED.md trước.
Tìm trên GitHub 10–15 repo liên quan trực tiếp: crypto news/social sentiment → return/volatility; FinBERT/CryptoBERT trên tin crypto; BERTopic/LDA cho narrative tài chính; GDELT/RSS/CryptoPanic crawler; walk-forward/OOS cho dự báo crypto; Diebold–Mariano, Granger cho sentiment–price; dashboard narrative.
Lọc: còn cập nhật hoặc nhiều sao, có code chạy được (không chỉ notebook rời rạc), ưu tiên repo đi kèm paper.
Với mỗi repo, MỞ code thật (gh api / git clone --depth 1 vào thư mục tạm ngoài repo) và ghi vào docs/research/REPOS.md:
- link, sao, cập nhật lần cuối, GIẤY PHÉP (MIT/Apache/BSD → được chép code có ghi nguồn; GPL/không giấy phép → CHỈ học ý tưởng, tự viết lại)
- họ làm tốt điều gì (cụ thể tới file/hàm), điểm yếu (leakage? không có OOS? timezone?)
- áp dụng vào module nào của mình (src/... ), owner Claude hay Codex (theo PLAN.md), độ ưu tiên P1/P2/P3
Cuối file: bảng "Top 5 nên áp dụng ngay" + "Bẫy họ mắc mà mình phải tránh". Không sửa src/. Xóa thư mục tạm khi xong.
```

## R2 — Paper đọc được (open access)
```text
/caveman lite
Repo crypto-narrative-nlp (Blueprint 10). Đọc docs/blueprint.md (RQ1–RQ5, mục 5 tài liệu gợi ý).
Tìm 15–25 paper liên quan TRỰC TIẾP: news/social sentiment & crypto return/volatility/volume; FinBERT vs dictionary (Loughran–McDonald); topic modeling/narratives trong tài chính (vd Bybee et al. "Business News and Business Cycles", Shiller narrative economics); asymmetry tin xấu; lead-lag/Granger; OOS forecast có text; look-ahead bias trong LLM/text cho tài chính. Bao gồm cả 7 bài trong blueprint.
Nguồn: arXiv, SSRN, NBER working papers, OpenAlex, Semantic Scholar, Unpaywall, kho của trường/tác giả.
CHỈ giữ bài có bản toàn văn đọc được miễn phí: tải hoặc mở được PDF/HTML thật thì mới ghi; bị paywall thì ghi vào mục "Chỉ có abstract" riêng. Không bịa số liệu, không bịa DOI.
Ghi docs/research/PAPERS.md, mỗi bài: trích dẫn APA, link toàn văn (OA), dữ liệu & giai đoạn, phương pháp, kết quả chính (có số), trả lời RQ nào của mình, điều mình nên làm theo (biến, cửa sổ, kiểm định, robustness).
Thêm paper/references.bib và paper/related_work.md (viết học thuật tiếng Việt, gom theo RQ, cuối có "khoảng trống nghiên cứu" mà đề tài lấp).
```

## R3 — Đưa phát hiện vào kế hoạch (chạy sau R1, R2)
```text
/caveman lite
Đọc docs/research/REPOS.md và docs/research/PAPERS.md. Viết docs/research/ADOPT.md: danh sách thay đổi cụ thể (file, hàm, owner Claude/Codex, P1/P2/P3, nguồn repo/paper), và đề xuất chỉnh docs/PLAN.md + docs/DATA_CONTRACT.md nếu cần. KHÔNG tự sửa src/. Append 1 dòng vào docs/PROGRESS.md: "ADOPT.md sẵn sàng — Claude/Codex đọc trước giai đoạn kế".
```
Sau đó nhắn cho cả 2 agent chính: `Đọc docs/research/ADOPT.md, làm các mục P1 thuộc phần của bạn, ghi nguồn vào CREDITS.md.`
