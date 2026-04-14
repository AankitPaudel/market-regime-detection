/**
 * Bundled sample dashboard (~4y-shaped chart + ML-shaped cards) so the UI
 * renders on static hosts when the API is missing, cold, or slow.
 * Replaced automatically when /api/dashboard-preview succeeds.
 */
import type { DashboardPreview, Prediction } from '../lib/api'

function mulberry32(a: number) {
  return () => {
    let t = (a += 0x6d2b79f5)
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function synthCloses(seed: number, endClose: number, n = 280): { d: string; c: number }[] {
  const rand = mulberry32(seed)
  const out: { d: string; c: number }[] = []
  let p = endClose * 0.62
  const end = new Date(Date.UTC(2026, 3, 13))
  for (let i = 0; out.length < n && i < 500; i++) {
    const d = new Date(end)
    d.setUTCDate(d.getUTCDate() - i)
    const wd = d.getUTCDay()
    if (wd === 0 || wd === 6) continue
    p *= 1 + (rand() - 0.48) * 0.014 + Math.sin(out.length / 22) * 0.0045
    out.push({ d: d.toISOString().slice(0, 10), c: Math.round(p * 100) / 100 })
  }
  out.reverse()
  if (out.length > 0) {
    const fac = endClose / out[out.length - 1].c
    out.forEach((row) => {
      row.c = Math.round(row.c * fac * 10000) / 10000
    })
    out[out.length - 1].c = endClose
  }
  return out
}

const TICKER_LAST: Record<string, number> = {
  AAPL: 259.2,
  GOOGL: 165.4,
  MSFT: 395.2,
  TSLA: 248.6,
  NVDA: 892.1,
}

function horizonProbs(h: number): Prediction['prediction'] {
  if (h >= 5) {
    return {
      label: 'HOLD',
      confidence: 0.74,
      probabilities: { BUY: 0.13, HOLD: 0.74, SELL: 0.13 },
    }
  }
  if (h >= 3) {
    return {
      label: 'HOLD',
      confidence: 0.79,
      probabilities: { BUY: 0.11, HOLD: 0.79, SELL: 0.1 },
    }
  }
  return {
    label: 'HOLD',
    confidence: 0.862,
    probabilities: { BUY: 0.071, HOLD: 0.862, SELL: 0.067 },
  }
}

function shapFor(ticker: string, h: number) {
  const s = ticker.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + h * 17
  const r = mulberry32(s)
  const base = [
    { feature: 'bb_lower', shap_value: -0.423 },
    { feature: 'macd_diff', shap_value: 0.077 },
    { feature: 'volatility_10d', shap_value: 0.152 },
    { feature: 'volatility_20d', shap_value: 0.118 },
    { feature: 'rsi', shap_value: 0.091 },
    { feature: 'bb_pct', shap_value: 0.062 },
    { feature: 'bb_width', shap_value: 0.041 },
    { feature: 'bb_upper', shap_value: 0.019 },
  ]
  return base.map((row) => ({
    ...row,
    shap_value: Math.round((row.shap_value + (r() - 0.5) * 0.04) * 10000) / 10000,
  }))
}

export function getOfflineDashboardPreview(ticker: string, horizon: number): DashboardPreview {
  const t = ticker.toUpperCase()
  const last = TICKER_LAST[t] ?? TICKER_LAST.AAPL
  const h = horizon === 3 || horizon === 5 ? horizon : 1
  const seed = t.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + h * 31
  const closes = synthCloses(seed, last)
  const firstClose = closes[0]?.c ?? last * 0.62
  const dailyRet = closes.slice(1).map((row, i) => (row.c - closes[i].c) / closes[i].c)
  const vol = dailyRet.length
    ? Math.round(Math.sqrt(dailyRet.reduce((a, x) => a + x * x, 0) / dailyRet.length) * Math.sqrt(252) * 10000) / 100
    : 28
  const pred = horizonProbs(h)
  const rsi = Math.round((48 + (seed % 17) + h) * 100) / 100
  const ml: Prediction & { preview_mode?: boolean; preview_note?: string; demo_data?: boolean } = {
    ticker: t,
    horizon: h,
    prediction: pred,
    features: {
      rsi,
      ai_index: Math.min(0.95, Math.round((0.45 + (seed % 10) / 100 + h * 0.008) * 10000) / 10000),
      ai_regime: 1,
      volatility_10d: Math.round(0.012 + (seed % 7) / 1000 + h * 0.0008),
      macd_diff: Math.round((1.1 + (seed % 20) / 50 + h * 0.05) * 10000) / 10000,
    },
    shap_values: shapFor(t, h),
    commentary:
      'Bundled sample narrative for layout. Connect the live API for Yahoo prices, model output, and optional enrichments.',
    has_commentary: true,
    enrichments: { news: null, reddit: null, alpha_vantage: null },
    preview_mode: true,
    preview_note:
      'Illustrative values only. When the backend is available, this panel is replaced by the same pipeline on live ~4y data.',
    demo_data: true,
  }

  return {
    ticker: t,
    source: 'Bundled sample (offline)',
    period_requested: '4y',
    history_start: '2022-04-14',
    history_end: '2026-04-13',
    trading_days: 1001,
    last_close: last,
    first_close: Math.round(firstClose * 100) / 100,
    total_return_pct: Math.round(((last / firstClose - 1) * 100) * 100) / 100,
    annualized_volatility_pct: vol,
    closes,
    horizon_requested: h,
    ml_preview: ml,
    ml_preview_error: null,
  }
}
