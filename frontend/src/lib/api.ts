import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
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

export const fetchPrediction = async (ticker: string, horizon: number): Promise<Prediction> => {
  const res = await api.get(`/api/predict/${ticker}`, { params: { horizon } })
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
