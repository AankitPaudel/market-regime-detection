const HORIZONS = [
  { value: 1, label: '1 Day',  desc: 'Next session' },
  { value: 3, label: '3 Days', desc: 'Short-term' },
  { value: 5, label: '5 Days', desc: '1 trading week' },
]

interface Props { value: number; onChange: (h: number) => void }

export default function HorizonToggle({ value, onChange }: Props) {
  return (
    <div style={{ display: 'flex', gap: 8 }}>
      {HORIZONS.map((h) => {
        const active = value === h.value
        return (
          <button
            key={h.value}
            onClick={() => onChange(h.value)}
            style={{
              padding: '8px 16px', borderRadius: 10, cursor: 'pointer', textAlign: 'left',
              border: active ? '1px solid rgba(99,102,241,0.5)' : '1px solid #1f2937',
              background: active ? 'rgba(99,102,241,0.12)' : '#070710',
              color: active ? '#a5b4fc' : '#4b5563',
            }}
          >
            <div style={{ fontSize: 13, fontWeight: 700 }}>{h.label}</div>
            <div style={{ fontSize: 10, opacity: 0.7, marginTop: 2 }}>{h.desc}</div>
          </button>
        )
      })}
    </div>
  )
}
