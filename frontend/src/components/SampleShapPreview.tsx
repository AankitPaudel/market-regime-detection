import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

/** Static sample so visitors always see the same chart style as a live SHAP run. */
const SAMPLE = [
  { feature: 'rsi', shap_value: 0.32, displayName: 'RSI (14)' },
  { feature: 'macd_diff', shap_value: -0.21, displayName: 'MACD diff' },
  { feature: 'ai_index', shap_value: 0.18, displayName: 'AI intensity' },
  { feature: 'volatility_10d', shap_value: -0.12, displayName: '10d volatility' },
  { feature: 'volume_zscore', shap_value: 0.09, displayName: 'Volume z-score' },
]

export default function SampleShapPreview() {
  const maxAbs = Math.max(...SAMPLE.map(d => Math.abs(d.shap_value)))
  return (
    <div style={{ background: '#0d0d1a', border: '1px dashed #334155', borderRadius: 20, padding: 24, opacity: 0.92 }}>
      <div style={{ marginBottom: 12 }}>
        <p style={{ fontSize: 11, color: '#6366f1', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 4 }}>EXAMPLE CHART</p>
        <p style={{ fontSize: 13, color: '#9ca3af', lineHeight: 1.5 }}>
          This is what the <strong style={{ color: '#e5e7eb' }}>SHAP</strong> panel looks like after a successful Predict — horizontal bars, green pushes the signal, red works against it.
          Your first request may take up to ~90s while the Render backend wakes from sleep (free tier).
        </p>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={SAMPLE} layout="vertical" margin={{ left: 4, right: 12, top: 4, bottom: 4 }}>
          <XAxis type="number" domain={[-maxAbs * 1.2, maxAbs * 1.2]} tick={{ fill: '#374151', fontSize: 10 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
          <YAxis dataKey="displayName" type="category" tick={{ fill: '#6b7280', fontSize: 11 }} width={100} tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{ background: '#0a0a14', border: '1px solid #1f2937', borderRadius: 8, fontSize: 12 }}
            formatter={(v: number) => [v.toFixed(3), 'SHAP']}
          />
          <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
            {SAMPLE.map((e, i) => (
              <Cell key={i} fill={e.shap_value > 0 ? '#22c55e' : '#ef4444'} opacity={0.55} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
