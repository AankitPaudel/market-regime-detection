"""Technical indicators"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import get_config, RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.helpers import save_dataframe, load_dataframe

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['Close'].ewm(span=fast).mean()
    ema_slow = df['Close'].ewm(span=slow).mean()
    df['macd'] = ema_fast - ema_slow
    df['macd_signal'] = df['macd'].ewm(span=signal).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    return df

def calculate_bollinger(df, period=20, std=2):
    df['bb_middle'] = df['Close'].rolling(period).mean()
    bb_std = df['Close'].rolling(period).std()
    df['bb_upper'] = df['bb_middle'] + (std * bb_std)
    df['bb_lower'] = df['bb_middle'] - (std * bb_std)
    df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    return df

def calculate_volume_features(df, lookback=20):
    vol_mean = df['Volume'].rolling(lookback).mean()
    vol_std = df['Volume'].rolling(lookback).std()
    df['volume_zscore'] = (df['Volume'] - vol_mean) / vol_std
    return df

def create_technical_features(prices_df, config):
    all_features = []
    
    for ticker in prices_df['Ticker'].unique():
        print(f"Processing {ticker}...")
        
        df = prices_df[prices_df['Ticker'] == ticker].copy().sort_values('Date')
        
        # Returns
        for p in [1, 3, 5, 10]:
            df[f'return_{p}d'] = df['Close'].pct_change(p)
        
        # Volatility
        df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
        for w in [10, 20]:
            df[f'volatility_{w}d'] = df['log_return'].rolling(w).std() * np.sqrt(252)
        df = df.drop('log_return', axis=1)
        
        # Technical indicators
        df = calculate_rsi(df, config.rsi_period)
        df = calculate_macd(df, config.macd_fast, config.macd_slow, config.macd_signal)
        df = calculate_bollinger(df, config.bollinger_period, config.bollinger_std)
        df = calculate_volume_features(df, config.volume_lookback)
        
        # Gap
        df['gap_pct'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)
        
        # Range
        df['range_pct'] = (df['High'] - df['Low']) / df['Close']
        
        all_features.append(df)
        print(f"  Created {len(df.columns)-7} features")
    
    return pd.concat(all_features, ignore_index=True).sort_values(['Date', 'Ticker'])

def main():
    print("="*60)
    print("TECHNICAL FEATURES")
    print("="*60)
    
    config = get_config()
    
    prices_file = RAW_DATA_DIR / "prices" / "all_tickers.parquet"
    prices_df = load_dataframe(prices_file)
    
    features_df = create_technical_features(prices_df, config)
    
    output = PROCESSED_DATA_DIR / "technical_features.parquet"
    save_dataframe(features_df, output)
    
    print("\n✓ COMPLETE")
    print(f"Features: {len(features_df.columns)}")

if __name__ == "__main__":
    main()