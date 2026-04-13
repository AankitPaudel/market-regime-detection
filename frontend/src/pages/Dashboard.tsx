import { useState } from 'react'
import { fetchPrediction, Prediction } from '../lib/api'
import HorizonToggle from '../components/HorizonToggle'
import PredictionCard from '../components/PredictionCard'
import ShapChart from '../components/ShapChart'
import Commentary from '../components/Commentary'
import RetrainButton from '../components/RetrainButton'
import toast from 'react-hot-toast'

const TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']

export default function Dashboard() {
  const [ticker, setTicker] = useState('AAPL')
  const [horizon, setHorizon] = useState(1)
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async (t = ticker, h = horizon) => {
    setLoading(true)
    setPrediction(null)
    try {
      const data = await fetchPrediction(t, h)
      setPrediction(data)
    } catch {
      toast.error('Prediction failed. Backend may be warming up — try again in 30s.')
    } finally {
      setLoading(false)
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

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Top bar */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold">Market Regime Dashboard</h1>
          <p className="text-xs text-gray-500">
            Live predictions · Pre-trained LightGBM · SHAP explanations · Ankit Paudel
          </p>
        </div>
        <a href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
          ← Back
        </a>
      </div>

      <div className="p-6 max-w-6xl mx-auto">
        {/* Ticker selector */}
        <div className="flex flex-wrap gap-3 mb-4">
          {TICKERS.map((t) => (
            <button
              key={t}
              onClick={() => handleTickerChange(t)}
              className={`px-4 py-2 rounded-lg font-mono text-sm font-bold transition-all
                ${ticker === t
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Horizon toggle */}
        <div className="mb-6">
          <HorizonToggle value={horizon} onChange={handleHorizonChange} />
        </div>

        {/* Predict button */}
        <button
          onClick={() => handlePredict()}
          disabled={loading}
          className="mb-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50
                     rounded-xl font-semibold text-sm transition-all"
        >
          {loading ? 'Running model...' : `Predict ${ticker} — ${horizon}d horizon →`}
        </button>
        <p className="text-xs text-gray-600 mb-8">
          First request may take 30s — Render free tier cold starts
        </p>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center py-16 gap-4">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm">
              Fetching live data · Computing features · Running LightGBM
            </p>
          </div>
        )}

        {/* Results grid */}
        {prediction && !loading && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PredictionCard prediction={prediction} />
            <ShapChart shapValues={prediction.shap_values} />
            {prediction.has_commentary && (
              <div className="lg:col-span-2">
                <Commentary text={prediction.commentary} />
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {!prediction && !loading && (
          <div className="text-center py-20 text-gray-600">
            <p className="text-4xl mb-4">📊</p>
            <p>Select a ticker and click Predict to run a live prediction</p>
          </div>
        )}

        {/* Advanced retrain — hidden at bottom for technical recruiters */}
        <div className="mt-16 pt-8 border-t border-gray-800/50">
          <p className="text-xs text-gray-600 mb-3">
            ⚙️ Advanced — Retrain model live on latest yfinance data (~60s)
          </p>
          <RetrainButton ticker={ticker} horizon={horizon} />
        </div>
      </div>
    </div>
  )
}
