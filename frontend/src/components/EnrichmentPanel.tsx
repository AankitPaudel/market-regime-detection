interface News {
  score: number
  headline_count: number
  sample_headline: string
}

interface Reddit {
  mention_count: number
  sentiment_score: number
  top_post_title: string
}

interface AlphaVantage {
  next_earnings: string
  analyst_target: number | null
  analyst_rating: string
}

interface Enrichments {
  news: News | null
  reddit: Reddit | null
  alpha_vantage: AlphaVantage | null
}

interface Props {
  enrichments: Enrichments
}

function SentimentBar({ score }: { score: number }) {
  const pct = Math.round((score + 1) * 50) // map -1..1 to 0..100
  const color = score > 0.1 ? '#22c55e' : score < -0.1 ? '#ef4444' : '#eab308'
  const label = score > 0.1 ? 'Positive' : score < -0.1 ? 'Negative' : 'Neutral'
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 11, color: '#6b7280' }}>Sentiment</span>
        <span style={{ fontSize: 11, fontWeight: 700, color }}>{label} ({score > 0 ? '+' : ''}{score.toFixed(2)})</span>
      </div>
      <div style={{ height: 5, background: '#1a1a2e', borderRadius: 999, position: 'relative' }}>
        {/* center line */}
        <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: 1, background: '#374151' }} />
        <div style={{
          position: 'absolute',
          left: score >= 0 ? '50%' : `${pct}%`,
          width: `${Math.abs(score) * 50}%`,
          height: '100%',
          background: color,
          borderRadius: 999,
          opacity: 0.85,
        }} />
      </div>
    </div>
  )
}

function RatingBadge({ rating }: { rating: string }) {
  const r = rating.toLowerCase()
  const color = r === 'buy' ? '#22c55e' : r === 'sell' ? '#ef4444' : '#eab308'
  return (
    <span style={{
      fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999,
      background: `${color}15`, color, border: `1px solid ${color}30`,
    }}>
      {rating}
    </span>
  )
}

export default function EnrichmentPanel({ enrichments }: Props) {
  const { news, reddit, alpha_vantage } = enrichments
  const hasAny = news !== null || reddit !== null || alpha_vantage !== null

  if (!hasAny) return null

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <p style={{ fontSize: 11, color: '#374151', fontWeight: 700, letterSpacing: '0.1em' }}>
          OPTIONAL ENRICHMENTS
        </p>
        <span style={{ fontSize: 10, color: '#1f2937', padding: '2px 8px', border: '1px solid #1f2937', borderRadius: 999 }}>
          Configure API keys in .env to enable these panels
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>

        {/* News Sentiment */}
        {news && (
          <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 16, padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <span style={{ fontSize: 18 }}>📰</span>
              <div>
                <p style={{ fontWeight: 700, fontSize: 13 }}>News Sentiment</p>
                <p style={{ fontSize: 11, color: '#4b5563' }}>NewsAPI · last 3 days</p>
              </div>
            </div>

            <SentimentBar score={news.score} />

            <p style={{ fontSize: 11, color: '#6b7280', marginTop: 10 }}>
              {news.headline_count} headline{news.headline_count !== 1 ? 's' : ''} analyzed
            </p>

            {news.sample_headline && (
              <p style={{ fontSize: 12, color: '#9ca3af', marginTop: 8, fontStyle: 'italic', lineHeight: 1.5 }}>
                "{news.sample_headline.length > 80 ? news.sample_headline.slice(0, 80) + '…' : news.sample_headline}"
              </p>
            )}
          </div>
        )}

        {/* Reddit Mentions */}
        {reddit && (
          <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 16, padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <span style={{ fontSize: 18 }}>📣</span>
              <div>
                <p style={{ fontWeight: 700, fontSize: 13 }}>Reddit Mentions (24h)</p>
                <p style={{ fontSize: 11, color: '#4b5563' }}>r/wallstreetbets · r/investing</p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 10 }}>
              <span style={{ fontSize: 36, fontWeight: 900, fontFamily: 'monospace', color: '#e5e7eb', lineHeight: 1 }}>
                {reddit.mention_count}
              </span>
              <span style={{ fontSize: 12, color: '#4b5563' }}>mentions</span>
              {reddit.sentiment_score !== 0 && (
                <span style={{
                  fontSize: 11, fontWeight: 700, marginLeft: 'auto',
                  color: reddit.sentiment_score > 0 ? '#22c55e' : '#ef4444',
                  padding: '2px 8px', borderRadius: 999,
                  background: reddit.sentiment_score > 0 ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
                }}>
                  {reddit.sentiment_score > 0 ? '+' : ''}{reddit.sentiment_score.toFixed(2)} sentiment
                </span>
              )}
            </div>

            <p style={{ fontSize: 12, color: '#6b7280', lineHeight: 1.5, fontStyle: 'italic' }}>
              "{reddit.top_post_title.length > 60 ? reddit.top_post_title.slice(0, 60) + '…' : reddit.top_post_title}"
            </p>
          </div>
        )}

        {/* Alpha Vantage */}
        {alpha_vantage && (
          <div style={{ background: '#0d0d1a', border: '1px solid #1f2937', borderRadius: 16, padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <span style={{ fontSize: 18 }}>📈</span>
              <div>
                <p style={{ fontWeight: 700, fontSize: 13 }}>Analyst Data</p>
                <p style={{ fontSize: 11, color: '#4b5563' }}>Alpha Vantage</p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {alpha_vantage.next_earnings && alpha_vantage.next_earnings !== 'N/A' && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: '#6b7280' }}>Next Earnings</span>
                  <span style={{ fontSize: 13, fontWeight: 700, fontFamily: 'monospace' }}>
                    {alpha_vantage.next_earnings}
                  </span>
                </div>
              )}

              {alpha_vantage.analyst_target !== null && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: '#6b7280' }}>Analyst Target</span>
                  <span style={{ fontSize: 13, fontWeight: 700, fontFamily: 'monospace', color: '#3b82f6' }}>
                    ${alpha_vantage.analyst_target.toFixed(2)}
                  </span>
                </div>
              )}

              {alpha_vantage.analyst_rating && alpha_vantage.analyst_rating !== 'N/A' && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: '#6b7280' }}>Consensus Rating</span>
                  <RatingBadge rating={alpha_vantage.analyst_rating} />
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
