# Prompt phiên Codex CLI (dán vào `../cnn-codex`, chạy cùng lúc với Claude)

```text
$caveman full
$ponytail full

Repo: crypto-narrative-nlp (Blueprint 10). Đọc AGENTS.md, docs/PLAN.md, docs/DATA_CONTRACT.md, docs/PORTED.md, docs/PROGRESS.md, docs/blueprint.md; nếu có claude-mem thì tra lịch sử phiên trước.
Bạn là owner phần MARKET DATA + ECONOMETRICS + ML (src/data/market.py, src/models/, src/evaluation/, tests/fixtures/, notebooks/).
Claude Code đang chạy SONG SONG làm text/NLP — KHÔNG sửa src/features/, src/data/news_*, src/data/vn_*, dict/, dashboard/, paper/.
Text thật chưa có → dùng fixture đúng DATA_CONTRACT §3, khi Claude merge thì chỉ cần đổi đường dẫn.

X1 – Dữ liệu thị trường
- src/data/market.py: ccxt Binance, assets trong config.sample.assets (cặp USDT), OHLCV 1h + 1d từ sample.start → sample.end, cache data/raw/. Tính ret (log), rv = Σ r_1h² trong ngày UTC, volume_usd, logvol, ret_lag1..7 → data/processed/market_daily.parquet (§4).
- tests/fixtures/make_fixtures.py: sinh text_daily giả (seed) đúng schema, có cài sẵn một tín hiệu nhỏ để kiểm tra pipeline tìm lại được nó.

X2 – Kinh tế lượng (src/models/econometrics.py, output outputs/tables/)
- RQ1/RQ3: r_{t+h} và RV_{t+h} hồi quy trên Sent_t, Attention_k,t, controls (ret lags, rv, logvol), OLS Newey–West HAC (config.model.hac_lags), h ∈ config.model.horizons; so cột sent_lm vs sent_hv vs sent_finbert.
- RQ2: RV_{t+h} = α + β⁻NegSent + β⁺PosSent + γ'X; Wald H0: β⁻ = β⁺.
- RQ4: VAR (chọn lag bằng AIC ≤ config.model.var_maxlags) + Granger hai chiều Sent↔Return, Sent↔RV; kết luận rõ chiều nào.
- Hàm make_panel() là nơi DUY NHẤT dịch target −h; có test chứng minh feature ngày t không chứa dữ liệu ≥ t+1.

X3 – ML out-of-sample (src/models/ml.py, src/evaluation/oos.py)
- Walk-forward/expanding window, tuning chỉ trên train/valid (split trong config), test chạm 1 lần cuối.
- Elastic Net, XGBoost, LightGBM; mỗi model 2 bản: market-only vs market+text (RQ5).
- Metric: RMSE/MAE/R²_oos (so với historical mean), QLIKE cho RV, Diebold–Mariano market vs market+text; SHAP cho bản tốt nhất.
- Chiến lược tín hiệu (chỉ là economic-value test): long/flat theo dự báo, trừ phí 10 bps, so buy&hold, Sharpe.

X4 (khi Claude đã có text thật) – robustness: horizon, trọng số w_d (equal/source), bỏ narrative price_speculation, chia sub-period; viết lại main() của src/evaluation/event_study.py (đã port) cho 24/7: T0 = bar 1h đầu tiên sau public_ts_utc, market = BTC.

Quy tắc: pytest -q không cần mạng; commit nhỏ message tiếng Anh; code tối giản theo ponytail; mỗi bảng output kèm 1–2 dòng diễn giải kinh tế trong outputs/tables/README.md. Cuối phiên append docs/PROGRESS.md, push nhánh codex/phase1, mở PR vào main.
Báo lại: file đã đổi, bảng kết quả chính, rủi ro leakage còn nghi ngờ.
```
