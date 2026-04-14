"""
Single-call dashboard payload: ~4y market summary plus ML-shaped preview
(features + LightGBM + SHAP) from the latest row of that history — same
pipeline as /predict, without optional enrichments or GPT commentary.
"""

from fastapi import APIRouter, HTTPException, Query
import yfinance as yf

from app.pipeline.market_snapshot import prepare_yf_dataframe, build_market_json
from app.pipeline.features import compute_features, get_latest_features
from app.pipeline.predict import predict, MODELS, FEAT_COLS
from app.pipeline.shap_explain import get_shap_values

router = APIRouter()
TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
VALID_HORIZONS = [1, 3, 5]


@router.get('/dashboard-preview/{ticker}')
def dashboard_preview(ticker: str, horizon: int = Query(1, description='Must be 1, 3, or 5')):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=400, detail=f'Ticker must be one of {TICKERS}')
    if horizon not in VALID_HORIZONS:
        raise HTTPException(status_code=400, detail='Horizon must be 1, 3, or 5')

    try:
        raw = yf.download(ticker, period='4y', progress=False, auto_adjust=True)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f'yfinance error: {e}') from e

    if raw is None or raw.empty:
        raise HTTPException(status_code=503, detail='No price data returned for this ticker')

    df = prepare_yf_dataframe(raw)
    required = {'open', 'high', 'low', 'close', 'volume'}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=503, detail='Unexpected Yahoo Finance schema (need OHLCV)')

    try:
        market = build_market_json(ticker, df)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    market['horizon_requested'] = horizon

    key = f'{ticker}_{horizon}d'
    ml_preview = None
    ml_preview_error = None

    if key not in MODELS:
        ml_preview_error = f'Model not loaded for {key} (train and deploy models/). Market summary is still valid.'
    else:
        try:
            df_feat = compute_features(df)
        except Exception as e:
            ml_preview_error = f'Feature build failed: {e}'
            return {**market, 'ml_preview': None, 'ml_preview_error': ml_preview_error}

        if len(df_feat) < 5:
            ml_preview_error = 'Not enough rows after feature engineering'
            return {**market, 'ml_preview': None, 'ml_preview_error': ml_preview_error}

        features, feature_cols = get_latest_features(df_feat)
        pred = predict(ticker, horizon, features)
        if 'error' in pred:
            ml_preview_error = pred['error']
        else:
            shap_values = get_shap_values(MODELS[key], features, FEAT_COLS[key])
            top_feature = shap_values[0]['feature'] if shap_values else 'unknown'
            ml_preview = {
                'ticker': ticker,
                'horizon': horizon,
                'prediction': pred,
                'features': {
                    'rsi': round(features.get('rsi', 0), 2),
                    'ai_index': round(features.get('ai_index', 0), 4),
                    'ai_regime': int(features.get('ai_regime', 0)),
                    'volatility_10d': round(features.get('volatility_10d', 0), 6),
                    'macd_diff': round(features.get('macd_diff', 0), 4),
                },
                'shap_values': shap_values,
                'commentary': (
                    f'Latest bar from ~4y Yahoo history. Strongest SHAP driver: {top_feature}. '
                    'Use Predict for a fresh live pull (optional news / Reddit / analyst cards if configured).'
                ),
                'has_commentary': True,
                'enrichments': {'news': None, 'reddit': None, 'alpha_vantage': None},
                'preview_mode': True,
                'preview_note': (
                    'Same 17-feature pipeline and LightGBM + SHAP as Predict, evaluated on the most recent '
                    'trading day in the downloaded ~4y window (not a second live yfinance call).'
                ),
            }

    return {**market, 'ml_preview': ml_preview, 'ml_preview_error': ml_preview_error}
