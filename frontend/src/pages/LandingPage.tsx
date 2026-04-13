import { useNavigate } from 'react-router-dom'

const TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']

const PIPELINE_STEPS = [
  {
    step: '01',
    icon: '📡',
    title: 'Live Market Data',
    subtitle: 'yfinance · No API key · Always fresh',
    desc: 'Every time you click Predict, the system fetches the last 120 days of real price, volume, and OHLCV data directly from Yahoo Finance. No cached data — the model always sees what the market looked like today.',
    detail: '120 days · 5 tickers · OHLCV',
  },
  {
    step: '02',
    icon: '⚙️',
    title: 'Feature Engineering',
    subtitle: '17 technical indicators · AI Intensity Index',
    desc: 'Raw price data is transformed into 17 meaningful signals that quantitative analysts actually use: momentum (RSI), trend (MACD), volatility (Bollinger Bands), volume anomalies, and more. The AI Intensity Index is original research — it measures how much algorithmic trading is dominating the market right now.',
    detail: 'RSI · MACD · Bollinger Bands · Volume Z-Score · AI Index',
  },
  {
    step: '03',
    icon: '🧠',
    title: 'LightGBM Prediction',
    subtitle: 'Gradient boosting · TimeSeriesSplit CV · Balanced classes',
    desc: 'A LightGBM gradient boosting model — the same algorithm used in top-ranked Kaggle competitions and by hedge funds — takes these 17 features and outputs a probability distribution over three outcomes: BUY, SELL, or HOLD. Trained with time-series cross-validation to prevent data leakage.',
    detail: '15 models · 300 trees · 3-class output',
  },
  {
    step: '04',
    icon: '🔍',
    title: 'SHAP Explainability',
    subtitle: 'Not a black box — every prediction explained',
    desc: 'SHAP (SHapley Additive exPlanations) breaks open the model and shows you exactly which features pushed the prediction toward BUY or SELL, and by how much. This is the same explainability technique used in production ML systems at financial institutions.',
    detail: 'TreeExplainer · Top 8 features · Per-prediction',
  },
]

const ML_MODELS = [
  {
    name: 'LightGBM',
    badge: 'Primary Model',
    badgeColor: '#22c55e',
    desc: 'Gradient boosted decision trees. Fast, handles missing values, excellent on tabular financial data. Used in production by many quant funds.',
    why: 'Handles class imbalance with built-in class_weight. Trains in seconds on 3 years of data.',
  },
  {
    name: 'Meta-Labeling Gate',
    badge: 'Signal Filter',
    badgeColor: '#3b82f6',
    desc: 'Inspired by Marcos López de Prado\'s "Advances in Financial Machine Learning" — a secondary model layer that filters low-confidence predictions and reduces false signals.',
    why: 'BUY/SELL only fires when model confidence exceeds threshold. HOLD otherwise.',
  },
  {
    name: 'AI Intensity Index',
    badge: 'Original Research',
    badgeColor: '#a855f7',
    desc: 'A custom composite signal built from rolling percentile ranks of volatility, volume anomaly, MACD divergence, and Bollinger Band width. Detects when algorithmic trading is dominating price action.',
    why: 'High AI regime = more predictable patterns. Low regime = noisy/random market.',
  },
  {
    name: 'TimeSeriesSplit CV',
    badge: 'No Data Leakage',
    badgeColor: '#f59e0b',
    desc: 'Standard cross-validation randomly shuffles data, which leaks future data into training in time series problems. TimeSeriesSplit respects temporal order — train on past, validate on future.',
    why: 'Ensures reported accuracy is honest. Prevents look-ahead bias.',
  },
]

