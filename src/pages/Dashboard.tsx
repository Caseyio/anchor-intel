import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <div className="p-6 max-w-xl mx-auto space-y-8 bg-white rounded-2xl shadow">
      <h1 className="text-3xl font-bold text-center">Dashboard</h1>

      <div className="grid gap-6">
        <button
          onClick={() => navigate('/pos')}
          className="w-full bg-yellow-500 hover:bg-yellow-600 text-white text-lg py-4 rounded-xl shadow"
        >
          🛒 POS (Checkout)
        </button>

        <button
          onClick={() => navigate('/cashier-closeout')}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white text-lg py-4 rounded-xl shadow"
        >
          🧾 Cashier Closeout
        </button>

        <button
          onClick={() => navigate('/manager-closeout')}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-lg py-4 rounded-xl shadow"
        >
          📋 Manager Daily Closeout & Z-Report
        </button>

        <button
          onClick={() => navigate('/analytics')}
          className="w-full bg-green-600 hover:bg-green-700 text-white text-lg py-4 rounded-xl shadow"
        >
          📊 Analytics & Business Intelligence
        </button>
      </div>
    </div>
  )
}
