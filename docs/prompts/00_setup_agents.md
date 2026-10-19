# Cài plugin (làm 1 lần trên máy, trước khi mở 2 phiên)

> Lệnh lấy theo README các repo tại thời điểm 16/10/2026 — nếu báo lỗi, xem README gốc của từng repo.

## Clone (1 folder, nhánh `dev` – xem AGENTS.md "Làm chung 1 folder")
```bash
git clone https://github.com/thienanpham160806-code/crypto-narrative-nlp.git
cd crypto-narrative-nlp
git checkout dev
```

## Claude Code (mở trong `crypto-narrative-nlp/`)
```text
/plugin marketplace add JuliusBrussee/caveman
/plugin install caveman@caveman
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
/reload-plugins
/codex:setup
```
```bash
npx -y skills add DietrichGebert/ponytail --skill ponytail --agent claude-code
npx -y skills add pbakaus/impeccable --agent claude-code
```

## Codex CLI (mở trong `crypto-narrative-nlp/`)
```bash
npx -y skills add JuliusBrussee/caveman --agent codex
npx -y skills add DietrichGebert/ponytail --skill ponytail --agent codex
npx claude-mem install          # chọn thêm Codex CLI trong danh sách agent
```
Codex đọc `AGENTS.md` ở gốc repo tự động.

## Kiểm tra nhanh
- Claude: gõ `/caveman` và `/ponytail` thấy phản hồi; `/codex:status` chạy được.
- Codex: hỏi "list skills" thấy caveman, ponytail.
