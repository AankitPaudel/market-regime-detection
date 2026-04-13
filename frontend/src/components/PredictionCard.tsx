import { Prediction } from '../lib/api'

const LABEL_STYLES: Record<string, string> = {
  BUY:  'text-green-400 bg-green-400/10 border-green-400/30',
  SELL: 'text-red-400 bg-red-400/10 border-red-400/30',
  HOLD: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
}

const BAR_COLORS: Record<string, string> = {
  BUY:  'bg-green-500',
  SELL: 'bg-red-500',
  HOLD: 'bg-yellow-500',
}

interface Props {
  prediction: Prediction
}

export default function PredictionCard({ prediction }: Props) {
  const { ticker, horizon, prediction: pred, features } = prediction

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-gray-500 text-xs mb-1">{horizon}-day prediction</p>
          <h2 className="text-3xl font-mono font-black">{ticker}</h2>
        </div>
        <span className={`px-4 py-2 rounded-xl border text-xl font-black ${LABEL_STYLES[pred.label]}`}>
          {pred.label}
        </span>
      </div>

      <p className="text-gray-400 text-xs mb-3">
        Model confidence:{' '}
        <span className="text-white font-bold">{(pred.confidence * 100).toFixed(1)}%</span>
      </p>

      <div className="space-y-2 mb-6">
        {(['BUY', 'HOLD', 'SELL'] as const).map((l) => (
          <div key={l} className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-8">{l}</span>
            <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${BAR_COLORS[l]}`}
                style={{ width: `${pred.probabilities[l] * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-400 w-10 text-right">
              {(pred.probabilities[l] * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-800/60 rounded-xl p-3">
          <p className="text-gray-500 text-xs mb-1">RSI (14)</p>
          <p className={`font-mono font-bold text-lg ${
            features.rsi < 30 ? 'text-green-400' : features.rsi > 70 ? 'text-red-400' : 'text-white'
          }`}>
            {features.rsi}
          </p>
        </div>
        <div className="bg-gray-800/60 rounded-xl p-3">
          <p className="text-gray-500 text-xs mb-1">AI Intensity</p>
          <p className="font-mono font-bold text-lg text-blue-400">
            {(features.ai_index * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-gray-800/60 rounded-xl p-3">
          <p className="text-gray-500 text-xs mb-1">AI Regime</p>
          <p className={`font-bold ${features.ai_regime === 1 ? 'text-blue-400' : 'text-gray-500'}`}>
            {features.ai_regime === 1 ? '⚡ High' : '— Low'}
          </p>
        </div>
        <div className="bg-gray-800/60 rounded-xl p-3">
          <p className="text-gray-500 text-xs mb-1">10d Volatility</p>
          <p className="font-mono font-bold text-lg text-white">
            {(features.volatility_10d * 100).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}
