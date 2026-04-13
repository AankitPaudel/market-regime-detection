import { useNavigate } from 'react-router-dom'

const scrollTo = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const NAV_LINKS = [
  { label: 'How it works', id: 'how-it-works' },
  { label: 'ML methods', id: 'ml-methods' },
  { label: 'Features', id: 'features' },
  { label: 'Dashboard guide', id: 'dashboard-guide' },
  { label: 'Optional APIs', id: 'optional-apis' },
]

const STATS = [
  { value: '5', label: 'Tickers', sub: 'AAPL · GOOGL · MSFT · TSLA · NVDA' },
  { value: '15', label: 'Trained models', sub: '5 tickers × 3 time horizons' },
  { value: '17', label: 'Input features', sub: 'Technical indicators + AI Index' },
  { value: '3y', label: 'Training data', sub: 'Daily OHLCV from Yahoo Finance' },
]

const PIPELINE_STEPS = [
  {
    num: '1',
    icon: '📡',
    title: 'Fetch live market data',
    tag: 'yfinance — no API key needed',
    tagColor: '#22c55e',
    desc: 'Every prediction starts by pulling the last 120 days of real OHLCV data from Yahoo Finance. Nothing is cached — the model always sees today\'s market.',
  },
  {
    num: '2',
    icon: '⚙️',
    title: 'Compute 17 features',
    tag: 'RSI · MACD · Bollinger Bands · AI Index',
    tagColor: '#3b82f6',
    desc: 'Raw prices are turned into 17 meaningful signals: momentum, trend, volatility, volume anomalies, and the custom AI Intensity Index that detects algorithmic trading dominance.',
  },
  {
    num: '3',
    icon: '🧠',
    title: 'Run LightGBM prediction',
    tag: '300 trees · probability calibrated',
    tagColor: '#a855f7',
    desc: 'A gradient boosting classifier outputs calibrated probabilities for BUY, SELL, and HOLD. Trained with TimeSeriesSplit to ensure no future data leaks into training.',
  },
  {
    num: '4',
    icon: '🔍',
    title: 'Explain with SHAP',
    tag: 'TreeExplainer · computed per prediction',
    tagColor: '#f59e0b',
    desc: 'SHAP values break open the model and show exactly which features drove this specific prediction — not an average, but a fresh explanation every time.',
  },
]

const ML_METHODS = [
  {
    name: 'LightGBM Classifier',
    badge: 'Core model',
    color: '#22c55e',
    desc: 'Gradient boosted decision trees — the algorithm behind many Kaggle championship solutions and real quant systems. Fast, handles class imbalance, works well on tabular financial data.',
    why: 'Class-weighted training ensures SELL signals aren\'t drowned out by the more common HOLD labels in the training set.',
  },
  {
    name: 'Probability Calibration',
    badge: 'Signal quality',
    color: '#3b82f6',
    desc: 'Raw gradient boosting probabilities are often overconfident (outputting 0.99 when the true probability is closer to 0.7). Isotonic regression calibration fixes this.',
    why: 'Confidence scores you see in the dashboard are real probabilities, not inflated softmax outputs. 65% means 65%.',
  },
  {
    name: 'AI Intensity Index',
    badge: 'Original feature',
    color: '#a855f7',
    desc: 'A custom composite signal that detects when algorithmic trading is dominating price action — built from rolling percentile ranks of volatility, volume anomaly, MACD divergence, and Bollinger Band width.',
    why: 'High AI regime = more consistent, momentum-driven patterns. The model performs differently in these regimes, so knowing the regime improves accuracy.',
  },
  {
    name: 'TimeSeriesSplit CV',
    badge: 'Prevents data leakage',
    color: '#f59e0b',
    desc: 'Standard k-fold cross-validation randomly shuffles data, accidentally training on future prices. TimeSeriesSplit always trains on the past and validates on the future.',
    why: 'The accuracy numbers in the Model Card are honest. No look-ahead bias, no inflated metrics.',
  },
]

