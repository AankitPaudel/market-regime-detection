"""Lightweight market history for dashboard preview — no ML models required."""

import yfinance as yf
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()
TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']


@router.get('/snapshot/{ticker}')
def market_snapshot(ticker: str):
    """
    ~4 years of daily closes from Yahoo Finance (yfinance).
    Used by the frontend preview so recruiters see real data before running Predict.
    """
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=400, detail=f'Ticker must be one of {TICKERS}')

    try:
        raw = yf.download(ticker, period='4y', progress=False, auto_adjust=True)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f'yfinance error: {e}') from e

    if raw is None or raw.empty:
        raise HTTPException(status_code=503, detail='No price data returned for this ticker')

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    raw.columns = [str(c).lower() for c in raw.columns]
    if 'close' not in raw.columns:
        raise HTTPException(status_code=503, detail='Unexpected Yahoo Finance schema')

    s = raw['close'].dropna()
    if len(s) < 10:
        raise HTTPException(status_code=503, detail='Not enough history')

    first = float(s.iloc[0])
    last = float(s.iloc[-1])
    total_return_pct = round((last / first - 1) * 100, 2)
    daily_ret = s.pct_change().dropna()
    vol_ann = round(float(daily_ret.std() * (252 ** 0.5) * 100), 2)

    start_d = s.index[0]
    end_d = s.index[-1]
    if hasattr(start_d, 'strftime'):
        start_s = start_d.strftime('%Y-%m-%d')
    else:
        start_s = str(pd.Timestamp(start_d).date())
    if hasattr(end_d, 'strftime'):
        end_s = end_d.strftime('%Y-%m-%d')
    else:
        end_s = str(pd.Timestamp(end_d).date())

    tail = s.tail(280)
    chart = []
    for ts, val in tail.items():
        if hasattr(ts, 'strftime'):
            ds = ts.strftime('%Y-%m-%d')
        else:
            ds = str(pd.Timestamp(ts).date())
        chart.append({'d': ds, 'c': round(float(val), 4)})

    return {
        'ticker': ticker,
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
