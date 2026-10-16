# RESEARCH BLUEPRINT 10

## Crypto Narrative & NLP Sentiment Intelligence

*Xây chỉ số narrative/sentiment từ news và social text để giải thích và dự báo return, volatility và volume của crypto*

> **Môn học gợi ý:** Công nghệ ứng dụng trong Tài chính / Financial Technology  
> **Định dạng:** Research + Code + Financial Product  
> **Mức độ:** Undergraduate advanced / MSc-entry level  
> **Thời lượng phù hợp:** 8–12 tuần  
> **Ngôn ngữ triển khai:** Python ưu tiên; R có thể dùng cho econometrics  
> **Lưu ý:** Đây là thiết kế học thuật và mô phỏng nghiên cứu, không phải khuyến nghị đầu tư.

---

## 1. Tên chủ đề

**Crypto Narrative and NLP Sentiment Intelligence: Transformer-Based Text Signals for Cryptocurrency Returns, Volatility and Trading Activity**

**Hướng nghiên cứu:** NLP, Behavioral Finance, Asset Pricing, Machine Learning, Alternative Data.

---

## 2. Mục tiêu nghiên cứu, câu hỏi nghiên cứu và mô hình dự kiến

### 2.1. Mục tiêu nghiên cứu

Crypto là thị trường đặc biệt nhạy với narratives như regulation, ETF, institutional adoption, hacks, DeFi, stablecoins, AI tokens và monetary policy. Dự án xây các chỉ số **sentiment, attention và narrative intensity** từ text, rồi kiểm tra liệu các chỉ số này có incremental information cho return/volatility/volume hay không.

Mục tiêu:

1. Thu thập corpus news/social text có timestamp.
2. So sánh lexicon với FinBERT/transformer sentiment.
3. Phát hiện topic/narrative bằng topic modeling hoặc embeddings.
4. Xây daily narrative indices.
5. Kiểm định lead-lag và out-of-sample prediction.
6. Xây Crypto Narrative Intelligence dashboard.

### 2.2. Câu hỏi nghiên cứu

- **RQ1:** Transformer sentiment có tốt hơn dictionary sentiment trong giải thích crypto outcomes không?
- **RQ2:** Negative sentiment có tác động bất đối xứng mạnh hơn positive sentiment không?
- **RQ3:** Narrative attention nào liên hệ mạnh nhất với return, volatility và volume?
- **RQ4:** Text signals dẫn thị trường hay chủ yếu phản ứng với price movements?
- **RQ5:** Sentiment/narratives có cải thiện out-of-sample forecast ngoài market variables không?

### 2.3. Text representation

Mỗi document \(d\):

\[
Sentiment_d\in[-1,1]
\]

Daily index:

\[
Sent_t=
\frac{\sum_{d\in t}w_d Sentiment_d}
{\sum_{d\in t}w_d}
\]

Weights \(w_d\) có thể:
- equal;
- source-based;
- engagement-based nếu hợp lệ.

Attention:

\[
Attention_{k,t}
=
\frac{N_{k,t}}{N_t}
\]

với \(k\) là narrative.

### 2.4. Narrative extraction

Benchmark:
- LDA.

Advanced:
- BERTopic;
- sentence embeddings + clustering;
- zero-shot classification với predefined narratives.

Narratives dự kiến:

- regulation;
- ETF/institutional;
- security/hacks;
- stablecoins;
- DeFi;
- AI/token narratives;
- macro/monetary;
- price/speculation.

### 2.5. Predictive regression

\[
r_{t+h}
=
\alpha+
\beta Sent_t+
\theta Attention_{k,t}
+\gamma'X_t+
\varepsilon_{t+h}
\]

Volatility:

\[
RV_{t+h}
=
\alpha+
\beta^- NegSent_t+
\beta^+ PosSent_t+
\gamma'X_t+
\varepsilon_{t+h}
\]

Asymmetry được kiểm tra bằng:

\[
H_0:\beta^-=\beta^+
\]

### 2.6. Lead-lag / reverse causality

Dùng VAR/Granger:

\[
Sentiment_t
\leftrightarrow
Return_t
\]

Nếu return dự báo sentiment nhưng sentiment không dự báo return, cần kết luận rằng text index chủ yếu phản ứng với giá.

### 2.7. ML models

Baseline market-only:
- lagged returns;
- volatility;
- volume.

Text-augmented:
- sentiment;
- attention;
- embeddings/narratives.

Models:
- Elastic Net;
- XGBoost;
- LightGBM;
- LSTM/Transformer nếu sample đủ lớn.

So sánh:

\[
Model_{market}
\quad vs \quad
Model_{market+text}
\]

Đây là test incremental value chính.

### 2.8. Avoiding text leakage

Cực kỳ quan trọng:

- article publication time phải trước return horizon;
- không dùng headline xuất bản sau market move để dự báo market move đó;
- duplicate news phải loại;
- timezone phải chuẩn hóa;
- train NLP classifier trên dữ liệu không “nhìn” test period khi tuning.

---

## 3. Data dự kiến

### 3.1. Text sources