const FEATURES = [
  { name: 'RSI (14)', full: 'Relative Strength Index', range: '0–100', color: '#22c55e', insight: 'Below 30 → potential oversold bounce. Above 70 → potential pullback incoming.' },
  { name: 'MACD Diff', full: 'MACD Histogram divergence', range: 'Unbounded', color: '#3b82f6', insight: 'Positive = upward momentum building. Negative = downward momentum building.' },
  { name: 'BB Width', full: 'Bollinger Band Width', range: '0 – 1', color: '#a855f7', insight: 'Narrow band (squeeze) → breakout likely coming in either direction.' },
  { name: 'Volume Z-Score', full: '20-day volume deviation', range: '−3 to +3', color: '#f59e0b', insight: 'High positive = unusual institutional activity. Often precedes a directional move.' },
  { name: 'AI Intensity', full: 'Algorithmic trading intensity', range: '0 – 1', color: '#ec4899', insight: 'Above its own rolling mean = algorithmic regime. Patterns are more predictable.' },
  { name: '10d Volatility', full: 'Annualized rolling volatility', range: '0 – 1', color: '#14b8a6', insight: 'High = uncertain, noisy market. Low = calm trending conditions.' },
]

const DASHBOARD_PANELS = [
  { icon: '🎯', title: 'Prediction Signal', color: '#22c55e', desc: 'BUY / SELL / HOLD — the model\'s directional call, with color-coding. Shows the class with the highest calibrated probability.', tag: 'LightGBM output' },
  { icon: '📊', title: 'Probability Bars', color: '#3b82f6', desc: 'The full probability distribution — all three classes at once. Knowing the margin (e.g. 58% vs 57%) tells you how confident the model actually is.', tag: 'Calibrated probabilities' },
  { icon: '⚡', title: 'AI Regime Indicator', color: '#a855f7', desc: 'Is the market currently in an algorithmic-dominated regime? This affects how the model interprets momentum signals.', tag: 'Custom feature' },
  { icon: '📉', title: 'SHAP Feature Chart', color: '#f59e0b', desc: 'A bar chart showing which features pushed the prediction toward BUY or SELL for this specific ticker and moment — not a global average.', tag: 'TreeExplainer' },
  { icon: '📅', title: 'Horizon Toggle', color: '#14b8a6', desc: 'Switch between 1-day, 3-day, and 5-day forecasts. Each is a completely separate trained model — not the same model scaled.', tag: '3 independent models' },
  { icon: '💬', title: 'GPT-4o Commentary', color: '#ec4899', desc: 'If you have an OpenAI key configured, GPT-4o writes a 2-sentence plain-English analyst note citing the regime and top SHAP driver.', tag: 'Optional' },
  { icon: '📰', title: 'News Sentiment', color: '#f97316', desc: 'Fetches recent headlines via NewsAPI and shows a live sentiment bar from bearish to bullish. Activate with NEWSAPI_KEY.', tag: 'Optional' },
  { icon: '📣', title: 'Reddit Mentions', color: '#ef4444', desc: 'Tracks 24-hour mention volume on r/wallstreetbets and r/investing. Crowd sentiment often diverges from the model signal interestingly.', tag: 'Optional' },
]

