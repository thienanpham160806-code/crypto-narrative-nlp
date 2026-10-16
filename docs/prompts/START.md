# Bắt đầu nhanh (2 prompt)

1. VS Code → terminal: `git clone https://github.com/thienanpham160806-code/crypto-narrative-nlp.git` → `code crypto-narrative-nlp`
2. Mở Claude Code trong thư mục đó → dán **Prompt 1**. Claude tự cài plugin cho cả mình lẫn Codex.
3. Claude báo "Codex sẵn sàng" → mở Codex trong **cùng thư mục** `crypto-narrative-nlp` → dán **Prompt 2**. Cả hai làm trên nhánh `dev` (luật git: `AGENTS.md` mục "Làm chung 1 folder").

## Prompt 1 — Claude Code
```text
Repo crypto-narrative-nlp (Blueprint 10). Đọc CLAUDE.md, AGENTS.md, docs/*.md trước. Không tường thuật từng bước, chỉ báo kết quả.

BƯỚC 0 – Setup (tự làm hết bằng terminal, chỉ dừng khi cần tôi đăng nhập/bấm):
- Plugin Claude Code: caveman (JuliusBrussee/caveman), codex (openai/codex-plugin-cc), claude-mem (thedotmack/claude-mem) qua `claude plugin marketplace add` + `claude plugin install`; skill ponytail (DietrichGebert/ponytail) và impeccable (pbakaus/impeccable) qua `npx -y skills add ... --agent claude-code`. Lệnh nào lỗi thì đọc README gốc của repo đó và sửa.
- Cho Codex: kiểm tra `codex --version` (chưa có thì `npm i -g @openai/codex`); cài caveman + ponytail với `--agent codex`; chạy `npx claude-mem install` chọn thêm Codex.
- `git switch dev` (chưa có thì `git switch -c dev origin/main`); cả Claude và Codex làm trên `dev`, cùng folder.
- Tạo venv, `pip install -r requirements.txt`, `pytest -q` phải pass.
- Báo tôi: (1) cần khởi động lại Claude Code để nạp plugin, (2) nếu Codex chưa đăng nhập thì tôi chạy `codex login`, (3) mở Codex trong cùng folder. Ghi "setup xong" vào docs/PROGRESS.md.

Sau khi tôi khởi động lại và gõ "tiếp": bật /caveman full và /ponytail, chạy /codex:setup, rồi làm giai đoạn C1 → C2 đúng theo docs/prompts/01_claude_code.md (thu thập tin + timestamp công bố, NLP, text_daily). Cuối mỗi giai đoạn tự gọi /codex:review --base main --background, đọc /codex:result, sửa lỗi hợp lệ. Trước khi xong C2 gọi /codex:adversarial-review tập trung leakage/timezone/dedup. `git pull --rebase` rồi push `dev`; hết giai đoạn mở PR `dev` → `main`.
```

## Prompt 2 — Codex (mở cùng thư mục crypto-narrative-nlp)
```text
$caveman full
$ponytail full
Repo crypto-narrative-nlp (Blueprint 10), bạn ở nhánh dev (chung folder với Claude; tuân AGENTS.md mục "Làm chung 1 folder"). Đọc AGENTS.md, docs/PLAN.md, docs/DATA_CONTRACT.md, docs/PROGRESS.md, docs/blueprint.md; có claude-mem thì tra phiên trước.
Bạn owner phần MARKET DATA + ECONOMETRICS + ML. Claude Code chạy song song làm text/NLP — KHÔNG sửa src/features/, src/data/news_*, src/data/vn_*, dict/, dashboard/, paper/.
Làm X1 → X3 đúng theo docs/prompts/02_codex.md (Binance qua ccxt → market_daily; fixture text_daily giả đúng contract; HAC + Wald + VAR/Granger; walk-forward EN/XGB/LGBM market-only vs market+text, Diebold–Mariano, SHAP). pytest -q không cần mạng. Cuối phiên append docs/PROGRESS.md, `git pull --rebase`, push dev. Báo: file đã đổi, bảng kết quả chính, rủi ro leakage còn nghi ngờ.
```