Tùy điều kiện API/licensing:

- crypto/financial news RSS/public archives;
- GDELT-type public news;
- Reddit/public forums;
- Bitcointalk archives;
- project announcements.

Nếu social platform API khó, chọn news corpus nhỏ nhưng sạch.

### 3.2. Market data

- BTC;
- ETH;
- có thể 5–10 major coins.

Nguồn:
- Binance;
- CoinGecko;
- CryptoCompare.

### 3.3. Fields

Text table:

```text
timestamp
source
headline
body_optional
asset_tags
url/id
```

Derived:

```text
sentiment
positive_prob
negative_prob
topic
topic_probability
embedding
```

Daily merge:

```text
date
asset
return
volatility
volume
sentiment
negative_sentiment
attention_regulation
attention_defi
attention_security
...
```

### 3.4. Sample

Ít nhất 2–3 năm daily nếu làm time-series forecasting.

Nếu corpus lớn intraday, có thể thực hiện event study quanh publication time.

---

## 4. Output dự kiến

### 4.1. Academic output

Bảng:

1. corpus statistics;
2. narrative taxonomy;
3. sentiment validation;
4. predictive regressions;
5. VAR/Granger;
6. out-of-sample model comparison.

Hình:

- topic prevalence through time;
- sentiment index vs BTC;
- narrative event timelines;
- SHAP importance;
- cumulative performance của signal-based strategy chỉ như economic-value test.

### 4.2. Product output

**Crypto Narrative Intelligence Platform**

Dashboard:

```text
Dominant narrative: Regulation
Narrative intensity: High
Overall sentiment: -0.42
Negative-news acceleration: +35%
BTC volatility risk: Elevated
```

Charts:
- narrative trends;
- sentiment;
- asset-specific attention;
- text snippets đại diện;
- predicted volatility.

### 4.3. NLP pipeline

```text
Ingestion
  ↓
Deduplication
  ↓
Cleaning
  ↓
Asset tagging
  ↓
FinBERT / Transformer sentiment
  ↓
Topic/Narrative model
  ↓
Daily indices
  ↓
Econometric / ML model
  ↓
Dashboard
```

### 4.4. Tiêu chí chất lượng

Dự án không được dừng ở “word cloud” hoặc sentiment score.

Phải chứng minh:
- validity của text signal;
- timing;
- incremental predictive value;
- economic interpretation;
- robustness.

---

## 5. Tài liệu tham khảo gợi ý

1. Araci, D. (2019). *FinBERT: Financial Sentiment Analysis with Pre-trained Language Models*. arXiv:1908.10063.
2. Kraaijeveld, O., & De Smedt, J. (2020). The predictive power of public Twitter sentiment for forecasting cryptocurrency prices. *Journal of International Financial Markets, Institutions and Money*.
3. Chou, K.-H., Day, M.-Y., & Chiu, C.-L. (2023). Do Bitcoin news information flow and return volatility fit the sequential information arrival hypothesis and the mixture of distribution hypothesis? *International Review of Economics & Finance, 88*, 365–385.
4. Walker, C. B. (2024). Going mainstream: Cryptocurrency narratives in newspapers. *International Review of Financial Analysis, 94*, 103305.
5. Kao, Y.-S., Day, M.-Y., & Chou, K.-H. (2024). A comparison of Bitcoin futures return and return volatility based on news sentiment contemporaneously or lead-lag. *North American Journal of Economics and Finance, 72*, 102159.
6. Gür, E., & Ünal, E. (2026). The impact of news sentiment on the Bitcoin price via machine learning and deep learning-based NLP models. *Journal of Forecasting*. https://doi.org/10.1002/for.70068
7. Khaksar, E., Biktimirov, E. N., Ayanso, A., & Sokolyk, T. (2026). Bitcoin returns and volume: Uncovering investor sentiment through topic modeling. *International Review of Financial Analysis, 116*, 105197.


---

## 6. Checklist bàn giao tối thiểu cho nhóm

- [ ] Research question được phát biểu rõ và nhất quán với model.
- [ ] Data dictionary và source log.
- [ ] Script tải/chuẩn hóa dữ liệu có thể chạy lại.
- [ ] Không có look-ahead bias/data leakage.
- [ ] Có econometric/statistical benchmark.
- [ ] Có ít nhất một model nâng cao.
- [ ] Có untouched out-of-sample test.
- [ ] Có robustness hoặc sensitivity analysis.
- [ ] Có README hướng dẫn chạy code.
- [ ] Có dashboard/app hoặc research visualization có thể demo.
- [ ] Có báo cáo học thuật giải thích economic meaning, không chỉ model metrics.

## 7. Cấu trúc repository đề xuất

```text
project/
├── README.md
├── requirements.txt
├── config/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   └── utils/
├── notebooks/
├── dashboard/
├── tests/
├── outputs/
│   ├── tables/
│   └── figures/
└── paper/
```

> **Nguyên tắc chung:** một model đơn giản nhưng point-in-time đúng, có benchmark và kiểm định out-of-sample tốt hơn một model phức tạp nhưng leakage hoặc không thể tái lập.
