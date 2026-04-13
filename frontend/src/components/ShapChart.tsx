import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ShapValue {
  feature: string
  shap_value: number
}

interface Props {
  shapValues: ShapValue[]
}

export default function ShapChart({ shapValues }: Props) {
  const data = [...shapValues].sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h3 className="text-sm font-semibold text-gray-300 mb-1">SHAP Feature Importance</h3>
      <p className="text-xs text-gray-600 mb-4">Why the model made this prediction</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical">
          <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 10 }} />
          <YAxis
            dataKey="feature"
            type="category"
            tick={{ fill: '#9ca3af', fontSize: 10 }}
            width={115}
          />
          <Tooltip
            contentStyle={{
              background: '#111827',
              border: '1px solid #374151',
              borderRadius: 8,
              color: '#fff',
            }}
            formatter={(val: number) => [val.toFixed(5), 'SHAP value']}
          />
          <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.shap_value > 0 ? '#22c55e' : '#ef4444'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-600 mt-2">
        Green = pushes toward signal · Red = pushes against
      </p>
    </div>
  )
}
