"""Shared Yahoo Finance normalization and 4y-style market summary for API routes."""

from __future__ import annotations

import pandas as pd


def prepare_yf_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance columns to lowercase OHLCV."""
    if raw is None or raw.empty:
        return pd.DataFrame()
    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]
    return df.dropna()


def build_market_json(ticker: str, df: pd.DataFrame, chart_tail: int = 280) -> dict:
    """
    Build the JSON shape used by GET /api/snapshot from a prepared OHLCV frame.
    Expects 'close' column; stats use full close series.
    """
    if df.empty or 'close' not in df.columns:
        raise ValueError('empty_or_no_close')

    s = df['close'].dropna()
    if len(s) < 10:
        raise ValueError('not_enough_history')

    first = float(s.iloc[0])
    last = float(s.iloc[-1])
    total_return_pct = round((last / first - 1) * 100, 2)
    daily_ret = s.pct_change().dropna()
    vol_ann = round(float(daily_ret.std() * (252 ** 0.5) * 100), 2)

    start_d = s.index[0]
    end_d = s.index[-1]
    start_s = start_d.strftime('%Y-%m-%d') if hasattr(start_d, 'strftime') else str(pd.Timestamp(start_d).date())
    end_s = end_d.strftime('%Y-%m-%d') if hasattr(end_d, 'strftime') else str(pd.Timestamp(end_d).date())

    tail = s.tail(chart_tail)
    chart = []
    for ts, val in tail.items():
        ds = ts.strftime('%Y-%m-%d') if hasattr(ts, 'strftime') else str(pd.Timestamp(ts).date())
        chart.append({'d': ds, 'c': round(float(val), 4)})

    return {
        'ticker': ticker.upper(),
        'source': 'Yahoo Finance via yfinance',
        'period_requested': '4y',
        'history_start': start_s,
        'history_end': end_s,
        'trading_days': int(len(s)),
        'last_close': round(last, 4),
        'first_close': round(first, 4),
        'total_return_pct': total_return_pct,
        'annualized_volatility_pct': vol_ann,
        'closes': chart,
    }