const OPTIONAL_APIS = [
  { icon: '💬', title: 'GPT-4o Commentary', color: '#ec4899', key: 'OPENAI_API_KEY', link: 'https://platform.openai.com/api-keys', desc: 'Plain-English 2-sentence analyst note written by GPT-4o for each prediction, citing regime and top SHAP feature.' },
  { icon: '📰', title: 'News Sentiment', color: '#f97316', key: 'NEWSAPI_KEY', link: 'https://newsapi.org/register', desc: 'Live headline sentiment bar. Fetches last 10 articles and scores positive vs negative language.' },
  { icon: '📣', title: 'Reddit Mentions', color: '#ef4444', key: 'REDDIT_CLIENT_ID', link: 'https://www.reddit.com/prefs/apps', desc: '24-hour mention volume and sentiment from r/wallstreetbets and r/investing via PRAW.' },
  { icon: '📈', title: 'Analyst Data', color: '#14b8a6', key: 'ALPHA_VANTAGE_KEY', link: 'https://www.alphavantage.co/support/#api-key', desc: 'Wall Street consensus rating, 12-month price target, and next earnings date from Alpha Vantage free tier.' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{ backgroundColor: '#0b0f1a', color: '#e2e8f0', fontFamily: '"Inter", system-ui, -apple-system, sans-serif', scrollBehavior: 'smooth' }}>

      {/* ── STICKY NAV ── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: 'rgba(11, 15, 26, 0.92)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        padding: '0 32px', height: 56,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', display: 'inline-block', boxShadow: '0 0 6px #22c55e80' }} />
          <span style={{ fontWeight: 700, fontSize: 14, color: '#f1f5f9' }}>Market Regime</span>
          <span style={{ fontSize: 12, color: '#475569', marginLeft: 4 }}>by Ankit Paudel</span>
        </div>

        <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
          {NAV_LINKS.map(({ label, id }) => (
            <button
              key={id}
              onClick={() => scrollTo(id)}
              style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 13, fontWeight: 500, cursor: 'pointer', padding: '6px 12px', borderRadius: 8, transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#e2e8f0')}
              onMouseLeave={e => (e.currentTarget.style.color = '#64748b')}
            >
              {label}
            </button>
          ))}
          <div style={{ width: 1, height: 20, background: '#1e293b', margin: '0 8px' }} />
          <button
            onClick={() => navigate('/dashboard')}
            style={{ background: '#2563eb', border: 'none', color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', padding: '7px 16px', borderRadius: 8 }}
          >
            Open Dashboard
          </button>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '100px 24px 80px', position: 'relative', overflow: 'hidden' }}>
        {/* Soft background glow */}
        <div style={{ position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%, -50%)', width: 700, height: 700, background: 'radial-gradient(circle, rgba(37,99,235,0.07) 0%, transparent 65%)', pointerEvents: 'none' }} />

        {/* Author badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '5px 14px', borderRadius: 999, background: 'rgba(37,99,235,0.08)', border: '1px solid rgba(37,99,235,0.2)', color: '#93c5fd', fontSize: 12, fontWeight: 500, marginBottom: 28 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
          Ankit Paudel · CS 4771 Machine Learning · University of Idaho
        </div>

        <h1 style={{ fontSize: 'clamp(32px, 6vw, 72px)', fontWeight: 800, lineHeight: 1.08, letterSpacing: '-0.025em', marginBottom: 20, maxWidth: 820 }}>
          Predict stock direction{' '}
          <span style={{ color: '#93c5fd' }}>by detecting</span>
          <br />
          <span style={{ background: 'linear-gradient(135deg, #3b82f6 30%, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            algorithmic market regimes
          </span>
        </h1>

        <p style={{ fontSize: 17, color: '#94a3b8', maxWidth: 580, lineHeight: 1.75, marginBottom: 12 }}>
          A full-stack ML system that identifies when AI traders are dominating the market — 
          and uses that regime signal to predict <strong style={{ color: '#e2e8f0', fontWeight: 600 }}>BUY / SELL / HOLD</strong> for
          AAPL, GOOGL, MSFT, TSLA, and NVDA.
        </p>
        <p style={{ fontSize: 13, color: '#334155', marginBottom: 40 }}>
          LightGBM · SHAP explainability · FastAPI backend · React dashboard · Deployed live
        </p>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center', marginBottom: 60 }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{ padding: '13px 28px', borderRadius: 10, background: '#2563eb', border: 'none', color: '#fff', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 4px 20px rgba(37,99,235,0.35)' }}
          >
            Open Live Dashboard →
          </button>
          <a
            href="https://github.com/AankitPaudel/market-regime-detection"
            target="_blank"
            rel="noopener noreferrer"
            style={{ padding: '13px 28px', borderRadius: 10, background: 'transparent', border: '1px solid #1e293b', color: '#64748b', fontWeight: 500, fontSize: 15, textDecoration: 'none' }}
          >
            View on GitHub ↗
          </a>
          <button
            onClick={() => scrollTo('how-it-works')}
            style={{ padding: '13px 20px', borderRadius: 10, background: 'transparent', border: '1px solid #1e293b', color: '#64748b', fontWeight: 500, fontSize: 15, cursor: 'pointer' }}
          >
            Learn how it works ↓
          </button>
        </div>

        {/* Stat row */}
        <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap', justifyContent: 'center' }}>
          {STATS.map(({ value, label, sub }) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <p style={{ fontSize: 30, fontWeight: 800, color: '#f1f5f9', fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>{value}</p>
              <p style={{ fontSize: 12, color: '#475569', marginTop: 4, fontWeight: 600 }}>{label}</p>
              <p style={{ fontSize: 11, color: '#334155', marginTop: 2 }}>{sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── THE PROBLEM ── */}
      <section style={{ padding: '100px 24px', background: '#080c17' }}>
        <div style={{ maxWidth: 860, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
          <div>
            <p style={{ fontSize: 11, fontWeight: 700, color: '#3b82f6', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 16 }}>Why this project exists</p>
            <h2 style={{ fontSize: 'clamp(22px, 2.5vw, 34px)', fontWeight: 700, lineHeight: 1.25, marginBottom: 20, color: '#f1f5f9' }}>
              Traditional indicators weren't designed for algorithmic markets
            </h2>
            <p style={{ color: '#64748b', lineHeight: 1.85, marginBottom: 16, fontSize: 15 }}>
              Over 70% of US equity volume now comes from algorithmic and high-frequency traders. When algorithms dominate, price patterns change — momentum amplifies faster, mean reversion tightens, and volume spikes carry different meaning.
            </p>
            <p style={{ color: '#64748b', lineHeight: 1.85, fontSize: 15 }}>
              This system detects <em style={{ color: '#94a3b8', fontStyle: 'normal', fontWeight: 500 }}>when</em> you're in a high-algorithm regime and bakes that detection directly into the prediction as a feature — giving the model context that standard RSI and MACD can't see.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {[
              { pct: '70%', label: 'of US equity volume is algorithmic', color: '#ef4444' },
              { pct: '15', label: 'separate models trained (5 × 3)', color: '#3b82f6' },
              { pct: '17', label: 'engineered features per prediction', color: '#a855f7' },
              { pct: '0', label: 'API keys required to run', color: '#22c55e' },
            ].map(({ pct, label, color }) => (
              <div key={label} style={{ background: '#0d1120', border: '1px solid #1e293b', borderRadius: 14, padding: '20px 18px' }}>
                <p style={{ fontSize: 32, fontWeight: 800, color, fontVariantNumeric: 'tabular-nums', lineHeight: 1, marginBottom: 8 }}>{pct}</p>
                <p style={{ fontSize: 12, color: '#475569', lineHeight: 1.5 }}>{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" style={{ padding: '100px 24px' }}>
        <div style={{ maxWidth: 820, margin: '0 auto' }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#3b82f6', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 14, textAlign: 'center' }}>How it works</p>
          <h2 style={{ fontSize: 'clamp(22px, 3vw, 38px)', fontWeight: 700, textAlign: 'center', marginBottom: 10, color: '#f1f5f9' }}>
            From raw prices to explained prediction — in 4 steps
          </h2>
          <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 64, fontSize: 15 }}>
            Every time you click Predict, all four stages run live. Nothing is pre-computed.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {PIPELINE_STEPS.map(({ num, icon, title, tag, tagColor, desc }, i) => (
              <div key={num} style={{ display: 'grid', gridTemplateColumns: '60px 1fr', position: 'relative' }}>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div style={{ position: 'absolute', left: 29, top: 56, bottom: -4, width: 2, background: 'linear-gradient(to bottom, #1e293b, transparent)' }} />
                )}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 18 }}>
                  <div style={{ width: 38, height: 38, borderRadius: '50%', background: '#0d1120', border: '1.5px solid #1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 17 }}>
                    {icon}
                  </div>
                </div>
                <div style={{ background: '#0d1120', border: '1px solid #1e293b', borderRadius: 14, padding: '20px 24px', marginBottom: 6 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: 11, color: '#334155', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>STEP {num}</span>
                    <span style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9' }}>{title}</span>
                    <span style={{ fontSize: 11, color: tagColor, background: `${tagColor}12`, padding: '2px 10px', borderRadius: 999, border: `1px solid ${tagColor}25`, fontWeight: 600, marginLeft: 'auto' }}>
                      {tag}
                    </span>
                  </div>
                  <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.75 }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ML METHODS ── */}
      <section id="ml-methods" style={{ padding: '100px 24px', background: '#080c17' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#3b82f6', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 14, textAlign: 'center' }}>Machine learning methods</p>
          <h2 style={{ fontSize: 'clamp(22px, 3vw, 38px)', fontWeight: 700, textAlign: 'center', marginBottom: 10, color: '#f1f5f9' }}>
            Four techniques that work together
          </h2>
          <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 64, fontSize: 15 }}>
            Each one solves a specific problem in financial machine learning. Here's what each does and why it's here.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 14 }}>
            {ML_METHODS.map(({ name, badge, color, desc, why }) => (
              <div key={name} style={{ background: '#0d1120', border: '1px solid #1e293b', borderRadius: 16, padding: 26, display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                  <h3 style={{ fontSize: 17, fontWeight: 700, color: '#f1f5f9', margin: 0 }}>{name}</h3>
                  <span style={{ fontSize: 11, fontWeight: 600, padding: '3px 10px', borderRadius: 999, color, background: `${color}12`, border: `1px solid ${color}25`, whiteSpace: 'nowrap' }}>
                    {badge}
                  </span>
                </div>
                <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.75, flex: 1 }}>{desc}</p>
                <div style={{ background: '#070b16', borderRadius: 10, padding: '12px 14px', borderLeft: `3px solid ${color}` }}>
                  <p style={{ fontSize: 11, color: '#334155', fontWeight: 700, marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Why this matters</p>
                  <p style={{ fontSize: 13, color: '#475569', lineHeight: 1.65 }}>{why}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section id="features" style={{ padding: '100px 24px' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#3b82f6', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 14, textAlign: 'center' }}>Input features</p>
          <h2 style={{ fontSize: 'clamp(22px, 3vw, 38px)', fontWeight: 700, textAlign: 'center', marginBottom: 10, color: '#f1f5f9' }}>
            What the model actually looks at
          </h2>
          <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 56, fontSize: 15 }}>
            The SHAP chart in the dashboard references these. Here's what each feature means in plain English.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
            {FEATURES.map(({ name, full, range, color, insight }) => (
              <div key={name} style={{ background: '#0d1120', border: '1px solid #1e293b', borderRadius: 14, padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
                  <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: 14, color: '#e2e8f0' }}>{name}</span>
                </div>
                <p style={{ fontSize: 13, color: '#475569', marginBottom: 4 }}>{full}</p>
                <p style={{ fontSize: 11, color: '#334155', marginBottom: 12 }}>Range: {range}</p>
                <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.65, borderTop: '1px solid #1e293b', paddingTop: 12 }}>{insight}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── DASHBOARD GUIDE ── */}
      <section id="dashboard-guide" style={{ padding: '100px 24px', background: '#080c17' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#3b82f6', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 14, textAlign: 'center' }}>Dashboard guide</p>
          <h2 style={{ fontSize: 'clamp(22px, 3vw, 38px)', fontWeight: 700, textAlign: 'center', marginBottom: 10, color: '#f1f5f9' }}>
            Every panel explained
          </h2>
          <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 56, fontSize: 15 }}>
            The dashboard is dense — here's a quick guide to what each section shows.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
            {DASHBOARD_PANELS.map(({ icon, title, color, desc, tag }) => (
              <div key={title} style={{ background: '#0d1120', border: '1px solid #1e293b', borderRadius: 14, padding: 22 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                  <span style={{ fontSize: 24 }}>{icon}</span>
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 999, background: `${color}12`, color, border: `1px solid ${color}25`, fontWeight: 600 }}>
                    {tag}
                  </span>
                </div>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9', marginBottom: 8 }}>{title}</h3>
                <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.7 }}>{desc}</p>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 32, textAlign: 'center' }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{ padding: '13px 28px', borderRadius: 10, background: '#2563eb', border: 'none', color: '#fff', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 4px 20px rgba(37,99,235,0.3)' }}
            >
              Open the Dashboard →
            </button>
          </div>
        </div>
      </section>

      {/* ── OPTIONAL APIS ── */}
      <section id="optional-apis" style={{ padding: '100px 24px' }}>
        <div style={{ maxWidth: 860, margin: '0 auto' }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#3b82f6', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 14, textAlign: 'center' }}>Optional APIs</p>
          <h2 style={{ fontSize: 'clamp(22px, 3vw, 38px)', fontWeight: 700, textAlign: 'center', marginBottom: 10, color: '#f1f5f9' }}>
            Four bonus features — all off by default
          </h2>
          <p style={{ color: '#64748b', textAlign: 'center', marginBottom: 16, fontSize: 15, maxWidth: 560, margin: '0 auto 16px' }}>
            The core prediction runs with zero API keys. These features activate individually once you add the key to your <code style={{ color: '#94a3b8', background: '#0d1120', padding: '1px 7px', borderRadius: 5, fontSize: 13 }}>backend/.env</code>.
          </p>
          <p style={{ color: '#475569', textAlign: 'center', fontSize: 13, marginBottom: 56 }}>
            All free-tier. None required.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 14 }}>
            {OPTIONAL_APIS.map(({ icon, title, color, key, link, desc }) => (
              <div key={title} style={{ background: '#0d1120', border: '1px solid #1e293b', borderRadius: 16, padding: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <span style={{ fontSize: 22 }}>{icon}</span>
                  <h3 style={{ fontSize: 16, fontWeight: 700, color: '#f1f5f9', margin: 0 }}>{title}</h3>
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 999, color, background: `${color}12`, border: `1px solid ${color}25`, fontWeight: 600, marginLeft: 'auto' }}>
                    Optional
                  </span>
                </div>
                <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.75, marginBottom: 14 }}>{desc}</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#070b16', borderRadius: 8, padding: '10px 14px' }}>
                  <code style={{ fontSize: 12, color: '#475569' }}>{key}</code>
                  <a href={link} target="_blank" rel="noopener noreferrer"
                    style={{ fontSize: 12, color: '#3b82f6', textDecoration: 'none', fontWeight: 600 }}>
                    Get free key →
                  </a>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 24, background: '#0d1120', border: '1px solid #1e293b', borderRadius: 12, padding: '18px 22px', display: 'flex', gap: 14, alignItems: 'flex-start' }}>
            <span style={{ fontSize: 18, flexShrink: 0 }}>🔑</span>
            <p style={{ fontSize: 13, color: '#475569', lineHeight: 1.75 }}>
              <strong style={{ color: '#64748b', fontWeight: 600 }}>To enable:</strong> copy <code style={{ color: '#94a3b8', background: '#070b16', padding: '1px 6px', borderRadius: 4 }}>backend/.env.example</code> to <code style={{ color: '#94a3b8', background: '#070b16', padding: '1px 6px', borderRadius: 4 }}>backend/.env</code>, fill in whichever keys you have, restart the server.
              If deployed on Render, add keys in the <strong style={{ color: '#64748b', fontWeight: 600 }}>Environment</strong> tab of your service dashboard.
            </p>
          </div>
        </div>
      </section>

      {/* ── FINAL CTA ── */}
      <section style={{ padding: '100px 24px', background: '#080c17', textAlign: 'center' }}>
        <div style={{ maxWidth: 560, margin: '0 auto' }}>
          <h2 style={{ fontSize: 'clamp(26px, 4vw, 44px)', fontWeight: 700, lineHeight: 1.15, marginBottom: 18, color: '#f1f5f9' }}>
            Try it on live market data
          </h2>
          <p style={{ color: '#64748b', fontSize: 16, lineHeight: 1.75, marginBottom: 36 }}>
            Pick a ticker, choose a horizon, hit Predict. Live data flows through all four pipeline stages in under 5 seconds.
          </p>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{ padding: '14px 32px', borderRadius: 10, background: '#2563eb', border: 'none', color: '#fff', fontWeight: 600, fontSize: 16, cursor: 'pointer', boxShadow: '0 4px 24px rgba(37,99,235,0.35)' }}
            >
              Open Dashboard →
            </button>
            <a
              href="https://github.com/AankitPaudel/market-regime-detection"
              target="_blank"
              rel="noopener noreferrer"
              style={{ padding: '14px 24px', borderRadius: 10, background: 'transparent', border: '1px solid #1e293b', color: '#475569', fontWeight: 500, fontSize: 15, textDecoration: 'none', display: 'flex', alignItems: 'center' }}
            >
              GitHub ↗
            </a>
          </div>
        </div>
      </section>

      {/* ── TECH STACK ── */}
      <section style={{ padding: '60px 24px', maxWidth: 760, margin: '0 auto', textAlign: 'center' }}>
        <p style={{ fontSize: 11, color: '#1e293b', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 18 }}>Full stack</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
          {[
            'Python', 'LightGBM', 'scikit-learn', 'SHAP', 'pandas', 'numpy', 'ta', 'yfinance',
            'FastAPI', 'uvicorn', 'React', 'TypeScript', 'Vite', 'Recharts',
            'Render', 'Vercel', 'GPT-4o (optional)',
          ].map((t) => (
            <span key={t} style={{ fontSize: 12, padding: '5px 12px', borderRadius: 999, border: '1px solid #1e293b', color: '#334155', background: '#0d1120' }}>
              {t}
            </span>
          ))}
        </div>
      </section>

      {/* ── FOOTER ── */}
      <div style={{ borderTop: '1px solid #0f172a', padding: '28px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, maxWidth: 940, margin: '0 auto' }}>
        <p style={{ fontSize: 12, color: '#1e293b' }}>
          Built by{' '}
          <a href="https://github.com/AankitPaudel/market-regime-detection" target="_blank" rel="noopener noreferrer" style={{ color: '#334155', textDecoration: 'none', fontWeight: 600 }}>
            Ankit Paudel
          </a>
          {' '}· University of Idaho · CS 4771 Machine Learning
        </p>
        <p style={{ fontSize: 12, color: '#1e293b' }}>
          ⚠️ Research project only — not financial advice.
        </p>
      </div>
    </div>
  )
}
