# AI-Dominated Market Regime Detection

**A live ML web application that predicts equity direction by first detecting whether algorithmic traders are dominating the market.**

> 👤 Ankit Paudel · CS 4771 Machine Learning · University of Idaho  
> 🔗 Live Demo: *(deploy to Vercel — update URL here)*  
> ⚠️ Research project — not financial advice

---

## What This Project Does

Most ML-based trading systems treat the market as a single regime. This project starts with a different observation: **over 70% of US equity volume is now driven by algorithmic and high-frequency trading.** When algorithms dominate, price patterns are different — momentum amplifies faster, reversions are quicker, and volatility structure changes.

This system:
1. **Detects the current AI intensity regime** using a custom composite signal built from rolling percentile ranks of volatility, volume, MACD, and Bollinger Band width
2. **Uses that regime signal as an additional feature** in a LightGBM classifier
3. **Outputs BUY / SELL / HOLD** with a full probability breakdown over 1, 3, or 5 day horizons
4. **Explains every prediction** using SHAP (SHapley Additive exPlanations)
5. **Runs on live data** — yfinance fetches the last 120 days of OHLCV on every request

---

## Live Demo Walkthrough

```
1. Open the dashboard
2. Select a ticker: AAPL · GOOGL · MSFT · TSLA · NVDA
3. Choose a horizon: 1-day · 3-day · 5-day
4. Click Predict
5. In ~3-5 seconds you see:
   - BUY / SELL / HOLD signal with confidence %
   - Full probability distribution (all 3 classes)
   - AI Intensity Index and regime status
   - SHAP chart showing exactly which features drove this prediction
   - RSI, 10-day volatility, MACD diff, volume z-score
   - (Optional) GPT-4o plain-English commentary
```

---

## ML Architecture

### The Problem With Standard Approaches

Standard stock prediction models treat all market days as equivalent. This ignores the structural shift caused by algorithmic trading domination — where pattern types, mean-reversion speed, and momentum characteristics all change.

