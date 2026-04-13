import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ShapValue { feature: string; shap_value: number }

const FEATURE_LABELS: Record<string, string> = {
  return_1d:      '1-day return',
  return_5d:      '5-day return',
  volatility_10d: '10d volatility',
  volatility_20d: '20d volatility',
  rsi:            'RSI (14)',
  macd:           'MACD line',
  macd_signal:    'MACD signal',
  macd_diff:      'MACD diff',
  bb_upper:       'BB upper band',
  bb_lower:       'BB lower band',
  bb_width:       'BB width',
  bb_pct:         'BB % position',
  volume_zscore:  'Volume z-score',
  gap:            'Opening gap',
  range:          'Daily range',
  ai_index:       'AI intensity',
  ai_regime:      'AI regime flag',
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: { payload: ShapValue }[] }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const isPos = d.shap_value > 0
  return (
    <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 10, padding: '12px 16px', minWidth: 220 }}>
      <p style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>{FEATURE_LABELS[d.feature] || d.feature}</p>
      <p style={{ fontSize: 12, color: isPos ? '#22c55e' : '#ef4444', fontFamily: 'monospace' }}>
        {isPos ? '+' : ''}{d.shap_value.toFixed(5)}
      </p>
      <p style={{ fontSize: 11, color: '#6b7280', marginTop: 6 }}>
        {isPos ? '↑ Pushed toward the predicted signal' : '↓ Pushed against the predicted signal'}
      </p>
    </div>
  )
}

export default function ShapChart({ shapValues }: { shapValues: ShapValue[] }) {
  const data = [...shapValues]
    .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
    .map(d => ({ ...d, displayName: FEATURE_LABELS[d.feature] || d.feature }))

  const maxAbs = Math.max(...data.map(d => Math.abs(d.shap_value)))

  return (
    <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 20, padding: 28, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <p style={{ fontSize: 11, color: '#4b5563', fontWeight: 700, letterSpacing: '0.1em', marginBottom: 6 }}>SHAP FEATURE IMPORTANCE</p>
        <p style={{ fontSize: 13, color: '#6b7280' }}>Why the model made this specific prediction</p>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
          <XAxis
            type="number"
            domain={[-maxAbs * 1.1, maxAbs * 1.1]}
            tick={{ fill: '#374151', fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: '#1f2937' }}
          />
          <YAxis
            dataKey="displayName"
            type="category"
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            width={100}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
          <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.shap_value > 0 ? '#22c55e' : '#ef4444'} opacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div style={{ display: 'flex', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 10, height: 10, borderRadius: 2, background: '#22c55e' }} />
          <span style={{ fontSize: 11, color: '#6b7280' }}>Supports the signal</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 10, height: 10, borderRadius: 2, background: '#ef4444' }} />
          <span style={{ fontSize: 11, color: '#6b7280' }}>Works against the signal</span>
        </div>
      </div>

      <div style={{ background: '#070710', borderRadius: 10, padding: '12px 14px', borderLeft: '3px solid #3b82f6' }}>
        <p style={{ fontSize: 12, color: '#6b7280', lineHeight: 1.6 }}>
          SHAP values measure each feature's contribution to this specific prediction using Shapley values from cooperative game theory. The top feature here is the biggest driver of the model's output.
        </p>
      </div>
    </div>
  )
}
