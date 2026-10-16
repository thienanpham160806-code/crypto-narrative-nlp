# Cài plugin (làm 1 lần trên máy, trước khi mở 2 phiên)

> Lệnh lấy theo README các repo tại thời điểm 16/10/2026 — nếu báo lỗi, xem README gốc của từng repo.

## Clone + 2 worktree (để Claude và Codex không giẫm chân nhau)
```bash
git clone https://github.com/thienanpham160806-code/crypto-narrative-nlp.git
cd crypto-narrative-nlp
git worktree add ../cnn-claude -b claude/phase1
git worktree add ../cnn-codex  -b codex/phase1
```

## Claude Code (mở trong `../cnn-claude`)
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

## Codex CLI (mở trong `../cnn-codex`)
```bash
npx -y skills add JuliusBrussee/caveman --agent codex
npx -y skills add DietrichGebert/ponytail --skill ponytail --agent codex
npx claude-mem install          # chọn thêm Codex CLI trong danh sách agent
```
Codex đọc `AGENTS.md` ở gốc repo tự động.

## Kiểm tra nhanh
- Claude: gõ `/caveman` và `/ponytail` thấy phản hồi; `/codex:status` chạy được.
- Codex: hỏi "list skills" thấy caveman, ponytail.