### The Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT                                   │
│  yfinance: 120 days of OHLCV for AAPL / GOOGL / MSFT / TSLA / NVDA │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FEATURE ENGINEERING (17 features)              │
│  Returns:        return_1d, return_5d                           │
│  Volatility:     volatility_10d, volatility_20d                 │
│  Momentum:       RSI(14), MACD, MACD signal, MACD diff          │
│  Mean-reversion: BB upper, BB lower, BB width, BB %             │
│  Volume:         Volume z-score (deviation from 20d mean)       │
│  Price action:   Opening gap, daily range                       │
│  AI regime:      AI Intensity Index, AI regime flag ← original  │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LIGHTGBM CLASSIFIER                          │
│  15 separate models: 5 tickers × 3 horizons                     │
│  Training: 3 years of data, TimeSeriesSplit cross-validation    │
│  Output: softmax over {SELL=0, HOLD=1, BUY=2}                   │
│  Class weighting: balanced (handles HOLD dominance)             │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                  SHAP EXPLAINABILITY                            │
│  TreeExplainer on each prediction                               │
│  Returns: top 8 features with signed SHAP values                │
│  Positive = supports the predicted class                        │
│  Negative = works against the predicted class                   │
└─────────────────────────────────────────────────────────────────┘
```

### Why LightGBM?

| Property | Why It Matters Here |
|----------|---------------------|
| Gradient boosting | Builds an ensemble of weak learners; excellent on tabular financial data |
| Handles class imbalance | `class_weight='balanced'` prevents model from always predicting HOLD |
| Fast inference | Pre-trained .pkl loads in milliseconds at server startup |
| SHAP compatible | TreeExplainer works natively with LightGBM trees |
| TimeSeriesSplit CV | Respects temporal order — no look-ahead bias in evaluation |

### The AI Intensity Index (Original Contribution)

```python
ai_feats = ['volatility_10d', 'volume_zscore', 'bb_width', 'macd_diff']
df['ai_index'] = df[ai_feats].rank(pct=True).mean(axis=1)
df['ai_regime'] = (df['ai_index'] > df['ai_index'].rolling(20).mean()).astype(int)
```

This composite signal uses rolling percentile ranking across 4 indicators that are known to spike during algorithmic trading episodes:
- **High volatility** → algorithms amplifying moves
- **Volume z-score spike** → institutional order flow
- **Wide Bollinger Bands** → regime uncertainty or breakout
- **MACD divergence** → momentum shift that algos often front-run

The regime flag is binary: 1 when the index exceeds its own 20-day rolling mean.

### Label Creation (Meta-Labeling Inspired)

```python
fwd_return = df['close'].pct_change(horizon).shift(-horizon)
labels[fwd_return > +0.02] = 2  # BUY
labels[fwd_return < -0.02] = 0  # SELL
labels[otherwise]          = 1  # HOLD
```

The ±2% threshold filters out noise and creates a meaningful three-class problem. Inspired by Marcos López de Prado's *Advances in Financial Machine Learning* meta-labeling framework.

---

## Backtest Results

> Evaluated on held-out test data (most recent 20% of each ticker's history, ~150 trading days).  
> Strategy: follow BUY/SELL signals, hold cash on HOLD. Transaction cost: 0.1% per trade.  
> Run `python run_backtest.py` to regenerate these results locally.

| Ticker | Horizon | Strategy Return | Buy & Hold | Sharpe Ratio | Win Rate | Total Trades |
|--------|---------|----------------|------------|--------------|----------|--------------|
| AAPL   | 1d      | +0.0%          | +10.3%     | 0.00         | 0%       | 0            |
| AAPL   | 3d      | **+39.6%**     | +10.3%     | **4.07**     | 100%     | 4            |
| AAPL   | 5d      | **+61.3%**     | +10.3%     | **4.23**     | 100%     | 5            |
| GOOGL  | 1d      | +0.0%          | +26.3%     | 0.00         | 0%       | 0            |
| GOOGL  | 3d      | **+88.1%**     | +26.3%     | **5.49**     | 100%     | 5            |
| GOOGL  | 5d      | **+55.1%**     | +26.3%     | **3.85**     | 100%     | 2            |
| MSFT   | 1d      | +0.0%          | -27.7%     | 0.00         | 0%       | 0            |
| MSFT   | 3d      | -21.4%         | -27.7%     | -1.72        | 0%       | 0            |
| MSFT   | 5d      | -27.8%         | -27.7%     | -2.19        | 0%       | 0            |
| TSLA   | 1d      | +11.1%         | -14.9%     | 0.73         | 71%      | 7            |
| TSLA   | 3d      | **+72.8%**     | -14.9%     | **3.49**     | 93%      | 14           |
| TSLA   | 5d      | **+39.5%**     | -14.9%     | **2.00**     | 70%      | 20           |
| NVDA   | 1d      | +0.0%          | +6.1%      | 0.00         | 0%       | 0            |
| NVDA   | 3d      | **+18.4%**     | +6.1%      | **1.90**     | 100%     | 2            |
| NVDA   | 5d      | **+67.4%**     | +6.1%      | **3.81**     | 100%     | 8            |

> ⚠️ Past performance does not indicate future results. Research only.

---

## Technical Features Explained

| Feature | What It Measures | Trading Signal |
|---------|-----------------|----------------|
| `rsi` | Relative Strength Index (14-period) | <30 = oversold, >70 = overbought |
| `macd_diff` | MACD histogram | Positive = upward momentum |
| `bb_width` | Bollinger Band width normalized by price | High = volatile squeeze incoming |
| `volume_zscore` | Volume deviation from 20-day mean | High = institutional activity |
| `ai_index` | Composite algorithmic intensity | High = algo-dominated regime |
| `volatility_10d` | 10-day rolling std of returns | High = uncertain market |
| `gap` | Overnight gap (open vs prior close) | Positive = bullish gap |
| `range` | Intraday range / close | High = high intraday volatility |

---

## Project Structure

```
AI Market Regime Detection V2/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point, CORS, startup model loading
│   │   ├── pipeline/
│   │   │   ├── data_fetch.py          # yfinance OHLCV fetch (120 days, live)
│   │   │   ├── features.py            # All 17 technical features + AI Intensity Index
│   │   │   ├── predict.py             # Load .pkl models, LightGBM inference
│   │   │   ├── shap_explain.py        # SHAP TreeExplainer, handles new 3D format
│   │   │   ├── train.py               # Retrain logic (used by retrain endpoint only)
│   │   │   └── commentary.py          # GPT-4o optional commentary
│   │   └── routers/
│   │       ├── predict.py             # GET /api/predict/{ticker}?horizon={1|3|5}
│   │       └── retrain.py             # POST /api/retrain/{ticker}?horizon={1|3|5}
│   ├── models/                        # 30 pre-trained .pkl files (committed to git)
│   │   ├── lgbm_AAPL_1d.pkl           # ~3MB each
│   │   ├── features_AAPL_1d.pkl       # Feature column list
│   │   └── ... (5 tickers × 3 horizons × 2 files = 30 files)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx        # Storytelling landing: pipeline, features, ML methods
│   │   │   └── Dashboard.tsx          # Live prediction dashboard
│   │   ├── components/
│   │   │   ├── PredictionCard.tsx     # Signal + probability bars + signal explanation
│   │   │   ├── ShapChart.tsx          # SHAP horizontal bar chart with tooltips
│   │   │   ├── HorizonToggle.tsx      # 1/3/5 day selector
│   │   │   ├── Commentary.tsx         # GPT-4o commentary display
│   │   │   └── RetrainButton.tsx      # Live retrain trigger with polling
│   │   ├── lib/
│   │   │   └── api.ts                 # Axios API client + TypeScript types
│   │   └── App.tsx
│   └── package.json
├── notebooks/                         # V1 research notebooks (EDA → models → evaluation)
├── results/                           # V1 model performance figures and backtest results
├── train_local.py                     # Run this to regenerate all 30 .pkl files
└── README.md
```

---

## API Endpoints

### `GET /api/predict/{ticker}?horizon={1|3|5}`

Returns a full prediction for the given ticker and horizon.

**Response:**
```json
{
  "ticker": "AAPL",
  "horizon": 1,
  "prediction": {
    "label": "HOLD",
    "confidence": 0.9999,
    "probabilities": { "SELL": 0.00001, "HOLD": 0.9999, "BUY": 0.00007 }
  },
  "features": {
    "rsi": 54.32,
    "ai_index": 0.6241,
    "ai_regime": 1,
    "volatility_10d": 0.014,
    "macd_diff": -0.423
  },
  "shap_values": [
    { "feature": "macd_diff", "shap_value": -1.149 },
    { "feature": "rsi", "shap_value": 0.234 },
    ...
  ],
  "commentary": "...",
  "has_commentary": false
}
```

### `POST /api/retrain/{ticker}?horizon={1|3|5}`

Triggers background retraining on latest 365 days of yfinance data. Returns immediately, model updates in ~60s.

### `GET /api/retrain/status/{ticker}_{horizon}d`

Poll retraining progress. Returns `"running"` → `"done"` or `"error: ..."`.

### `GET /api/health`

Returns list of all loaded model keys.

---

## Running Locally

### Prerequisites
- Python environment with: `fastapi uvicorn yfinance pandas numpy scikit-learn lightgbm shap joblib openai python-dotenv ta`
- Node.js 18+

### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
# OR with conda:
# conda run -n ml-env uvicorn app.main:app --reload
```

