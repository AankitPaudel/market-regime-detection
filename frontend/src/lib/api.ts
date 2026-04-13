import axios from 'axios'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, ''),
  timeout: 120_000,
})

export interface Prediction {
  ticker: string
  horizon: number
  prediction: {
    label: 'BUY' | 'SELL' | 'HOLD'
    confidence: number
    probabilities: { BUY: number; SELL: number; HOLD: number }
  }
  features: {
    rsi: number
    ai_index: number
    ai_regime: number
    volatility_10d: number
    macd_diff: number
  }
  shap_values: { feature: string; shap_value: number }[]
  commentary: string
  has_commentary: boolean
  enrichments: {
    news: {
      score: number
      headline_count: number
      sample_headline: string
    } | null
    reddit: {
      mention_count: number
      sentiment_score: number
      top_post_title: string
    } | null
    alpha_vantage: {
      next_earnings: string
      analyst_target: number | null
      analyst_rating: string
    } | null
  }
}

export interface MarketSnapshot {
  ticker: string
  source: string
  period_requested: string
  history_start: string
  history_end: string
  trading_days: number
  last_close: number
  first_close: number
  total_return_pct: number
  annualized_volatility_pct: number
  closes: { d: string; c: number }[]
}

export const fetchMarketSnapshot = async (ticker: string, signal?: AbortSignal): Promise<MarketSnapshot> => {
  const res = await api.get(`/api/snapshot/${ticker}`, { signal, timeout: 60_000 })
  return res.data
}

/** One request: 4y market summary + optional ML preview (same shape as Prediction). */
export interface DashboardPreview extends MarketSnapshot {
  horizon_requested: number
  ml_preview: (Prediction & { preview_mode?: boolean; preview_note?: string }) | null
  ml_preview_error: string | null
}

export const fetchDashboardPreview = async (
  ticker: string,
  horizon: number,
  signal?: AbortSignal,
): Promise<DashboardPreview> => {
  const res = await api.get(`/api/dashboard-preview/${ticker}`, {
    params: { horizon },
    signal,
    timeout: 90_000,
  })
  return res.data
}

export const fetchPrediction = async (
  ticker: string,
  horizon: number,
  signal?: AbortSignal,
): Promise<Prediction> => {
  const res = await api.get(`/api/predict/${ticker}`, {
    params: { horizon },
    signal,
  })
  return res.data
}

export const triggerRetrain = async (ticker: string, horizon: number) => {
  const res = await api.post(`/api/retrain/${ticker}`, null, { params: { horizon } })
  return res.data
}

export const getRetrainStatus = async (key: string) => {
  const res = await api.get(`/api/retrain/status/${key}`)
  return res.data
}
