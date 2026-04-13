interface Props {
  text: string
}

export default function Commentary({ text }: Props) {
  return (
    <div className="bg-blue-950/20 border border-blue-800/30 rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-blue-400 text-sm font-semibold">GPT-4o Analysis</span>
        <span className="text-xs bg-blue-900/40 text-blue-300 px-2 py-0.5 rounded-full border border-blue-800/40">
          AI Generated
        </span>
      </div>
      <p className="text-gray-200 text-sm leading-relaxed">{text}</p>
      <p className="text-xs text-gray-600 mt-3">Research only · Not financial advice</p>
    </div>
  )
}
