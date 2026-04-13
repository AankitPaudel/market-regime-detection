import { useState } from 'react'
import { triggerRetrain, getRetrainStatus } from '../lib/api'
import toast from 'react-hot-toast'

interface Props {
  ticker: string
  horizon: number
}

type Status = 'idle' | 'running' | 'done' | 'error'

export default function RetrainButton({ ticker, horizon }: Props) {
  const [status, setStatus] = useState<Status>('idle')

  const handleRetrain = async () => {
    setStatus('running')
    toast('Retraining started — this takes ~60 seconds', { icon: '⚙️' })
    try {
      await triggerRetrain(ticker, horizon)
      const key = `${ticker}_${horizon}d`
      const poll = setInterval(async () => {
        const res = await getRetrainStatus(key)
        if (res.status === 'done') {
          clearInterval(poll)
          setStatus('done')
          toast.success(`Model retrained for ${ticker} ${horizon}d!`)
        } else if (typeof res.status === 'string' && res.status.startsWith('error')) {
          clearInterval(poll)
          setStatus('error')
          toast.error('Retrain failed')
        }
      }, 5000)
    } catch {
      setStatus('error')
      toast.error('Retrain request failed')
    }
  }

  const labels: Record<Status, string> = {
    idle:    `⚙️ Retrain ${ticker} ${horizon}d model on live data`,
    running: '⏳ Retraining... (~60s)',
    done:    '✅ Retrained successfully',
    error:   '❌ Retrain failed — try again',
  }

  return (
    <button
      onClick={handleRetrain}
      disabled={status === 'running'}
      className="px-4 py-2 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-40
                 text-gray-400 rounded-lg border border-gray-700 transition-all"
    >
      {labels[status]}
    </button>
  )
}
