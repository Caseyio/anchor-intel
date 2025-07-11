import React, { useEffect, useState } from 'react'

type CashierSession = {
  id: number
  cashier_id: number
  terminal_id?: string
  opened_at: string
  closed_at?: string
  opening_cash: number
  closing_cash?: number
  system_cash_total?: number
  cash_difference?: number
  is_over_short?: boolean
  notes?: string
}

export default function CashierCloseout() {
  const [session, setSession] = useState<CashierSession | null>(null)
  const [systemTotal, setSystemTotal] = useState<number>(0)
  const [closingCash, setClosingCash] = useState<string>('')
  const [notes, setNotes] = useState<string>('')
  const [difference, setDifference] = useState<string>('0.00')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string>('')
  const [submitting, setSubmitting] = useState<boolean>(false)

  const getCurrentSession = async () => {
    try {
      const res = await fetch('/cashier_sessions/current')
      if (!res.ok) throw new Error('No active session found.')
      const data: CashierSession = await res.json()
      setSession(data)
    } catch (err: any) {
      setError(err.message)
    }
  }

  const getSystemTotal = async (sessionId: number) => {
    try {
      const res = await fetch(`/cashier_sessions/${sessionId}/summary`)
      const data = await res.json()
      setSystemTotal(parseFloat(data.system_cash_total))
    } catch (err) {
      console.error('Error fetching system total:', err)
    }
  }

  useEffect(() => {
    getCurrentSession().finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (session?.id) getSystemTotal(session.id)
  }, [session])

  useEffect(() => {
    const diff = parseFloat(closingCash || '0') - (systemTotal || 0)
    setDifference(diff.toFixed(2))
  }, [closingCash, systemTotal])

  const handleCloseout = async () => {
    if (!session?.id || closingCash === '') return
    setSubmitting(true)
    try {
      const res = await fetch(`/cashier_sessions/${session.id}/close`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          closing_cash: parseFloat(closingCash),
          notes,
        }),
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Closeout failed.')
      }

      const closedSession: CashierSession = await res.json()
      alert(`Session closed. Over/Short: $${closedSession.cash_difference}`)
      setSession(null)
      setClosingCash('')
      setNotes('')
    } catch (err: any) {
      alert(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="p-4 text-lg">Loading session...</div>
  if (error) return <div className="p-4 text-red-600">{error}</div>

  return (
    <div className="p-6 max-w-xl mx-auto text-left space-y-6">
      <h1 className="text-2xl font-bold">Cashier Closeout</h1>

      {session ? (
        <>
          <div className="bg-white rounded-xl shadow p-4 space-y-2 border">
            <p><strong>Terminal:</strong> {session.terminal_id}</p>
            <p><strong>Opened At:</strong> {new Date(session.opened_at).toLocaleString()}</p>
            <p><strong>Opening Cash:</strong> ${session.opening_cash.toFixed(2)}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-xl border space-y-3">
            <p><strong>System Cash Total:</strong> ${systemTotal.toFixed(2)}</p>

            <label className="block text-sm font-semibold">Actual Cash in Drawer:</label>
            <input
              type="number"
              value={closingCash}
              onChange={(e) => setClosingCash(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-lg"
              placeholder="Enter closing cash"
            />

            <p className={`font-semibold ${Math.abs(parseFloat(difference)) > 1 ? 'text-red-600' : 'text-green-600'}`}>
              {parseFloat(difference) > 0
                ? 'Over'
                : parseFloat(difference) < 0
                ? 'Short'
                : 'Exact'} by ${Math.abs(parseFloat(difference))}
            </p>

            <label className="block text-sm font-semibold">Notes:</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border p-2 rounded-lg"
              rows={3}
              placeholder="Enter notes, incidents, or handoff info"
            />

            <button
              disabled={submitting}
              onClick={handleCloseout}
              className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Closeout'}
            </button>
          </div>
        </>
      ) : (
        <div className="text-gray-600">No active session found.</div>
      )}
    </div>
  )
}
