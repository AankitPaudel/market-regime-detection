from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.pipeline.train import retrain

router = APIRouter()
TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
VALID_HORIZONS = [1, 3, 5]
_retrain_status: dict = {}


@router.post("/retrain/{ticker}")
def retrain_model(ticker: str, horizon: int = 1, background_tasks: BackgroundTasks = None):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(400, "Invalid ticker")
    if horizon not in VALID_HORIZONS:
        raise HTTPException(400, "Horizon must be 1, 3, or 5")

    key = f"{ticker}_{horizon}d"
    _retrain_status[key] = "running"

    def _run():
        try:
            retrain(ticker, horizon)
            _retrain_status[key] = "done"
        except Exception as e:
            _retrain_status[key] = f"error: {str(e)}"

    background_tasks.add_task(_run)
    return {"message": f"Retraining {key} in background. Poll /api/retrain/status/{key}"}


@router.get("/retrain/status/{key}")
def retrain_status(key: str):
    return {"key": key, "status": _retrain_status.get(key, "not started")}
