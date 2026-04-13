from fastapi import APIRouter, HTTPException
from app.pipeline.data_fetch import fetch_live_data
from app.pipeline.features import compute_features, get_latest_features
from app.pipeline.predict import predict, MODELS, FEAT_COLS
from app.pipeline.shap_explain import get_shap_values
from app.pipeline.commentary import generate_commentary

router = APIRouter()
TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
VALID_HORIZONS = [1, 3, 5]


@router.get("/predict/{ticker}")
def predict_ticker(ticker: str, horizon: int = 1):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(400, f"Ticker must be one of {TICKERS}")
    if horizon not in VALID_HORIZONS:
        raise HTTPException(400, "Horizon must be 1, 3, or 5")

    key = f"{ticker}_{horizon}d"
    if key not in MODELS:
        raise HTTPException(503, f"Model not loaded for {key}. Run train_local.py first.")

    df_raw = fetch_live_data(ticker, days=120)
    df = compute_features(df_raw)
    features, feature_cols = get_latest_features(df)

    prediction = predict(ticker, horizon, features)
    shap_values = get_shap_values(MODELS[key], features, feature_cols)

    top_feature = shap_values[0]['feature'] if shap_values else 'unknown'
    commentary = generate_commentary(
        ticker=ticker,
        label=prediction['label'],
        confidence=prediction['confidence'],
        horizon=horizon,
        ai_regime=int(features.get('ai_regime', 0)),
        rsi=float(features.get('rsi', 50)),
        top_feature=top_feature
    )

    return {
        "ticker": ticker,
        "horizon": horizon,
        "prediction": prediction,
        "features": {
            "rsi": round(features.get('rsi', 0), 2),
            "ai_index": round(features.get('ai_index', 0), 4),
            "ai_regime": int(features.get('ai_regime', 0)),
            "volatility_10d": round(features.get('volatility_10d', 0), 6),
            "macd_diff": round(features.get('macd_diff', 0), 4),
        },
        "shap_values": shap_values,
        "commentary": commentary,
        "has_commentary": bool(commentary)
    }


@router.get("/health")
def health():
    return {"status": "ok", "models_loaded": list(MODELS.keys())}
