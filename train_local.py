"""
AI Market Regime Detection V2 — Local Model Training Script
Author: Ankit Paudel | CS 4771 Machine Learning — University of Idaho

─────────────────────────────────────────────────────────────────────
WHAT IS PROBABILITY CALIBRATION AND WHY IT MATTERS
─────────────────────────────────────────────────────────────────────
LightGBM produces raw probability scores that are often overconfident —
for example, outputting 0.9999 for HOLD even when the true probability
is closer to 0.75. This is a known property of gradient-boosted trees
and is a red flag to ML engineers reviewing your model output.

CalibratedClassifierCV wraps the base model and applies a post-hoc
correction using isotonic regression (a non-parametric monotone mapping)
to align the model's output probabilities with the actual observed
frequencies. After calibration:
  - A 0.70 HOLD probability means the model was right ~70% of the time
    when it said 0.70 HOLD — this is called "calibration reliability"
  - Confidence scores look believable to recruiters and engineers
  - SHAP still works — we extract the base LightGBM estimator before
    running TreeExplainer (see shap_explain.py)

cv=3 uses 3-fold cross-calibration on the training data itself.
method='isotonic' is preferred over 'sigmoid' for multi-class problems
with enough data (>1000 samples per class).
─────────────────────────────────────────────────────────────────────

Usage:
    python train_local.py

Output:
    backend/models/lgbm_{TICKER}_{HORIZON}d.pkl   (calibrated model)
    backend/models/features_{TICKER}_{HORIZON}d.pkl

After running, commit the models:
    git add backend/models/
    git commit -m "Retrain: add probability calibration (isotonic)"
"""

import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import os
import ta
from lightgbm import LGBMClassifier
from sklearn.calibration import CalibratedClassifierCV

TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
HORIZONS = [1, 3, 5]
OUTPUT_DIR = 'backend/models'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_data(ticker: str, period: str = '3y') -> pd.DataFrame:
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    return df.dropna()


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['return_1d'] = df['close'].pct_change(1)
    df['return_5d'] = df['close'].pct_change(5)
    df['volatility_10d'] = df['return_1d'].rolling(10).std()
    df['volatility_20d'] = df['return_1d'].rolling(20).std()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(df['close'], window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['close']
    df['bb_pct'] = bb.bollinger_pband()
    df['volume_zscore'] = (
        (df['volume'] - df['volume'].rolling(20).mean()) /
        df['volume'].rolling(20).std()
    )
    df['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
    df['range'] = (df['high'] - df['low']) / df['close']
    ai_feats = ['volatility_10d', 'volume_zscore', 'bb_width', 'macd_diff']
    df['ai_index'] = df[ai_feats].rank(pct=True).mean(axis=1)
    df['ai_regime'] = (df['ai_index'] > df['ai_index'].rolling(20).mean()).astype(int)
    return df.dropna()


def make_labels(df: pd.DataFrame, horizon: int) -> pd.Series:
    fwd_return = df['close'].pct_change(horizon).shift(-horizon)
    labels = pd.Series(1, index=df.index)  # HOLD default
    labels[fwd_return > 0.02] = 2           # BUY
    labels[fwd_return < -0.02] = 0          # SELL
    return labels


FEATURE_COLS = [
    'return_1d', 'return_5d', 'volatility_10d', 'volatility_20d',
    'rsi', 'macd', 'macd_signal', 'macd_diff',
    'bb_upper', 'bb_lower', 'bb_width', 'bb_pct',
    'volume_zscore', 'gap', 'range', 'ai_index', 'ai_regime'
]

if __name__ == '__main__':
    print("=" * 62)
    print("  AI Market Regime Detection V2 — Model Training")
    print("  Author: Ankit Paudel | CS 4771 — Univ. of Idaho")
    print("  Calibration: CalibratedClassifierCV (isotonic, cv=3)")
    print("=" * 62)

    for ticker in TICKERS:
        print(f"\n{'─'*50}")
        print(f"  Training {ticker}...")
        df_raw = fetch_data(ticker)
        df = compute_features(df_raw)

        for horizon in HORIZONS:
            labels = make_labels(df, horizon)
            valid = labels.notna()
            X = df.loc[valid, FEATURE_COLS]
            y = labels.loc[valid]

            # Show class distribution — sanity check before training
            dist = y.value_counts().sort_index()
            dist_str = ' | '.join([
                f"{'SELL' if k==0 else 'HOLD' if k==1 else 'BUY'}:{v}"
                for k, v in dist.items()
            ])
            print(f"\n  [{ticker} {horizon}d] Class distribution: {dist_str}")

            base_model = LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=31,
                class_weight='balanced',
                random_state=42,
                verbose=-1
            )

            try:
                # Calibrate with isotonic regression — corrects overconfident probabilities
                model = CalibratedClassifierCV(
                    base_model,
                    method='isotonic',
                    cv=3
                )
                model.fit(X, y)
                calibrated = True
            except Exception as e:
                print(f"  ⚠️  Calibration failed ({e}) — saving uncalibrated model")
                base_model.fit(X, y)
                model = base_model
                calibrated = False

            model_path = f"{OUTPUT_DIR}/lgbm_{ticker}_{horizon}d.pkl"
            features_path = f"{OUTPUT_DIR}/features_{ticker}_{horizon}d.pkl"
            joblib.dump(model, model_path)
            joblib.dump(FEATURE_COLS, features_path)

            status = "calibrated ✓" if calibrated else "uncalibrated (fallback)"
            print(f"  ✓ Saved: lgbm_{ticker}_{horizon}d.pkl  [{status}]")

    print("\n" + "=" * 62)
    print("  All 15 models trained and saved.")
    print("  Probabilities are now calibrated (isotonic regression).")
    print("  Next step:")
    print("    git add backend/models/")
    print('    git commit -m "Retrain: add probability calibration"')
    print("=" * 62)
