#!/usr/bin/env python3
"""
Export ~4y Yahoo Finance closes + summary per ticker for the offline dashboard.

Run from repo root when you want fresher cached prices:
  python scripts/export_dashboard_cache.py

Writes frontend/src/data/cache/{TICKER}.json (same shape as GET /api/snapshot).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BACKEND = os.path.join(ROOT, 'backend')
sys.path.insert(0, BACKEND)

import yfinance as yf  # noqa: E402
from app.pipeline.market_snapshot import prepare_yf_dataframe, build_market_json  # noqa: E402

TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
OUT_DIR = os.path.join(ROOT, 'frontend', 'src', 'data', 'cache')


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    when = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for t in TICKERS:
        raw = yf.download(t, period='4y', progress=False, auto_adjust=True)
        df = prepare_yf_dataframe(raw)
        if df.empty or 'close' not in df.columns:
            print(f'SKIP {t}: no data')
            continue
        payload = build_market_json(t, df)
        payload['source'] = f'Yahoo Finance via yfinance — static export ({when} UTC)'
        path = os.path.join(OUT_DIR, f'{t}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
        print(f'Wrote {path} trading_days={payload["trading_days"]}')


if __name__ == '__main__':
    main()
