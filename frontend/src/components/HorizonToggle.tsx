const HORIZONS = [
  { value: 1, label: '1 Day' },
  { value: 3, label: '3 Days' },
  { value: 5, label: '5 Days' },
]

interface Props {
  value: number
  onChange: (h: number) => void
}

export default function HorizonToggle({ value, onChange }: Props) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500 mr-1">Horizon:</span>
      {HORIZONS.map((h) => (
        <button
          key={h.value}
          onClick={() => onChange(h.value)}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all
            ${value === h.value
              ? 'bg-gray-100 text-gray-900'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
        >
          {h.label}
        </button>
      ))}
    </div>
  )
}
