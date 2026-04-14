import { useState, useRef, useEffect, useMemo } from 'react'
import { fetchPrediction, fetchDashboardPreview } from '../lib/api'
import type { Prediction, DashboardPreview } from '../lib/api'
import { getOfflineDashboardPreview } from '../data/offlineDashboardPreview'
import HorizonToggle from '../components/HorizonToggle'
import PredictionCard from '../components/PredictionCard'
import ShapChart from '../components/ShapChart'
import Commentary from '../components/Commentary'
import RetrainButton from '../components/RetrainButton'
import EnrichmentPanel from '../components/EnrichmentPanel'
import MarketHistoryPanel from '../components/MarketHistoryPanel'
import toast from 'react-hot-toast'

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

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

  const [preview, setPreview] = useState<DashboardPreview | null>(null)
  const [previewLoading, setPreviewLoading] = useState(true)
  const [previewErr, setPreviewErr] = useState<string | null>(null)

  const skipLivePreviewFetch = import.meta.env.PROD && !import.meta.env.VITE_API_URL

  const offlinePreview = useMemo(
    () => getOfflineDashboardPreview(ticker, horizon),
    [ticker, horizon],
  )

  const resolvedPreview = useMemo((): DashboardPreview => {
    if (preview && !previewErr) {
      if (preview.ml_preview) return preview
      return {
        ...preview,
        ml_preview: offlinePreview.ml_preview,
        ml_preview_error: preview.ml_preview_error,
      }
    }
    return offlinePreview
  }, [preview, previewErr, offlinePreview])

  useEffect(() => {
    if (skipLivePreviewFetch) {
      setPreviewLoading(false)
      setPreviewErr(null)
      setPreview(null)
      return
    }
    const ac = new AbortController()
    setPreviewLoading(true)
    setPreviewErr(null)
    setPreview(null)
    fetchDashboardPreview(ticker, horizon, ac.signal)
      .then((data) => {
        if (!ac.signal.aborted) setPreview(data)
      })
      .catch((e: unknown) => {
        if (ac.signal.aborted) return
        const msg = e && typeof e === 'object' && 'message' in e ? String((e as Error).message) : 'Request failed'
        setPreviewErr(msg)
      })
      .finally(() => {
        if (!ac.signal.aborted) setPreviewLoading(false)
      })
    return () => ac.abort()
  }, [ticker, horizon, skipLivePreviewFetch])

  const displayPrediction = prediction ?? (!loading ? resolvedPreview.ml_preview ?? null : null)
  const isLiveHistorySnapshot =
    !prediction && !!preview?.ml_preview && !!displayPrediction && !displayPrediction.demo_data
  const isDemoLayout = !!displayPrediction?.demo_data

  const handlePredict = async (t = ticker, h = horizon) => {
    abortRef.current?.abort()
    const ac = new AbortController()
    abortRef.current = ac
    const seq = ++predictSeq.current

    setLoading(true)
    setPrediction(null)
    setLoadTime(null)
    const start = Date.now()
    const RETRY_ID = 'predict-retry'

    const load = async () => {
      const data = await fetchPrediction(t, h, ac.signal)
      if (seq !== predictSeq.current) return null
      return data
    }

    try {
      let data: Prediction | null = null
      try {
        data = await load()
      } catch (first) {
        if (seq !== predictSeq.current) return
        if (ac.signal.aborted) return
        const e0 = first as { code?: string }
        if (e0?.code === 'ERR_CANCELED') return
        toast.loading('Backend may be waking up — retrying once in 5s…', { id: RETRY_ID, duration: 6000 })
        await sleep(5000)
        toast.dismiss(RETRY_ID)
        if (seq !== predictSeq.current) return
        if (ac.signal.aborted) return
        data = await load()
      }
      if (!data || seq !== predictSeq.current) return
      setLoadTime(Date.now() - start)
      setPrediction(data)
      toast.dismiss()
    } catch (e: unknown) {
      if (seq !== predictSeq.current) return
      if (ac.signal.aborted) return
      const err = e as { code?: string }
      if (err?.code === 'ERR_CANCELED') return
      toast.dismiss(RETRY_ID)
      console.error(e)
      toast.error(
        'Predict failed. If the backend was asleep, wait and try again. If it always fails: set VITE_API_URL in Vercel to your Render https URL and redeploy.',
        { duration: 9000 },
      )
    } finally {
      if (seq === predictSeq.current) setLoading(false)
    }
  }

  const handleTickerChange = (t: string) => {
    setTicker(t)
  }

  const handleHorizonChange = (h: number) => {
    setHorizon(h)
    if (prediction) handlePredict(ticker, h)
  }

  const labelColor = displayPrediction?.prediction.label === 'BUY'
    ? '#22c55e' : displayPrediction?.prediction.label === 'SELL'
    ? '#ef4444' : '#eab308'

  const marketState = {
    data: resolvedPreview,
    loading: false,
    error: null,
  }

  const showLiveFetchNote = previewErr && !skipLivePreviewFetch

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

        {import.meta.env.PROD && !import.meta.env.VITE_API_URL && (
          <div style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)', borderRadius: 14, padding: '14px 18px', marginBottom: 20 }}>
            <p style={{ fontSize: 13, color: '#fecaca', fontWeight: 700, marginBottom: 6 }}>VITE_API_URL is not set</p>
            <p style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.6 }}>
              The browser cannot reach your Render API. In Vercel → Project → Settings → Environment Variables, add <code style={{ color: '#e5e7eb' }}>VITE_API_URL</code> = your backend URL (example: <code style={{ color: '#e5e7eb' }}>https://your-service.onrender.com</code>), then redeploy. Rebuilds bake this value into the site.
            </p>
          </div>
        )}

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
          <p style={{ fontSize: 11, color: '#374151', marginTop: 10, maxWidth: 720, lineHeight: 1.6 }}>
            <strong style={{ color: '#6b7280' }}>Dashboard load:</strong> chart and model cards load from <code style={{ color: '#4b5563' }}>/api/dashboard-preview</code> when the backend is configured (~4y Yahoo history, same feature pipeline, LightGBM + SHAP on the latest bar).{' '}
            Without <code style={{ color: '#4b5563' }}>VITE_API_URL</code>, the page shows a <strong style={{ color: '#6b7280' }}>bundled sample</strong> so the layout is never empty.{' '}
            <strong style={{ color: '#6b7280' }}>Predict</strong> runs a fresh live pull and optional enrichments. Free Render can sleep — first Predict after idle may take <strong style={{ color: '#6b7280' }}>30–90s</strong> (we auto-retry once).
          </p>
        </div>

        {previewLoading && !skipLivePreviewFetch && (
          <p style={{ fontSize: 11, color: '#4b5563', marginBottom: 10 }}>Syncing live dashboard data…</p>
        )}

        {previewLoading && !skipLivePreviewFetch && (
          <p style={{ fontSize: 11, color: '#4b5563', marginBottom: 12 }}>Loading live dashboard data…</p>
        )}

        {/* ── 4Y MARKET + model strip (live, merged, or bundled sample) ── */}
        <div style={{ marginBottom: 24 }}>
          <MarketHistoryPanel ticker={ticker} market={marketState} />
        </div>

        {isDemoLayout && !prediction && (
          <div style={{ background: 'rgba(234,179,8,0.08)', border: '1px solid rgba(234,179,8,0.35)', borderRadius: 14, padding: '14px 18px', marginBottom: 20 }}>
            <p style={{ fontSize: 13, color: '#fcd34d', fontWeight: 700, marginBottom: 6 }}>Sample data (offline)</p>
            <p style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.65 }}>
              {preview && !previewErr
                ? (
                    <>
                      The <strong style={{ color: '#e5e7eb' }}>price chart</strong> above is live from Yahoo. The <strong style={{ color: '#e5e7eb' }}>signal, SHAP, and tiles</strong> use bundled sample values until the server can run your trained models.
                    </>
                  )
                : (
                    <>
                      Chart and model cards are bundled in the frontend so the dashboard always renders (for example on Vercel without <code style={{ color: '#e5e7eb' }}>VITE_API_URL</code>). Set <code style={{ color: '#e5e7eb' }}>VITE_API_URL</code> to your Render URL and redeploy to replace this with live Yahoo + your models.
                    </>
                  )}
            </p>
            {showLiveFetchNote && (
              <p style={{ fontSize: 11, color: '#78716c', marginTop: 10, lineHeight: 1.55 }}>
                Live <code style={{ color: '#a8a29e' }}>/api/dashboard-preview</code> could not be reached ({previewErr}) — showing bundled sample instead.
              </p>
            )}
          </div>
        )}

        {preview?.ml_preview_error && !prediction && preview && !isDemoLayout && (
          <div style={{ background: 'rgba(234,179,8,0.08)', border: '1px solid rgba(234,179,8,0.35)', borderRadius: 14, padding: '14px 18px', marginBottom: 20 }}>
            <p style={{ fontSize: 13, color: '#fcd34d', fontWeight: 700, marginBottom: 6 }}>Live model output unavailable</p>
            <p style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.6 }}>{preview.ml_preview_error} Signal card uses bundled sample until models are deployed.</p>
          </div>
        )}

        {preview?.ml_preview?.preview_note && isLiveHistorySnapshot && (
          <div style={{ background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.35)', borderRadius: 14, padding: '14px 18px', marginBottom: 20 }}>
            <p style={{ fontSize: 13, color: '#93c5fd', fontWeight: 700, marginBottom: 6 }}>About this view</p>
            <p style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.65 }}>{preview.ml_preview.preview_note}</p>
          </div>
        )}

        {/* ── LOADING STATE ── */}
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '48px 24px 32px', gap: 20 }}>
            <div style={{
              width: 48, height: 48, borderRadius: '50%',
              border: '4px solid #1f2937', borderTopColor: '#3b82f6',
              animation: 'spin 1s linear infinite',
            }} />
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: '#9ca3af', marginBottom: 8 }}>Running the full pipeline for <strong>{ticker}</strong> ({horizon}d)</p>
              <p style={{ fontSize: 12, color: '#4b5563', marginBottom: 12, maxWidth: 420 }}>
                Please wait — cold backends often need up to 90s. Do not click Predict again unless you want to cancel and restart.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, justifyContent: 'center' }}>
                {['yfinance', '17 features', 'LightGBM', 'SHAP'].map((s, i) => (
                  <span key={i} style={{ fontSize: 11, color: '#374151' }}>{s}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── RESULTS (live predict or 4y-based preview) ── */}
        {displayPrediction && !loading && (
          <>
            <div style={{ background: `${labelColor}10`, border: `1px solid ${labelColor}30`, borderRadius: 16, padding: '16px 24px', marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ fontSize: 32, fontWeight: 900, color: labelColor, fontFamily: 'monospace' }}>
                  {displayPrediction.prediction.label}
                </span>
                <div>
                  <p style={{ fontWeight: 700, fontSize: 16 }}>
                    {TICKER_NAMES[displayPrediction.ticker]} · {displayPrediction.horizon}-day signal
                    {isLiveHistorySnapshot && (
                      <span style={{ marginLeft: 8, fontSize: 11, color: '#60a5fa', fontWeight: 600 }}>(historical snapshot)</span>
                    )}
                    {isDemoLayout && !prediction && (
                      <span style={{ marginLeft: 8, fontSize: 11, color: '#fbbf24', fontWeight: 600 }}>(sample)</span>
                    )}
                  </p>
                  <p style={{ fontSize: 13, color: '#6b7280' }}>
                    {(displayPrediction.prediction.confidence * 100).toFixed(1)}% model confidence ·{' '}
                    {displayPrediction.features.ai_regime === 1 ? '⚡ High AI regime' : '— Low AI regime'}
                  </p>
                </div>
              </div>
              <div style={{ fontSize: 12, color: '#4b5563', textAlign: 'right' }}>
                <p>Model: LightGBM (lgbm_{displayPrediction.ticker}_{displayPrediction.horizon}d)</p>
                <p>Features: 17 technical indicators</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <PredictionCard prediction={displayPrediction} />
              <ShapChart shapValues={displayPrediction.shap_values} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginBottom: displayPrediction.has_commentary ? 16 : 0 }}>
              {[
                { label: 'RSI (14)', value: displayPrediction.features.rsi.toString(), desc: displayPrediction.features.rsi < 30 ? 'Oversold zone' : displayPrediction.features.rsi > 70 ? 'Overbought zone' : 'Neutral range', color: displayPrediction.features.rsi < 30 ? '#22c55e' : displayPrediction.features.rsi > 70 ? '#ef4444' : '#9ca3af' },
                { label: 'AI Intensity', value: `${(displayPrediction.features.ai_index * 100).toFixed(1)}%`, desc: displayPrediction.features.ai_regime === 1 ? '⚡ High algo regime' : '— Low algo regime', color: displayPrediction.features.ai_regime === 1 ? '#8b5cf6' : '#4b5563' },
                { label: '10d Volatility', value: `${(displayPrediction.features.volatility_10d * 100).toFixed(2)}%`, desc: displayPrediction.features.volatility_10d > 0.02 ? 'Elevated volatility' : 'Calm market', color: displayPrediction.features.volatility_10d > 0.02 ? '#f59e0b' : '#9ca3af' },
                { label: 'MACD Diff', value: displayPrediction.features.macd_diff.toFixed(4), desc: displayPrediction.features.macd_diff > 0 ? 'Positive momentum' : 'Negative momentum', color: displayPrediction.features.macd_diff > 0 ? '#22c55e' : '#ef4444' },
                { label: 'BUY prob', value: `${(displayPrediction.prediction.probabilities.BUY * 100).toFixed(1)}%`, desc: 'LightGBM BUY class', color: '#22c55e' },
                { label: 'SELL prob', value: `${(displayPrediction.prediction.probabilities.SELL * 100).toFixed(1)}%`, desc: 'LightGBM SELL class', color: '#ef4444' },
              ].map(({ label, value, desc, color }) => (
                <div key={label} style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 12, padding: '14px 16px' }}>
                  <p style={{ fontSize: 11, color: '#4b5563', marginBottom: 4, fontWeight: 600 }}>{label}</p>
                  <p style={{ fontSize: 22, fontWeight: 800, color, fontFamily: 'monospace', lineHeight: 1 }}>{value}</p>
                  <p style={{ fontSize: 11, color: '#374151', marginTop: 6 }}>{desc}</p>
                </div>
              ))}
            </div>

            {displayPrediction.has_commentary && (
              <Commentary
                text={displayPrediction.commentary}
                variant={displayPrediction.demo_data ? 'note' : 'gpt'}
              />
            )}

            <EnrichmentPanel enrichments={displayPrediction.enrichments} />
          </>
        )}

        {!displayPrediction && !loading && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20, marginBottom: 24, alignItems: 'start' }}>
            <div style={{ background: '#080812', border: '1px solid #1f2937', borderRadius: 16, padding: '22px 24px' }}>
              <p style={{ fontSize: 11, color: '#3b82f6', fontWeight: 700, letterSpacing: '0.1em', marginBottom: 12 }}>HOW THIS DASHBOARD WORKS</p>
              <ol style={{ margin: 0, paddingLeft: 18, color: '#9ca3af', fontSize: 13, lineHeight: 1.85 }}>
                <li><strong style={{ color: '#e5e7eb' }}>Background load</strong> — ~4y chart + model cards from the backend when configured, otherwise a bundled sample keeps the page populated.</li>
                <li><strong style={{ color: '#e5e7eb' }}>Predict</strong> — fresh yfinance pull, optional news / Reddit / analyst cards if keys are set.</li>
                <li><strong style={{ color: '#e5e7eb' }}>Signal + SHAP</strong> — BUY / SELL / HOLD, probabilities, and feature attribution.</li>
              </ol>
            </div>
          </div>
        )}

        {!displayPrediction && !loading && (
          <div style={{ textAlign: 'center', padding: '40px 24px 60px' }}>
            <p style={{ fontSize: 36, marginBottom: 12 }}>▶</p>
            <p style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Click Predict for a full live run</p>
            <p style={{ color: '#4b5563', fontSize: 14, maxWidth: 520, margin: '0 auto', lineHeight: 1.65 }}>
              If the model preview could not load (missing <code style={{ color: '#4b5563' }}>.pkl</code> on the server), deploy trained models to Render. The 4y price chart still shows when Yahoo data is reachable.
            </p>
          </div>
        )}

        {/* ── ADVANCED / RETRAIN ── */}
        <div style={{ marginTop: 48, paddingTop: 24, borderTop: '1px solid #111122' }}>
          <p style={{ fontSize: 12, color: '#374151', fontWeight: 600, marginBottom: 6 }}>⚙️ Advanced — Live Retraining</p>
          <p style={{ fontSize: 11, color: '#1f2937', marginBottom: 12 }}>
            Triggers a full retrain of the selected model on the latest 365 days of yfinance data (~60s).
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
