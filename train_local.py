"""
AI Market Regime Detection V2 — Local Model Training Script
Author: Ankit Paudel | CS 4771 Machine Learning — University of Idaho

Run this script locally BEFORE deploying to train all 15 LightGBM models
(5 tickers × 3 horizons) and save them as .pkl files.

Usage:
    pip install yfinance lightgbm scikit-learn ta pandas numpy joblib
    python train_local.py

Output:
    backend/models/lgbm_{TICKER}_{HORIZON}d.pkl
    backend/models/features_{TICKER}_{HORIZON}d.pkl

After running, commit the models:
    git add backend/models/
    git commit -m "Add pre-trained LightGBM models (5 tickers x 3 horizons)"
"""

import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import os
import ta
from lightgbm import LGBMClassifier

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
    labels[fwd_return > 0.02] = 2          # BUY
    labels[fwd_return < -0.02] = 0         # SELL
    return labels


FEATURE_COLS = [
    'return_1d', 'return_5d', 'volatility_10d', 'volatility_20d',
    'rsi', 'macd', 'macd_signal', 'macd_diff',
    'bb_upper', 'bb_lower', 'bb_width', 'bb_pct',
    'volume_zscore', 'gap', 'range', 'ai_index', 'ai_regime'
]

if __name__ == '__main__':
    print("=" * 55)
    print("  AI Market Regime Detection V2 — Model Training")
    print("  Author: Ankit Paudel | CS 4771 — Univ. of Idaho")
    print("=" * 55)

    for ticker in TICKERS:
        print(f"\nTraining {ticker}...")
        df_raw = fetch_data(ticker)
        df = compute_features(df_raw)

        for horizon in HORIZONS:
            labels = make_labels(df, horizon)
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

            model_path = f"{OUTPUT_DIR}/lgbm_{ticker}_{horizon}d.pkl"
            features_path = f"{OUTPUT_DIR}/features_{ticker}_{horizon}d.pkl"
            joblib.dump(model, model_path)
            joblib.dump(FEATURE_COLS, features_path)
            print(f"  ✓ Saved: lgbm_{ticker}_{horizon}d.pkl")

    print("\n" + "=" * 55)
    print("  All 15 models trained and saved.")
    print("  Next step:")
    print("    git add backend/models/")
    print('    git commit -m "Add pre-trained LightGBM models"')
    print("=" * 55)
