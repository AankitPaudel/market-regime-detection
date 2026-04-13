import joblib
import numpy as np
import pandas as pd
import os

TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
HORIZONS = [1, 3, 5]
LABEL_MAP = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
MODELS: dict = {}
FEAT_COLS: dict = {}


def load_models():
    models_dir = os.path.join(os.path.dirname(__file__), '../../models')
    for ticker in TICKERS:
        for h in HORIZONS:
            key = f"{ticker}_{h}d"
            mp = os.path.join(models_dir, f"lgbm_{key}.pkl")
            fp = os.path.join(models_dir, f"features_{key}.pkl")
            if os.path.exists(mp):
                MODELS[key] = joblib.load(mp)
                FEAT_COLS[key] = joblib.load(fp)
                print(f"Loaded: {key}")
            else:
                print(f"WARNING: missing model for {key}")


def predict(ticker: str, horizon: int, features: dict) -> dict:
    key = f"{ticker}_{horizon}d"
    if key not in MODELS:
        return {"error": f"Model not loaded for {key}"}

    model = MODELS[key]
    feat_cols = FEAT_COLS[key]
    X = pd.DataFrame([features])[feat_cols]

    proba = model.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    label = LABEL_MAP[pred_idx]

    return {
        "label": label,
        "confidence": float(proba[pred_idx]),
        "probabilities": {
            "SELL": float(proba[0]),
            "HOLD": float(proba[1]),
            "BUY": float(proba[2])
        }
    }
