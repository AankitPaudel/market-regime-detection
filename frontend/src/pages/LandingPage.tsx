import { useNavigate } from 'react-router-dom'

const TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']

const HOW_IT_WORKS = [
  {
    icon: '📡',
    title: 'Live Data',
    desc: 'yfinance pulls 120 days of OHLCV price data on every request — always current, no stale cache.',
  },
  {
    icon: '🧠',
    title: 'Regime Detection',
    desc: 'Rolling rank + PCA builds an AI Intensity Index measuring algorithmic trading dominance in the market.',
  },
  {
    icon: '📊',
    title: 'Prediction',
    desc: 'LightGBM with meta-labeling gate outputs BUY / SELL / HOLD with full confidence probability breakdown.',
  },
]

const TECH_STACK = [
  'LightGBM', 'XGBoost', 'scikit-learn', 'SHAP',
  'FastAPI', 'React', 'TypeScript', 'Tailwind',
  'yfinance', 'GPT-4o',
]

const DASHBOARD_FEATURES = [
  { label: 'Prediction Signal', desc: 'BUY / SELL / HOLD with confidence score' },
  { label: 'Probability Bars', desc: '3-class probability breakdown per prediction' },
  { label: 'AI Intensity Index', desc: 'Regime gauge measuring algorithmic activity' },
  { label: 'SHAP Chart', desc: 'Feature importance explaining each prediction' },
  { label: 'Horizon Toggle', desc: '1 / 3 / 5 day prediction windows' },
  { label: 'GPT-4o Commentary', desc: 'Plain-English analyst summary (optional)' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#0a0a0f', color: '#fff' }}>

      {/* ── SECTION 1: HERO ── */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-28 relative overflow-hidden">
        {/* subtle grid bg */}
        <div
          className="absolute inset-0 opacity-5 pointer-events-none"
          style={{
            backgroundImage: 'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />

        {/* pill badge */}
        <span className="mb-6 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide border"
          style={{ borderColor: '#3b82f620', backgroundColor: '#3b82f610', color: '#93c5fd' }}>
          CS 4771 &nbsp;·&nbsp; University of Idaho &nbsp;·&nbsp; Ankit Paudel
        </span>

        <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-5 leading-tight">
          AI Market{' '}
          <span style={{ color: '#3b82f6' }}>Regime</span>{' '}
          Detection
        </h1>

        <p className="max-w-2xl text-lg text-gray-400 mb-10 leading-relaxed">
          Predicting equity direction using{' '}
          <span className="text-white font-semibold">LightGBM</span> + meta-labeling +{' '}
          <span className="text-white font-semibold">AI Intensity Index</span>
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-12">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-8 py-3.5 rounded-xl font-bold text-sm transition-all hover:scale-105 active:scale-95"
            style={{ backgroundColor: '#3b82f6', color: '#fff', boxShadow: '0 0 30px #3b82f640' }}
          >
            Open Dashboard →
          </button>
          <a
            href="https://github.com/paudelAnkit"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3.5 rounded-xl font-bold text-sm border transition-all hover:scale-105 active:scale-95"
            style={{ borderColor: '#374151', color: '#9ca3af', backgroundColor: 'transparent' }}
          >
            View on GitHub ↗
          </a>
        </div>

        {/* Ticker row */}
        <div className="flex gap-6 font-mono text-sm tracking-widest" style={{ color: '#4b5563' }}>
          {TICKERS.map((t, i) => (
            <span key={t}>
              {t}
              {i < TICKERS.length - 1 && <span className="ml-6" style={{ color: '#1f2937' }}>·</span>}
            </span>
          ))}
        </div>
      </section>

      {/* ── SECTION 2: HOW IT WORKS ── */}
      <section className="px-6 py-20 max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-3">How It Works</h2>
        <p className="text-center text-gray-500 text-sm mb-12">Three-stage pipeline from raw price data to actionable signal</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {HOW_IT_WORKS.map(({ icon, title, desc }) => (
            <div
              key={title}
              className="rounded-2xl p-6 border transition-all hover:border-blue-800/60"
              style={{ backgroundColor: '#0f0f1a', borderColor: '#1f2937' }}
            >
              <div className="text-4xl mb-4">{icon}</div>
              <h3 className="font-bold text-base mb-2">{title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#6b7280' }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── SECTION 3: DASHBOARD FEATURES ── */}
      <section className="px-6 py-20" style={{ backgroundColor: '#0d0d18' }}>
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-3">What You See in the Dashboard</h2>
          <p className="text-center text-gray-500 text-sm mb-12">Everything a recruiter needs to see ML applied end-to-end</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {DASHBOARD_FEATURES.map(({ label, desc }) => (
              <div
                key={label}
                className="rounded-xl p-5 border"
                style={{ backgroundColor: '#0a0a0f', borderColor: '#1f2937' }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#3b82f6' }} />
                  <span className="font-semibold text-sm">{label}</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: '#6b7280' }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 4: TECH STACK ── */}
      <section className="px-6 py-20 max-w-4xl mx-auto text-center">
        <h2 className="text-2xl font-bold mb-3">Tech Stack</h2>
        <p className="text-gray-500 text-sm mb-10">Production-grade tools used end-to-end</p>
        <div className="flex flex-wrap gap-3 justify-center">
          {TECH_STACK.map((tech) => (
            <span
              key={tech}
              className="px-4 py-2 rounded-full text-sm font-semibold border"
              style={{ borderColor: '#1f2937', color: '#9ca3af', backgroundColor: '#0f0f1a' }}
            >
              {tech}
            </span>
          ))}
        </div>
      </section>

      {/* ── SECTION 5: DISCLAIMER ── */}
      <section className="px-6 py-6">
        <div
          className="max-w-3xl mx-auto rounded-xl px-6 py-4 text-center text-sm border"
          style={{ backgroundColor: '#1a1200', borderColor: '#92400e40', color: '#d97706' }}
        >
          ⚠️ Research project for CS 4771 Machine Learning — University of Idaho. Not financial advice.
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="px-6 py-10 text-center text-xs" style={{ color: '#374151' }}>
        Built by{' '}
        <a
          href="https://github.com/paudelAnkit"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-gray-400 transition-colors"
        >
          Ankit Paudel
        </a>
        {' '}· University of Idaho · 2025 ·{' '}
        <a
          href="https://github.com/paudelAnkit"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-gray-400 transition-colors"
        >
          GitHub
        </a>
      </footer>
    </div>
  )
}
