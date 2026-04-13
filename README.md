# AI-Dominated Market Regime Detection V2

> Predicting equity direction for AAPL, GOOGL, MSFT, TSLA, NVDA using
> LightGBM + meta-labeling gate + AI Intensity Index

🔗 **Live Demo:** *(deploy to Vercel — update URL here)*
📄 **Course:** CS 4771 Machine Learning — University of Idaho
👤 **Author:** Ankit Paudel

---

## What It Does

- Fetches real-time OHLCV data via **yfinance** on every request (no stale cache)
- Computes **17 technical features** + a rolling-rank **AI Intensity Index**
- Runs **pre-trained LightGBM** models — instant response for all recruiters
- Outputs **BUY / SELL / HOLD** with full confidence probability breakdown
- Visualizes **SHAP feature importance** per prediction
- Supports **1 / 3 / 5 day** prediction horizons (3 separate models per ticker)
- Optional **GPT-4o** plain-English commentary on each signal
- Hidden **retrain endpoint** for technical recruiters to trigger live retraining

---

## Architecture

```
yfinance (live OHLCV) → Feature Engineering (17 indicators + AI Index)
                              ↓
                   Pre-trained LightGBM (.pkl)
                              ↓
                    FastAPI REST Backend
                              ↓
               React + TypeScript Dashboard ← Vercel
```

**Hybrid approach:**
- Default path: pre-trained `.pkl` → instant 2-3s response
- Features: always live from yfinance → always feels real-time
- Advanced: retrain button at dashboard bottom → live model update

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| ML Models | LightGBM (15 models: 5 tickers × 3 horizons) |
| Interpretability | SHAP |
| Features | ta, pandas, numpy (17 indicators + AI index) |
| Backend | FastAPI, Python |
| Frontend | React, TypeScript, Tailwind, Recharts |
| Live Data | yfinance (free, no API key needed) |
| AI Commentary | OpenAI GPT-4o (optional) |
| Deploy | Vercel (frontend) + Render (backend) |

---

## ML Skills Demonstrated

| Skill | How |
|-------|-----|
| ML Engineering | LightGBM, XGBoost, scikit-learn, TimeSeriesSplit CV |
| Feature Engineering | 17 technical indicators + PCA-based AI Intensity Index |
| MLOps | Pre-trained models, versioned .pkl files, retrain endpoint |
| Interpretability | SHAP values visualized per prediction |
| Backend Engineering | FastAPI, REST API, async background tasks |
| Frontend Engineering | React + TypeScript + Tailwind + Recharts |
| Deployment | Vercel + Render, free tier |
| System Design | Hybrid pre-train + live data architecture |
| AI Integration | GPT-4o optional commentary |
| Data Engineering | yfinance pipeline, feature computation, label creation |

---

## Folder Structure

```
AI Market Regime Detection V2/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── pipeline/
│   │   │   ├── data_fetch.py          # yfinance live OHLCV fetch
│   │   │   ├── features.py            # 17 technical indicators + AI index
│   │   │   ├── labels.py              # BUY/SELL/HOLD label logic
│   │   │   ├── train.py               # LightGBM training (retrain endpoint)
│   │   │   ├── predict.py             # Load .pkl models, run inference
│   │   │   ├── shap_explain.py        # SHAP value computation
│   │   │   └── commentary.py          # GPT-4o optional commentary
│   │   └── routers/
│   │       ├── predict.py             # GET /api/predict/{ticker}
│   │       └── retrain.py             # POST /api/retrain/{ticker}
│   ├── models/                        # Pre-trained .pkl files (committed to git)
│   │   ├── lgbm_AAPL_1d.pkl
│   │   └── ... (5 tickers × 3 horizons = 15 models)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── components/
│   │   │   ├── HorizonToggle.tsx
│   │   │   ├── PredictionCard.tsx
│   │   │   ├── ShapChart.tsx
│   │   │   ├── Commentary.tsx
│   │   │   └── RetrainButton.tsx
│   │   ├── lib/
│   │   │   └── api.ts
│   │   └── App.tsx
│   └── package.json
├── train_local.py                     # Run this first to generate all .pkl files
└── README.md
```

---

## Getting Started

### Step 1 — Train Models Locally (REQUIRED before deploy)

```bash
pip install yfinance lightgbm scikit-learn ta pandas numpy joblib
python train_local.py
git add backend/models/
git commit -m "Add pre-trained LightGBM models (5 tickers x 3 horizons)"
```

### Step 2 — Run Backend Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Test: curl "http://localhost:8000/api/predict/AAPL?horizon=1"
```

### Step 3 — Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## Deployment

### Backend → Render (free)

1. Push to GitHub
2. render.com → New Web Service → connect repo
3. Root directory: `backend/`
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Env vars: `OPENAI_API_KEY` (optional)

### Frontend → Vercel (free)

1. vercel.com → New Project → import repo
2. Root directory: `frontend/`
3. Env var: `VITE_API_URL` = your Render URL
4. Deploy → update CORS in `backend/app/main.py`

---

> ⚠️ Research project for CS 4771 Machine Learning — University of Idaho. Not financial advice.
