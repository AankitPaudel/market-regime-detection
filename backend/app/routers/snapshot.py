"""Lightweight market history for dashboard preview — no ML models required."""

import yfinance as yf
from fastapi import APIRouter, HTTPException

from app.pipeline.market_snapshot import prepare_yf_dataframe, build_market_json

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

    df = prepare_yf_dataframe(raw)
    if 'close' not in df.columns:
        raise HTTPException(status_code=503, detail='Unexpected Yahoo Finance schema')

    try:
        return build_market_json(ticker, df)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
