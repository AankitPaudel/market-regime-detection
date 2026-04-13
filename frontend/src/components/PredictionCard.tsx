import type { Prediction } from '../lib/api'

const LABEL_META: Record<string, { color: string; bg: string; border: string; desc: string }> = {
  BUY:  { color: '#22c55e', bg: 'rgba(34,197,94,0.08)',  border: 'rgba(34,197,94,0.25)',  desc: 'Model expects price to rise >2% over the horizon' },
  SELL: { color: '#ef4444', bg: 'rgba(239,68,68,0.08)',  border: 'rgba(239,68,68,0.25)',  desc: 'Model expects price to fall >2% over the horizon' },
  HOLD: { color: '#eab308', bg: 'rgba(234,179,8,0.08)',  border: 'rgba(234,179,8,0.25)',  desc: 'Model expects price movement within ±2% — no clear signal' },
}

interface Props { prediction: Prediction }

export default function PredictionCard({ prediction }: Props) {
  const { ticker, horizon, prediction: pred } = prediction
  const meta = LABEL_META[pred.label]

  return (
    <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 20, padding: '28px', display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <p style={{ fontSize: 11, color: '#4b5563', fontWeight: 700, letterSpacing: '0.1em', marginBottom: 6 }}>PREDICTION SIGNAL</p>
          <p style={{ fontSize: 13, color: '#6b7280' }}>{ticker} · {horizon}-day horizon · LightGBM</p>
        </div>
        <div style={{ textAlign: 'right', background: meta.bg, border: `1px solid ${meta.border}`, borderRadius: 12, padding: '10px 18px' }}>
          <p style={{ fontSize: 28, fontWeight: 900, color: meta.color, fontFamily: 'monospace', lineHeight: 1 }}>{pred.label}</p>
          <p style={{ fontSize: 10, color: meta.color, opacity: 0.7, marginTop: 4 }}>{(pred.confidence * 100).toFixed(1)}% confidence</p>
        </div>
      </div>

      {/* Signal meaning */}
      <div style={{ background: '#070710', borderRadius: 10, padding: '12px 14px', borderLeft: `3px solid ${meta.color}` }}>
        <p style={{ fontSize: 12, color: '#6b7280' }}>{meta.desc}</p>
      </div>

      {/* Probability bars */}
      <div>
        <p style={{ fontSize: 11, color: '#4b5563', fontWeight: 700, letterSpacing: '0.1em', marginBottom: 12 }}>FULL PROBABILITY DISTRIBUTION</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(['BUY', 'HOLD', 'SELL'] as const).map((l) => {
            const pct = pred.probabilities[l] * 100
            const clr = l === 'BUY' ? '#22c55e' : l === 'SELL' ? '#ef4444' : '#eab308'
            const isWinner = pred.label === l
            return (
              <div key={l}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                  <span style={{ fontSize: 12, fontWeight: isWinner ? 700 : 400, color: isWinner ? clr : '#6b7280' }}>{l}</span>
                  <span style={{ fontSize: 12, fontFamily: 'monospace', color: isWinner ? clr : '#4b5563', fontWeight: isWinner ? 700 : 400 }}>{pct.toFixed(1)}%</span>
                </div>
                <div style={{ height: 6, background: '#1a1a2e', borderRadius: 999, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${pct}%`, background: clr, borderRadius: 999, transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1)', opacity: isWinner ? 1 : 0.4 }} />
                </div>
              </div>
            )
          })}
        </div>
        <p style={{ fontSize: 11, color: '#374151', marginTop: 10 }}>
          Softmax probabilities from LightGBM — sum to 100%. The highest class wins.
        </p>
      </div>
    </div>
  )
}
