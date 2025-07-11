import React, { useEffect, useState } from 'react'

type SessionSummary = {
  id: number
  cashier_name: string
  terminal_id: string
  opened_at: string
  closed_at: string
  total_sales: number
  returns: number
  system_cash_total: number
  closing_cash: number
  cash_difference: number
  is_over_short: boolean
}

export default function ManagerCloseout() {
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [notes, setNotes] = useState<string>('')
  const [managerPin, setManagerPin] = useState<string>('')

  // Placeholder fetch
  const fetchSessions = async () => {
    // This will eventually call `/manager_closeouts/today` or similar
    setSessions([
      {
        id: 1,
        cashier_name: 'Alice',
        terminal_id: 'T001',
        opened_at: '2025-07-02T09:00:00Z',
        closed_at: '2025-07-02T17:00:00Z',
        total_sales: 980.5,
        returns: 30.0,
        system_cash_total: 700.0,
        closing_cash: 695.0,
        cash_difference: -5.0,
        is_over_short: true,
      },
      {
        id: 2,
        cashier_name: 'Bob',
        terminal_id: 'T002',
        opened_at: '2025-07-02T10:00:00Z',
        closed_at: '2025-07-02T18:00:00Z',
        total_sales: 820.0,
        returns: 10.0,
        system_cash_total: 550.0,
        closing_cash: 550.0,
        cash_difference: 0,
        is_over_short: false,
      },
    ])
    setLoading(false)
  }

  useEffect(() => {
    fetchSessions()
  }, [])

  const handleSubmit = () => {
    alert(`Z-report submitted with notes: ${notes}`)
    // This will call a POST to /manager_closeouts
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold">Manager Daily Closeout</h1>

      {loading ? (
        <div className="text-lg">Loading sessions...</div>
      ) : (
        <table className="w-full border text-sm rounded-xl overflow-hidden">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="p-2">Cashier</th>
              <th className="p-2">Terminal</th>
              <th className="p-2">Opened</th>
              <th className="p-2">Closed</th>
              <th className="p-2">Sales</th>
              <th className="p-2">Returns</th>
              <th className="p-2">Expected Cash</th>
              <th className="p-2">Actual Cash</th>
              <th className="p-2">Diff</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.id} className={s.is_over_short ? 'bg-red-50' : ''}>
                <td className="p-2 font-medium">{s.cashier_name}</td>
                <td className="p-2">{s.terminal_id}</td>
                <td className="p-2">{new Date(s.opened_at).toLocaleTimeString()}</td>
                <td className="p-2">{new Date(s.closed_at).toLocaleTimeString()}</td>
                <td className="p-2">${s.total_sales.toFixed(2)}</td>
                <td className="p-2">${s.returns.toFixed(2)}</td>
                <td className="p-2">${s.system_cash_total.toFixed(2)}</td>
                <td className="p-2">${s.closing_cash.toFixed(2)}</td>
                <td className={`p-2 font-semibold ${s.cash_difference !== 0 ? 'text-red-600' : 'text-green-600'}`}>
                  ${s.cash_difference.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="bg-gray-100 p-4 rounded-xl space-y-4 border">
        <div>
          <label className="block text-sm font-medium">Manager Notes:</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full p-2 border rounded-lg"
            placeholder="Add Z-report summary or exceptions..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Manager PIN (for confirmation):</label>
          <input
            type="password"
            value={managerPin}
            onChange={(e) => setManagerPin(e.target.value)}
            className="w-full p-2 border rounded-lg"
            placeholder="Enter PIN"
          />
        </div>

        <button
          onClick={handleSubmit}
          className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800"
        >
          Submit Z-Report
        </button>
      </div>
    </div>
  )
}
