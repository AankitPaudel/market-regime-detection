import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_live_data(ticker: str, days: int = 120) -> pd.DataFrame:
    """Fetch recent OHLCV. 120 days gives enough history for all indicators."""
    end = datetime.today()
    start = end - timedelta(days=days)
    df = yf.download(
        ticker,
        start=start.strftime('%Y-%m-%d'),
        end=end.strftime('%Y-%m-%d'),
        progress=False
    )
    df = df.dropna()
    df.columns = [c.lower() for c in df.columns]
    return df
