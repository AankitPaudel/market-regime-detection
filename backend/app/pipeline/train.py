"""
Used ONLY by the /api/retrain endpoint (optional advanced feature).
Retrains a single ticker+horizon model live using yfinance data.
"""
import joblib
import os
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from app.pipeline.data_fetch import fetch_live_data
from app.pipeline.features import compute_features, FEATURE_COLS
from app.pipeline.predict import MODELS, FEAT_COLS


def retrain(ticker: str, horizon: int):
    df_raw = fetch_live_data(ticker, days=365)
    df = compute_features(df_raw)

    fwd_return = df['close'].pct_change(horizon).shift(-horizon)
    labels = pd.Series(1, index=df.index)
    labels[fwd_return > 0.02] = 2
    labels[fwd_return < -0.02] = 0

    valid = labels.notna()
    X = df.loc[valid, FEATURE_COLS]
    y = labels.loc[valid]

    model = LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        class_weight='balanced',
        random_state=42,
        verbose=-1
    )
    model.fit(X, y)

    key = f"{ticker}_{horizon}d"
    models_dir = os.path.join(os.path.dirname(__file__), '../../models')
    joblib.dump(model, f"{models_dir}/lgbm_{key}.pkl")
    joblib.dump(FEATURE_COLS, f"{models_dir}/features_{key}.pkl")

    MODELS[key] = model
    FEAT_COLS[key] = FEATURE_COLS

    return {"status": "retrained", "ticker": ticker, "horizon": horizon}
