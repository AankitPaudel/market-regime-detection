import { useState } from 'react'
import { triggerRetrain, getRetrainStatus } from '../lib/api'
import toast from 'react-hot-toast'

interface Props { ticker: string; horizon: number }
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
          toast.success(`Model retrained for ${ticker} ${horizon}d on latest data!`)
        } else if (typeof res.status === 'string' && res.status.startsWith('error')) {
          clearInterval(poll)
          setStatus('error')
          toast.error('Retrain failed — check backend logs')
        }
      }, 5000)
    } catch {
      setStatus('error')
      toast.error('Retrain request failed')
    }
  }

  return (
    <button
      onClick={handleRetrain}
      disabled={status === 'running'}
      style={{
        padding: '8px 16px', borderRadius: 8, cursor: status === 'running' ? 'not-allowed' : 'pointer',
        border: '1px solid #1f2937', background: '#070710', color: '#4b5563',
        fontSize: 12, fontWeight: 600, opacity: status === 'running' ? 0.5 : 1,
      }}
    >
      {status === 'idle'    && `⚙️ Retrain lgbm_${ticker}_${horizon}d on latest 365d data`}
      {status === 'running' && '⏳ Retraining in background...'}
      {status === 'done'    && '✅ Retrained — next prediction uses updated model'}
      {status === 'error'   && '❌ Retrain failed — try again'}
    </button>
  )
}