const FEATURES_EXPLAINED = [
  { name: 'RSI (14)', what: 'Relative Strength Index', range: '0–100', signal: 'Below 30 = oversold (potential BUY) · Above 70 = overbought (potential SELL)', color: '#22c55e' },
  { name: 'MACD Diff', what: 'Moving Avg Convergence/Divergence', range: 'Unbounded', signal: 'Positive = upward momentum · Negative = downward momentum', color: '#3b82f6' },
  { name: 'BB Width', what: 'Bollinger Band Width', range: '0–1', signal: 'Wide = high volatility · Narrow = squeeze (breakout incoming)', color: '#a855f7' },
  { name: 'Volume Z-Score', what: 'Volume deviation from 20d mean', range: '-3 to +3', signal: 'High positive = unusual volume spike (institutional activity)', color: '#f59e0b' },
  { name: 'AI Index', what: 'Algorithmic Trading Intensity', range: '0–1', signal: 'Above rolling mean = high AI regime (more predictable patterns)', color: '#ec4899' },
  { name: '10d Volatility', what: 'Annualized rolling volatility', range: '0–1', signal: 'High = uncertain market · Low = calm trending market', color: '#14b8a6' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{ backgroundColor: '#05050f', color: '#e5e7eb', fontFamily: 'system-ui, sans-serif' }}>

      {/* ── HERO ── */}
      <section style={{ position: 'relative', overflow: 'hidden', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '80px 24px' }}>
        {/* Radial glow */}
        <div style={{ position: 'absolute', top: '30%', left: '50%', transform: 'translate(-50%,-50%)', width: 800, height: 800, background: 'radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)', pointerEvents: 'none' }} />
        {/* Grid */}
        <div style={{ position: 'absolute', inset: 0, opacity: 0.03, backgroundImage: 'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)', backgroundSize: '48px 48px', pointerEvents: 'none' }} />

        {/* Badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderRadius: 999, border: '1px solid rgba(59,130,246,0.3)', background: 'rgba(59,130,246,0.06)', color: '#93c5fd', fontSize: 12, fontWeight: 600, letterSpacing: '0.05em', marginBottom: 32 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
          CS 4771 Machine Learning · University of Idaho · Ankit Paudel
        </div>

        <h1 style={{ fontSize: 'clamp(36px, 7vw, 80px)', fontWeight: 900, lineHeight: 1.05, letterSpacing: '-0.03em', marginBottom: 24, maxWidth: 900 }}>
          AI-Dominated{' '}
          <span style={{ background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Market Regime
          </span>
          <br />Detection
        </h1>

        <p style={{ fontSize: 18, color: '#9ca3af', maxWidth: 620, lineHeight: 1.7, marginBottom: 16 }}>
          A live ML system that detects whether algorithmic traders are dominating the market —
          and uses that signal to predict <strong style={{ color: '#e5e7eb' }}>BUY / SELL / HOLD</strong> for
          major US equities with full explainability.
        </p>
        <p style={{ fontSize: 13, color: '#4b5563', marginBottom: 40 }}>
          Pre-trained LightGBM · Live yfinance data · SHAP explanations · FastAPI + React
        </p>

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center', marginBottom: 56 }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{ padding: '14px 32px', borderRadius: 12, background: 'linear-gradient(135deg, #3b82f6, #6366f1)', border: 'none', color: '#fff', fontWeight: 700, fontSize: 15, cursor: 'pointer', boxShadow: '0 0 40px rgba(59,130,246,0.3)' }}
          >
            Open Live Dashboard →
          </button>
          <a
            href="https://github.com/paudelAnkit"
            target="_blank"
            rel="noopener noreferrer"
            style={{ padding: '14px 32px', borderRadius: 12, background: 'transparent', border: '1px solid #374151', color: '#9ca3af', fontWeight: 600, fontSize: 15, textDecoration: 'none' }}
          >
            GitHub ↗
          </a>
        </div>

        {/* Ticker strip */}
        <div style={{ display: 'flex', gap: 8 }}>
          {TICKERS.map((t) => (
            <span key={t} style={{ fontFamily: 'monospace', fontSize: 13, color: '#374151', padding: '4px 12px', borderRadius: 6, border: '1px solid #1f2937', background: '#0a0a18' }}>
              {t}
            </span>
          ))}
        </div>
      </section>

      {/* ── THE PROBLEM ── */}
      <section style={{ padding: '100px 24px', maxWidth: 900, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 60, alignItems: 'center' }}>
          <div>
            <p style={{ color: '#6366f1', fontWeight: 700, fontSize: 12, letterSpacing: '0.12em', marginBottom: 16 }}>THE PROBLEM</p>
            <h2 style={{ fontSize: 'clamp(24px, 3vw, 36px)', fontWeight: 800, lineHeight: 1.2, marginBottom: 20 }}>
              Markets behave differently when algorithms dominate
            </h2>
            <p style={{ color: '#6b7280', lineHeight: 1.8, marginBottom: 16 }}>
              Over 70% of US equity volume is now driven by algorithmic and high-frequency trading systems. These AI-dominated regimes create distinct price patterns — momentum amplification, tighter spreads, faster mean reversion — that traditional technical analysis wasn't designed to detect.
            </p>
            <p style={{ color: '#6b7280', lineHeight: 1.8 }}>
              This project builds a regime detector that identifies <em style={{ color: '#9ca3af' }}>when</em> algorithms are in control, then uses that regime signal as an additional feature for directional prediction.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {[
              { label: 'Tickers covered', value: '5', sub: 'AAPL GOOGL MSFT TSLA NVDA' },
              { label: 'ML models trained', value: '15', sub: '5 tickers × 3 horizons' },
              { label: 'Technical features', value: '17', sub: 'indicators + AI index' },
              { label: 'Prediction horizons', value: '3', sub: '1 day · 3 day · 5 day' },
            ].map(({ label, value, sub }) => (
              <div key={label} style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 16, padding: 20 }}>
                <p style={{ fontSize: 36, fontWeight: 900, color: '#3b82f6', fontFamily: 'monospace', lineHeight: 1 }}>{value}</p>
                <p style={{ fontSize: 12, fontWeight: 600, color: '#e5e7eb', marginTop: 6 }}>{label}</p>
                <p style={{ fontSize: 11, color: '#4b5563', marginTop: 4 }}>{sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS — PIPELINE ── */}
      <section style={{ padding: '100px 24px', background: '#080812' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <p style={{ color: '#6366f1', fontWeight: 700, fontSize: 12, letterSpacing: '0.12em', marginBottom: 12, textAlign: 'center' }}>THE PIPELINE</p>
          <h2 style={{ fontSize: 'clamp(24px, 3vw, 40px)', fontWeight: 800, textAlign: 'center', marginBottom: 8 }}>From raw price to explained prediction</h2>
          <p style={{ color: '#6b7280', textAlign: 'center', marginBottom: 60, fontSize: 15 }}>Four stages — all running live, every time you click Predict</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {PIPELINE_STEPS.map(({ step, icon, title, subtitle, desc, detail }, i) => (
              <div key={step} style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: 0, position: 'relative' }}>
                {/* connector line */}
                {i < PIPELINE_STEPS.length - 1 && (
                  <div style={{ position: 'absolute', left: 39, top: 64, bottom: -2, width: 2, background: 'linear-gradient(to bottom, #3b82f620, transparent)' }} />
                )}
                {/* step number */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 20 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: '#0d0d1a', border: '2px solid #3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16 }}>
                    {icon}
                  </div>
                </div>
                {/* content */}
                <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 16, padding: '24px 28px', marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8, flexWrap: 'wrap', gap: 8 }}>
                    <div>
                      <span style={{ fontSize: 11, color: '#3b82f6', fontWeight: 700, fontFamily: 'monospace', marginRight: 12 }}>STEP {step}</span>
                      <span style={{ fontSize: 17, fontWeight: 800 }}>{title}</span>
                    </div>
                    <span style={{ fontSize: 11, color: '#4b5563', fontFamily: 'monospace' }}>{detail}</span>
                  </div>
                  <p style={{ fontSize: 12, color: '#6366f1', fontWeight: 600, marginBottom: 10 }}>{subtitle}</p>
                  <p style={{ color: '#9ca3af', fontSize: 14, lineHeight: 1.75 }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ML MODELS EXPLAINED ── */}
      <section style={{ padding: '100px 24px', maxWidth: 960, margin: '0 auto' }}>
        <p style={{ color: '#6366f1', fontWeight: 700, fontSize: 12, letterSpacing: '0.12em', marginBottom: 12, textAlign: 'center' }}>MACHINE LEARNING METHODS</p>
        <h2 style={{ fontSize: 'clamp(24px, 3vw, 40px)', fontWeight: 800, textAlign: 'center', marginBottom: 8 }}>Four techniques working together</h2>
        <p style={{ color: '#6b7280', textAlign: 'center', marginBottom: 60, maxWidth: 600, margin: '0 auto 60px' }}>Each method solves a specific problem in financial ML. Here's what each one does and why it's here.</p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: 16 }}>
          {ML_MODELS.map(({ name, badge, badgeColor, desc, why }) => (
            <div key={name} style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 20, padding: 28 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16, gap: 12 }}>
                <h3 style={{ fontSize: 18, fontWeight: 800, margin: 0 }}>{name}</h3>
                <span style={{ fontSize: 10, fontWeight: 700, padding: '4px 10px', borderRadius: 999, border: `1px solid ${badgeColor}40`, color: badgeColor, background: `${badgeColor}10`, whiteSpace: 'nowrap' }}>
                  {badge}
                </span>
              </div>
              <p style={{ color: '#9ca3af', fontSize: 14, lineHeight: 1.75, marginBottom: 16 }}>{desc}</p>
              <div style={{ background: '#070710', borderRadius: 10, padding: '12px 16px', borderLeft: `3px solid ${badgeColor}` }}>
                <p style={{ fontSize: 12, color: '#6b7280', marginBottom: 4, fontWeight: 600 }}>WHY THIS MATTERS</p>
                <p style={{ fontSize: 13, color: '#9ca3af', lineHeight: 1.6 }}>{why}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES EXPLAINED ── */}
      <section style={{ padding: '100px 24px', background: '#080812' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <p style={{ color: '#6366f1', fontWeight: 700, fontSize: 12, letterSpacing: '0.12em', marginBottom: 12, textAlign: 'center' }}>FEATURES DECODED</p>
          <h2 style={{ fontSize: 'clamp(24px, 3vw, 40px)', fontWeight: 800, textAlign: 'center', marginBottom: 8 }}>What the model actually looks at</h2>
          <p style={{ color: '#6b7280', textAlign: 'center', marginBottom: 56, fontSize: 15 }}>Every SHAP chart in the dashboard refers to these features. Here's what each one means in plain English.</p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
            {FEATURES_EXPLAINED.map(({ name, what, range, signal, color }) => (
              <div key={name} style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 16, padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, flexShrink: 0 }} />
                  <span style={{ fontFamily: 'monospace', fontWeight: 800, fontSize: 14, color: '#e5e7eb' }}>{name}</span>
                </div>
                <p style={{ fontSize: 12, color: '#6b7280', marginBottom: 6 }}>{what}</p>
                <p style={{ fontSize: 11, color: '#374151', marginBottom: 10 }}>Range: <span style={{ color: '#4b5563' }}>{range}</span></p>
                <div style={{ borderTop: '1px solid #1f2937', paddingTop: 10 }}>
                  <p style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.6 }}>{signal}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHAT YOU SEE IN THE DASHBOARD ── */}
      <section style={{ padding: '100px 24px', maxWidth: 960, margin: '0 auto' }}>
        <p style={{ color: '#6366f1', fontWeight: 700, fontSize: 12, letterSpacing: '0.12em', marginBottom: 12, textAlign: 'center' }}>DASHBOARD WALKTHROUGH</p>
        <h2 style={{ fontSize: 'clamp(24px, 3vw, 40px)', fontWeight: 800, textAlign: 'center', marginBottom: 56 }}>Every panel, explained</h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
          {[
            { icon: '🎯', title: 'Prediction Signal', color: '#22c55e', desc: 'BUY / SELL / HOLD — the model\'s directional call. Colored green, red, or yellow. Shows which of the 3 classes got the highest probability from LightGBM.', badge: 'LightGBM output' },
            { icon: '📊', title: 'Probability Bars', color: '#3b82f6', desc: 'Three confidence bars showing the full probability distribution across BUY, SELL, and HOLD. A 90% HOLD is very different from a 34% HOLD — this shows the certainty.', badge: 'Softmax probabilities' },
            { icon: '⚡', title: 'AI Intensity Index', color: '#a855f7', desc: 'The custom regime score (0–100%). Above its own rolling mean = high AI regime. In high AI regimes, the model historically performs better because algorithmic patterns are more consistent.', badge: 'Original feature' },
            { icon: '🔍', title: 'SHAP Feature Chart', color: '#f59e0b', desc: 'A horizontal bar chart showing which features drove THIS prediction. Green bars pushed toward the signal, red bars pushed against it. Not a global average — computed fresh for each prediction.', badge: 'TreeExplainer' },
            { icon: '📅', title: 'Horizon Toggle', color: '#14b8a6', desc: '1-day, 3-day, and 5-day prediction windows. Each is a completely separate trained model. Longer horizons are generally smoother but less reactive to intraday news.', badge: '3 separate models' },
            { icon: '💬', title: 'GPT-4o Commentary', color: '#ec4899', desc: 'If an OpenAI API key is configured, GPT-4o writes a 2-sentence plain-English analysis of the prediction, citing the regime and top SHAP feature. Optional — dashboard works fully without it.', badge: 'Optional AI layer' },
          ].map(({ icon, title, color, desc, badge }) => (
            <div key={title} style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 18, padding: 24 }}>
              <div style={{ display: 'flex', align: 'flex-start', justifyContent: 'space-between', marginBottom: 12, gap: 8 }}>
                <span style={{ fontSize: 28 }}>{icon}</span>
                <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 999, background: `${color}15`, color, border: `1px solid ${color}30`, fontWeight: 600, height: 'fit-content' }}>{badge}</span>
              </div>
              <h3 style={{ fontWeight: 800, fontSize: 15, marginBottom: 10 }}>{title}</h3>
              <p style={{ fontSize: 13, color: '#6b7280', lineHeight: 1.7 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{ padding: '100px 24px', textAlign: 'center', background: '#080812' }}>
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
          <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 900, lineHeight: 1.1, marginBottom: 20 }}>
            See it work on{' '}
            <span style={{ background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              live market data
            </span>
          </h2>
          <p style={{ color: '#6b7280', fontSize: 16, lineHeight: 1.7, marginBottom: 40 }}>
            Pick any of the 5 tickers. Choose a 1, 3, or 5-day horizon.
            Hit Predict — live yfinance data flows through all 4 pipeline stages in under 5 seconds.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            style={{ padding: '16px 40px', borderRadius: 14, background: 'linear-gradient(135deg, #3b82f6, #6366f1)', border: 'none', color: '#fff', fontWeight: 700, fontSize: 16, cursor: 'pointer', boxShadow: '0 0 60px rgba(99,102,241,0.3)' }}
          >
            Open Dashboard →
          </button>
        </div>
      </section>

      {/* ── TECH STACK ── */}
      <section style={{ padding: '60px 24px 80px', maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
        <p style={{ color: '#374151', fontSize: 12, fontWeight: 600, letterSpacing: '0.1em', marginBottom: 20 }}>FULL STACK</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
          {[
            'LightGBM', 'SHAP', 'scikit-learn', 'pandas', 'numpy', 'ta',
            'FastAPI', 'Python', 'React', 'TypeScript', 'Tailwind CSS',
            'Recharts', 'yfinance', 'GPT-4o (optional)', 'Vercel', 'Render',
          ].map((t) => (
            <span key={t} style={{ fontSize: 12, padding: '6px 14px', borderRadius: 999, border: '1px solid #1f2937', color: '#6b7280', background: '#0d0d1a' }}>
              {t}
            </span>
          ))}
        </div>
      </section>

      {/* ── DISCLAIMER + FOOTER ── */}
      <div style={{ borderTop: '1px solid #111122', padding: '24px', textAlign: 'center' }}>
        <p style={{ fontSize: 12, color: '#d97706', marginBottom: 16 }}>
          ⚠️ Research project for CS 4771 Machine Learning — University of Idaho. Not financial advice.
        </p>
        <p style={{ fontSize: 12, color: '#374151' }}>
          Built by{' '}
          <a href="https://github.com/paudelAnkit" target="_blank" rel="noopener noreferrer" style={{ color: '#4b5563', textDecoration: 'none' }}>
            Ankit Paudel
          </a>
          {' '}· University of Idaho · CS 4771 Machine Learning
        </p>
      </div>
    </div>
  )
}
