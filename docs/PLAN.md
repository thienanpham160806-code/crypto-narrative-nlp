# Kế hoạch & phân công (Claude Code ∥ Codex)

Hai agent chạy **cùng lúc trên hai nhánh/worktree riêng**, chỉ sửa thư mục mình sở hữu, giao tiếp qua `docs/DATA_CONTRACT.md` và `docs/PROGRESS.md`.

| Vùng | Owner | Nhánh |
|---|---|---|
| `src/data/news_*`, `src/data/vn_*`, `src/features/**`, `dict/`, `dashboard/`, `paper/` | **Claude** | `claude/*` |
| `src/data/market.py`, `src/models/**`, `src/evaluation/**`, `tests/fixtures/`, `notebooks/` | **Codex** | `codex/*` |
| `config/`, `docs/DATA_CONTRACT.md`, `README.md` | chung — sửa nhỏ, ghi PROGRESS | — |

## Giai đoạn
| # | Claude | Codex | Xong khi |
|---|---|---|---|
| 1 | C1 Thu thập text: GDELT + RSS (+ CryptoPanic nếu có key) + SEC text, dedup, asset tagging, timestamp → `documents.parquet`; bảng corpus stats + timestamp accuracy | X1 Giá Binance (ccxt) daily + hourly → `market_daily.parquet` (ret, RV, volume); fixture `text_daily` giả | 2 file đúng contract, test pass |
| 2 | C2 NLP: LM/Harvard (port), FinBERT (port), `crypto_vn.csv` + VietScorer cho tin Việt; narrative LDA → BERTopic → zero-shot/LLM; **validation 300 tiêu đề gán tay**; `text_daily.parquet` | X2 Kinh tế lượng trên fixture: predictive OLS HAC (RQ1–3), Wald β⁻=β⁺ (RQ2), VAR/Granger 2 chiều (RQ4) | bảng 3–5 của mục 4.1 |
| 3 | C3 Dashboard (impeccable) đọc `outputs/` + snippet đại diện | X3 Walk-forward: market-only vs market+text (EN, XGB, LGBM), Diebold–Mariano, SHAP, chiến lược tín hiệu (sau phí) | bảng 6 + SHAP |
| 4 | C4 Paper + README | X4 Robustness (horizon, trọng số w_d, bỏ tin price_speculation, sub-period), event study quanh `public_ts_utc` | checklist mục 6 blueprint đủ |

Mỗi cuối giai đoạn: Claude gọi `/codex:review --base main`; trước merge giai đoạn 2 & 3: `/codex:adversarial-review` tập trung **leakage**.
