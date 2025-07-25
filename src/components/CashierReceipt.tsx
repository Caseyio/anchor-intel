import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { format } from 'date-fns'
import { getSaleFromSession } from '../utils/storage'
import type { SaleOut } from '@/schemas/sale'
import { motion } from 'framer-motion'

const CashierReceipt = () => {
  const [sale, setSale] = useState<SaleOut | null>(null)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const stateSale = (location.state as { sale?: SaleOut })?.sale
    const sessionSale = getSaleFromSession()
    console.log('✅ Session sale:', sessionSale)

    if (stateSale) {
      setSale(stateSale)
    } else if (sessionSale) {
      setSale(sessionSale as SaleOut)
    } else {
      navigate('/pos')
    }
  }, [location.state, navigate])

  // ✅ Keyboard: space = print, escape = back
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === ' ') {
        e.preventDefault()
        window.print()
      } else if (e.key === 'Escape') {
        e.preventDefault()
        navigate('/pos')
      }
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [navigate])

  // ✅ Auto-print once rendered
  useEffect(() => {
    if (sale) {
      setTimeout(() => window.print(), 500)
    }
  }, [sale])

  if (!sale) return null

  const subtotal = sale.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  )
  const taxRate = 0.06
  const tax = subtotal * taxRate
  const total = subtotal + tax

  const formattedDate = (() => {
    const rawDate =
      sale.timestamp ??
      (sale as any)?.created_at ??
      (sale as any)?.sale_timestamp
    const parsed = rawDate ? new Date(rawDate) : null
    return parsed && !isNaN(parsed.getTime())
      ? format(parsed, 'PPPpp')
      : 'Unknown date'
  })()

  return (
    <motion.div
      className="receipt-container font-mono text-xs text-black mx-auto p-4 print:p-0 print:m-0"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Store Info */}
      <div className="text-center mb-2">
        <p><strong>Anchor Beverage Co.</strong></p>
        <p>123 Main Street</p>
        <p>Annapolis, MD 21401</p>
        <p>(410) 555-1234</p>
      </div>

      {/* Sale Info */}
      <p className="text-center mb-1">
        <strong>Sale ID:</strong> {sale.id ?? 'N/A'}
      </p>
      <p className="text-center mb-2">{formattedDate}</p>
      <hr className="my-2 border-black" />

      {/* Line Items */}
      {sale.items.map((item, idx) => (
        <div key={idx} className="flex justify-between py-1">
          <div>
            {item.quantity} × {item.name || 'Unnamed Item'}
            <br />
            <span className="text-[10px] text-gray-600">
              SKU: {item.sku || 'N/A'}
            </span>
          </div>
          <div>${(item.price * item.quantity).toFixed(2)}</div>
        </div>
      ))}
      <hr className="my-2 border-black" />

      {/* Totals */}
      <div className="flex justify-between">
        <span>Subtotal:</span>
        <span>${subtotal.toFixed(2)}</span>
      </div>
      <div className="flex justify-between">
        <span>Tax (6%):</span>
        <span>${tax.toFixed(2)}</span>
      </div>
      <div className="flex justify-between font-bold text-sm mt-1">
        <span>Total:</span>
        <span>${total.toFixed(2)}</span>
      </div>

      {/* Payment Confirmation */}
      <p className="text-center mt-3 text-green-600 font-semibold">
        Payment Accepted{sale.payment_type ? ` via ${sale.payment_type}` : ''}
      </p>

      {/* Footer */}
      <div className="text-center mt-2">
        <p>Thank you for supporting local businesses!</p>
        <p>All sales final unless otherwise stated.</p>
        <p>Must be 21+ to purchase alcohol.</p>
      </div>

      {/* Buttons */}
      <div className="flex gap-2 mt-4 print:hidden">
        <button
          onClick={() => navigate('/pos')}
          className="w-full bg-gray-200 py-2 rounded"
        >
          ⬅ Back to Checkout
        </button>
        <button
          onClick={() => window.print()}
          className="w-full bg-blue-500 text-white py-2 rounded"
        >
          🖨️ Print
        </button>
      </div>
    </motion.div>
  )
}

export default CashierReceipt