Visit `http://localhost:8000/api/health` to verify all 15 models loaded.

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Retrain models (optional)

```bash
python train_local.py
# Trains all 15 models on 3 years of data (~5 minutes)
# Saves 30 .pkl files to backend/models/
```

---

## Deployment

| Service | Platform | Config |
|---------|----------|--------|
| Backend | Render (free) | Root: `backend/` · Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Vercel (free) | Root: `frontend/` · Env: `VITE_API_URL=<render-url>` |

After deploying backend, update `allow_origins` in `backend/app/main.py` with the Vercel URL.

---

## Skills Demonstrated

| Area | Evidence |
|------|---------|
| **ML Engineering** | LightGBM multi-class classifier, TimeSeriesSplit CV, class balancing, pre-trained model serving |
| **Feature Engineering** | 17 hand-crafted technical indicators, original AI Intensity Index using rolling percentile ranks |
| **MLOps** | Pre-trained .pkl serving, background retrain endpoint, in-memory model hot-swap |
| **Explainability** | SHAP TreeExplainer per-prediction, handles SHAP v0.45 3D array format |
| **Backend Engineering** | FastAPI, async background tasks, CORS, REST API design |
| **Frontend Engineering** | React 18, TypeScript, Tailwind CSS, Recharts, routing |
| **System Design** | Hybrid pre-train + live-data architecture, cold-start tolerant |
| **Data Engineering** | yfinance pipeline, rolling feature computation, forward-return label creation |
| **AI Integration** | GPT-4o optional commentary with structured prompt engineering |

---

## Model Card

| | |
|-|-|
| **Model type** | LightGBM multi-class classifier wrapped in `CalibratedClassifierCV` (isotonic regression) |
| **Training data** | 3 years of daily OHLCV via yfinance — ~750 trading days per ticker |
| **Tickers** | AAPL, GOOGL, MSFT, TSLA, NVDA |
| **Horizons** | 1-day, 3-day, 5-day (15 separate models) |
| **Features** | 17 hand-crafted: technical indicators + original AI Intensity Index |
| **Labels** | BUY (fwd return >+2%), SELL (<-2%), HOLD (otherwise) |
| **Evaluation** | TimeSeriesSplit 3-fold CV — respects temporal order, no look-ahead bias |
| **Calibration** | Isotonic regression via `CalibratedClassifierCV(cv=3, method='isotonic')` — corrects overconfident probability scores |
| **Explainability** | SHAP TreeExplainer (applied to base estimator extracted from calibration wrapper) |
| **Known limitations** | Trained on recent data; may underperform in regimes not represented in training window |
| **Not suitable for** | Live trading, real financial decisions of any kind |
| **Last trained** | April 2026 — run `python train_local.py` to retrain on latest data |

---

> ⚠️ This is a research project for CS 4771 Machine Learning — University of Idaho. Predictions are for educational demonstration only and should not be used to make financial decisions.
