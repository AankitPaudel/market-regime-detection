import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchMarketSnapshot, type MarketSnapshot } from '../lib/api'

interface Props {
  ticker: string
}

export default function MarketHistoryPanel({ ticker }: Props) {
  const [data, setData] = useState<MarketSnapshot | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const ac = new AbortController()
    setLoading(true)
    setErr(null)
    setData(null)
    fetchMarketSnapshot(ticker, ac.signal)
      .then(setData)
      .catch((e: unknown) => {
        if (ac.signal.aborted) return
        const msg = e && typeof e === 'object' && 'message' in e ? String((e as Error).message) : 'Request failed'
        setErr(msg)
      })
      .finally(() => {
        if (!ac.signal.aborted) setLoading(false)
      })
    return () => ac.abort()
  }, [ticker])

  const chartData = data?.closes.map((p) => ({ ...p, label: p.d.slice(0, 7) })) ?? []

  return (
    <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 20, padding: 24 }}>
      <div style={{ marginBottom: 14 }}>
        <p style={{ fontSize: 11, color: '#22c55e', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>
          LIVE MARKET HISTORY (~4 YEARS)
        </p>
        <p style={{ fontSize: 13, color: '#9ca3af', lineHeight: 1.55 }}>
          Daily closes from <strong style={{ color: '#e5e7eb' }}>Yahoo Finance</strong> (same source as training). Updates when you change ticker. No ML models required — this loads even if Predict is slow.
        </p>
      </div>

      {loading && (
        <p style={{ fontSize: 13, color: '#4b5563' }}>Loading {ticker} history…</p>
      )}

      {!loading && err && (
        <div style={{ background: '#1a0a0a', border: '1px solid #3f1f1f', borderRadius: 12, padding: 16 }}>
          <p style={{ fontSize: 13, color: '#fca5a5', marginBottom: 8 }}>Could not load history from the API.</p>
          <p style={{ fontSize: 12, color: '#6b7280', lineHeight: 1.6 }}>
            In Vercel → Settings → Environment Variables, set <code style={{ color: '#9ca3af' }}>VITE_API_URL</code> to your Render backend URL (must start with <code style={{ color: '#9ca3af' }}>https://</code>), then redeploy the frontend.
          </p>
        </div>
      )}

      {!loading && data && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 12, marginBottom: 18 }}>
            <div style={{ background: '#070710', borderRadius: 10, padding: 12 }}>
              <p style={{ fontSize: 10, color: '#4b5563', marginBottom: 4 }}>Last close</p>
              <p style={{ fontSize: 18, fontWeight: 800, fontFamily: 'monospace', color: '#e5e7eb' }}>${data.last_close.toFixed(2)}</p>
            </div>
            <div style={{ background: '#070710', borderRadius: 10, padding: 12 }}>
              <p style={{ fontSize: 10, color: '#4b5563', marginBottom: 4 }}>4y total return</p>
              <p style={{ fontSize: 18, fontWeight: 800, fontFamily: 'monospace', color: data.total_return_pct >= 0 ? '#22c55e' : '#ef4444' }}>
                {data.total_return_pct >= 0 ? '+' : ''}{data.total_return_pct}%
              </p>
            </div>
            <div style={{ background: '#070710', borderRadius: 10, padding: 12 }}>
              <p style={{ fontSize: 10, color: '#4b5563', marginBottom: 4 }}>Ann. volatility</p>
              <p style={{ fontSize: 18, fontWeight: 800, fontFamily: 'monospace', color: '#eab308' }}>{data.annualized_volatility_pct}%</p>
            </div>
            <div style={{ background: '#070710', borderRadius: 10, padding: 12 }}>
              <p style={{ fontSize: 10, color: '#4b5563', marginBottom: 4 }}>Trading days</p>
              <p style={{ fontSize: 18, fontWeight: 800, fontFamily: 'monospace', color: '#93c5fd' }}>{data.trading_days}</p>
            </div>
          </div>
          <p style={{ fontSize: 11, color: '#374151', marginBottom: 10 }}>
            {data.history_start} → {data.history_end} · {data.source}
          </p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
              <XAxis dataKey="label" tick={{ fill: '#374151', fontSize: 9 }} interval="preserveStartEnd" tickLine={false} axisLine={{ stroke: '#1f2937' }} />
              <YAxis domain={['auto', 'auto']} tick={{ fill: '#374151', fontSize: 10 }} width={52} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
              <Tooltip
                contentStyle={{ background: '#0a0a14', border: '1px solid #1f2937', borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => [`$${v.toFixed(2)}`, 'Close']}
                labelFormatter={(_, p) => (p[0]?.payload?.d as string) || ''}
              />
              <Line type="monotone" dataKey="c" stroke="#3b82f6" strokeWidth={1.5} dot={false} name="Close" />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  )
}
