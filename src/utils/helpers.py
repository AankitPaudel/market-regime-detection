"""Helper functions"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List

from .config import MARKET_TIMEZONE

def create_forward_returns(prices: pd.DataFrame, horizons: List[int], price_col: str = 'Close') -> pd.DataFrame:
    returns_df = prices[[price_col]].copy()
    for h in horizons:
        future_price = returns_df[price_col].shift(-h)
        returns_df[f'return_{h}d'] = (future_price - returns_df[price_col]) / returns_df[price_col]
    return returns_df

def create_labels(returns: pd.Series, buy_threshold: float = 0.02, sell_threshold: float = -0.02) -> pd.Series:
    labels = pd.Series(0, index=returns.index)
    labels[returns > buy_threshold] = 1  # BUY
    labels[returns < sell_threshold] = -1  # SELL
    return labels

def save_dataframe(df: pd.DataFrame, filepath: Path, format: str = 'parquet') -> None:
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'parquet':
        df.to_parquet(filepath)
    elif format == 'csv':
        df.to_csv(filepath)
    else:
        df.to_pickle(filepath)
    
    print(f"Saved to {filepath}")

def load_dataframe(filepath: Path, format: str = None) -> pd.DataFrame:
    filepath = Path(filepath)
    if format is None:
        format = filepath.suffix[1:]
    
    if format == 'parquet':
        return pd.read_parquet(filepath)
    elif format == 'csv':
        return pd.read_csv(filepath, index_col=0, parse_dates=True)
    else:
        return pd.read_pickle(filepath)

def print_class_distribution(labels: pd.Series, name: str = "Labels") -> None:
    counts = labels.value_counts().sort_index()
    proportions = labels.value_counts(normalize=True).sort_index()
    
    print(f"\n{name} Distribution:")
    print("-" * 40)
    for label in counts.index:
        label_name = {1: 'BUY', 0: 'HOLD', -1: 'SELL'}.get(label, label)
        print(f"{label_name:8s}: {counts[label]:6d} ({proportions[label]:6.2%})")
    print("-" * 40)