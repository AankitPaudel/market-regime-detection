import pandas as pd
import numpy as np
import ta

FEATURE_COLS = [
    'return_1d', 'return_5d', 'volatility_10d', 'volatility_20d',
    'rsi', 'macd', 'macd_signal', 'macd_diff',
    'bb_upper', 'bb_lower', 'bb_width', 'bb_pct',
    'volume_zscore', 'gap', 'range', 'ai_index', 'ai_regime'
]


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


def get_latest_features(df: pd.DataFrame) -> tuple[dict, list]:
    latest = df[FEATURE_COLS].iloc[-1]
    return latest.to_dict(), FEATURE_COLS
