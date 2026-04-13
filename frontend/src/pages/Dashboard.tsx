import { useState, useRef } from 'react'
import { fetchPrediction } from '../lib/api'
import type { Prediction } from '../lib/api'
import HorizonToggle from '../components/HorizonToggle'
import PredictionCard from '../components/PredictionCard'
import ShapChart from '../components/ShapChart'
import Commentary from '../components/Commentary'
import RetrainButton from '../components/RetrainButton'
import EnrichmentPanel from '../components/EnrichmentPanel'
import toast from 'react-hot-toast'

const TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']

const TICKER_NAMES: Record<string, string> = {
  AAPL: 'Apple Inc.',
  GOOGL: 'Alphabet Inc.',
  MSFT: 'Microsoft Corp.',
  TSLA: 'Tesla Inc.',
  NVDA: 'NVIDIA Corp.',
}

export default function Dashboard() {
  const [ticker, setTicker] = useState('AAPL')
  const [horizon, setHorizon] = useState(1)
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadTime, setLoadTime] = useState<number | null>(null)
  const predictSeq = useRef(0)
  const abortRef = useRef<AbortController | null>(null)

  const handlePredict = async (t = ticker, h = horizon) => {
    abortRef.current?.abort()
    const ac = new AbortController()
    abortRef.current = ac
    const seq = ++predictSeq.current

    setLoading(true)
    setPrediction(null)
    setLoadTime(null)
    const start = Date.now()
    try {
      const data = await fetchPrediction(t, h, ac.signal)
      if (seq !== predictSeq.current) return
      setLoadTime(Date.now() - start)
      setPrediction(data)
      toast.dismiss()
    } catch (e: unknown) {
      if (seq !== predictSeq.current) return
      if (ac.signal.aborted) return
      const err = e as { code?: string; message?: string }
      if (err?.code === 'ERR_CANCELED') return
      console.error(e)
      toast.error(
        'Prediction failed — Render free tier can take 60s on first request after sleep. Check VITE_API_URL in Vercel env matches your backend URL, then try again.',
        { duration: 8000 },
      )
    } finally {
      if (seq === predictSeq.current) setLoading(false)
    }
  }

  const handleTickerChange = (t: string) => {
    setTicker(t)
    handlePredict(t, horizon)
  }

  const handleHorizonChange = (h: number) => {
    setHorizon(h)
    if (prediction) handlePredict(ticker, h)
  }

  const labelColor = prediction?.prediction.label === 'BUY'
    ? '#22c55e' : prediction?.prediction.label === 'SELL'
    ? '#ef4444' : '#eab308'

  return (
    <div style={{ minHeight: '100vh', background: '#05050f', color: '#e5e7eb' }}>

      {/* ── TOPBAR ── */}
      <div style={{ borderBottom: '1px solid #111122', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#080812' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <a href="/" style={{ fontSize: 13, color: '#4b5563', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6 }}>
            ← Back
          </a>
          <div style={{ width: 1, height: 20, background: '#1f2937' }} />
          <img src="/favicon.png" alt="logo" style={{ width: 28, height: 28, borderRadius: 8, objectFit: 'cover' }} />
          <div>
            <p style={{ fontWeight: 800, fontSize: 15, margin: 0 }}>Market Regime Dashboard</p>
            <p style={{ fontSize: 11, color: '#4b5563', margin: 0 }}>AI Market Regime Detection V2 · Ankit Paudel</p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
          <span style={{ fontSize: 11, color: '#4b5563' }}>Live · yfinance</span>
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '32px 24px' }}>

        {/* ── CONTROLS ── */}
        <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 20, padding: '24px 28px', marginBottom: 24 }}>
          <p style={{ fontSize: 11, color: '#4b5563', fontWeight: 700, letterSpacing: '0.1em', marginBottom: 16 }}>SELECT TICKER</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
            {TICKERS.map((t) => (
              <button
                key={t}
                onClick={() => handleTickerChange(t)}
                style={{
                  padding: '10px 20px', borderRadius: 10, border: ticker === t ? 'none' : '1px solid #1f2937',
                  background: ticker === t ? 'linear-gradient(135deg,#3b82f6,#6366f1)' : '#070710',
                  color: ticker === t ? '#fff' : '#6b7280', fontFamily: 'monospace', fontWeight: 700,
                  fontSize: 14, cursor: 'pointer',
                  boxShadow: ticker === t ? '0 0 20px rgba(99,102,241,0.25)' : 'none',
                }}
              >
                <div>{t}</div>
                <div style={{ fontSize: 10, fontFamily: 'system-ui', fontWeight: 400, opacity: 0.7, marginTop: 2 }}>{TICKER_NAMES[t].split(' ')[0]}</div>
              </button>
            ))}
          </div>

          <p style={{ fontSize: 11, color: '#4b5563', fontWeight: 700, letterSpacing: '0.1em', marginBottom: 12 }}>PREDICTION HORIZON</p>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
            <HorizonToggle value={horizon} onChange={handleHorizonChange} />
            <button
              onClick={() => handlePredict()}
              disabled={loading}
              style={{
                padding: '12px 28px', borderRadius: 12, border: 'none',
                background: loading ? '#1f2937' : 'linear-gradient(135deg,#3b82f6,#6366f1)',
                color: loading ? '#4b5563' : '#fff', fontWeight: 700, fontSize: 14,
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: loading ? 'none' : '0 0 30px rgba(99,102,241,0.25)',
              }}
            >
              {loading ? '⏳ Fetching live data...' : `▶ Predict ${ticker} · ${horizon}d`}
            </button>
          </div>

          {loadTime && (
            <p style={{ fontSize: 11, color: '#374151', marginTop: 12 }}>
              ✓ Completed in {(loadTime / 1000).toFixed(1)}s — live yfinance + LightGBM + SHAP
            </p>
          )}
          {!prediction && !loading && (
            <p style={{ fontSize: 11, color: '#374151', marginTop: 8 }}>
              First request may take ~30s on Render free tier cold starts
            </p>
          )}
        </div>

        {/* ── LOADING STATE ── */}
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '80px 24px', gap: 20 }}>
            <div style={{
              width: 48, height: 48, borderRadius: '50%',
              border: '4px solid #1f2937', borderTopColor: '#3b82f6',
              animation: 'spin 1s linear infinite',
            }} />
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: '#9ca3af', marginBottom: 8 }}>Running the full pipeline for <strong>{ticker}</strong> ({horizon}d)</p>
              <div style={{ display: 'flex', gap: 24, justifyContent: 'center' }}>
                {['Fetching yfinance', 'Computing 17 features', 'Running LightGBM', 'Computing SHAP'].map((s, i) => (
                  <span key={i} style={{ fontSize: 11, color: '#374151' }}>{s}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── RESULTS ── */}
        {prediction && !loading && (
          <>
            {/* Signal banner */}
            <div style={{ background: `${labelColor}10`, border: `1px solid ${labelColor}30`, borderRadius: 16, padding: '16px 24px', marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ fontSize: 32, fontWeight: 900, color: labelColor, fontFamily: 'monospace' }}>
                  {prediction.prediction.label}
                </span>
                <div>
                  <p style={{ fontWeight: 700, fontSize: 16 }}>
                    {TICKER_NAMES[prediction.ticker]} · {prediction.horizon}-day signal
                  </p>
                  <p style={{ fontSize: 13, color: '#6b7280' }}>
                    {(prediction.prediction.confidence * 100).toFixed(1)}% model confidence ·{' '}
                    {prediction.features.ai_regime === 1 ? '⚡ High AI regime' : '— Low AI regime'}
                  </p>
                </div>
              </div>
              <div style={{ fontSize: 12, color: '#4b5563', textAlign: 'right' }}>
                <p>Model: LightGBM (lgbm_{prediction.ticker}_{prediction.horizon}d)</p>
                <p>Features: 17 technical indicators</p>
              </div>
            </div>

            {/* Main grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <PredictionCard prediction={prediction} />
              <ShapChart shapValues={prediction.shap_values} />
            </div>

            {/* Feature stats row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginBottom: prediction.has_commentary ? 16 : 0 }}>
              {[
                { label: 'RSI (14)', value: prediction.features.rsi.toString(), desc: prediction.features.rsi < 30 ? 'Oversold zone' : prediction.features.rsi > 70 ? 'Overbought zone' : 'Neutral range', color: prediction.features.rsi < 30 ? '#22c55e' : prediction.features.rsi > 70 ? '#ef4444' : '#9ca3af' },
                { label: 'AI Intensity', value: `${(prediction.features.ai_index * 100).toFixed(1)}%`, desc: prediction.features.ai_regime === 1 ? '⚡ High algo regime' : '— Low algo regime', color: prediction.features.ai_regime === 1 ? '#8b5cf6' : '#4b5563' },
                { label: '10d Volatility', value: `${(prediction.features.volatility_10d * 100).toFixed(2)}%`, desc: prediction.features.volatility_10d > 0.02 ? 'Elevated volatility' : 'Calm market', color: prediction.features.volatility_10d > 0.02 ? '#f59e0b' : '#9ca3af' },
                { label: 'MACD Diff', value: prediction.features.macd_diff.toFixed(4), desc: prediction.features.macd_diff > 0 ? 'Positive momentum' : 'Negative momentum', color: prediction.features.macd_diff > 0 ? '#22c55e' : '#ef4444' },
                { label: 'BUY prob', value: `${(prediction.prediction.probabilities.BUY * 100).toFixed(1)}%`, desc: 'LightGBM BUY class', color: '#22c55e' },
                { label: 'SELL prob', value: `${(prediction.prediction.probabilities.SELL * 100).toFixed(1)}%`, desc: 'LightGBM SELL class', color: '#ef4444' },
              ].map(({ label, value, desc, color }) => (
                <div key={label} style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 12, padding: '14px 16px' }}>
                  <p style={{ fontSize: 11, color: '#4b5563', marginBottom: 4, fontWeight: 600 }}>{label}</p>
                  <p style={{ fontSize: 22, fontWeight: 800, color, fontFamily: 'monospace', lineHeight: 1 }}>{value}</p>
                  <p style={{ fontSize: 11, color: '#374151', marginTop: 6 }}>{desc}</p>
                </div>
              ))}
            </div>

            {prediction.has_commentary && (
              <Commentary text={prediction.commentary} />
            )}

            {/* Optional enrichment panels — only visible when API keys are set */}
            <EnrichmentPanel enrichments={prediction.enrichments} />
          </>
        )}

        {/* ── EMPTY STATE ── */}
        {!prediction && !loading && (
          <div style={{ textAlign: 'center', padding: '80px 24px' }}>
            <p style={{ fontSize: 48, marginBottom: 16 }}>📊</p>
            <p style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Ready to predict</p>
            <p style={{ color: '#4b5563', fontSize: 14, maxWidth: 400, margin: '0 auto' }}>
              Select a ticker above and click Predict. The system will fetch live market data,
              compute all 17 features, run LightGBM, and compute SHAP values — all in real time.
            </p>
          </div>
        )}

        {/* ── ADVANCED / RETRAIN ── */}
        <div style={{ marginTop: 48, paddingTop: 24, borderTop: '1px solid #111122' }}>
          <p style={{ fontSize: 12, color: '#374151', fontWeight: 600, marginBottom: 6 }}>⚙️ Advanced — Live Retraining</p>
          <p style={{ fontSize: 11, color: '#1f2937', marginBottom: 12 }}>
            Triggers a full retrain of the selected model on the latest 365 days of yfinance data (~60s). For technical recruiters.
          </p>
          <RetrainButton ticker={ticker} horizon={horizon} />
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
