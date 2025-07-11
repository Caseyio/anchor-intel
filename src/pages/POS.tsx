import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import API from '../services/api'
import { useSmartSearchFocus } from '../hooks/useSmartSearchFocus'
import { useCart } from '../hooks/useCart'
import CheckoutHeader from '../components/CheckoutHeader'
import ProductSearchBox from '../components/ProductSearchBox'
import ProductSuggestions from '../components/ProductSuggestions'
import Cart from '../components/Cart'
import PaymentModal from '../components/PaymentModal'
import CashConfirmModal from '../components/CashConfirmModal'
import { AnimatePresence } from 'framer-motion'
import { saveSaleToSession, getSaleFromSession } from '@/utils/storage'
import { SaleOut } from '@/schemas/sale'

interface Product {
  id: number
  name: string
  sku: string
  price: number
}

const POS = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [search, setSearch] = useState('')
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [showCashConfirm, setShowCashConfirm] = useState(false)
  const [lastSale, setLastSale] = useState<SaleOut | null>(null)

  const searchRef = useSmartSearchFocus(true)
  const navigate = useNavigate()

  const {
    cartItems,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
  } = useCart()

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await API.get('/products/products')
        setProducts(res.data)
      } catch (err) {
        console.error('❌ Failed to fetch products:', err)
      }
    }

    fetchProducts()

    const cached = getSaleFromSession()
    if (cached) {
      setLastSale(cached)
      console.log('✅ Restored cached sale:', cached)
    } else {
      console.log('⚠️ Session sale = null')
    }
  }, [])

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const isSearchEmpty = search.trim() === ''
      const isSafeToCheckout =
        isSearchEmpty &&
        !showPaymentModal &&
        !showCashConfirm &&
        cartItems.length > 0

      if (e.key === ' ' && isSafeToCheckout) {
        e.preventDefault()
        handleStartCheckout()
        return
      }

      if (showPaymentModal) {
        if (e.key === ' ') {
          e.preventDefault()
          handlePaymentConfirm()
        }
        if (e.key === 'Shift') {
          e.preventDefault()
          setShowPaymentModal(false)
          setShowCashConfirm(true)
        }
      }

      if (showCashConfirm && e.key === 'Escape') {
        e.preventDefault()
        setShowCashConfirm(false)
        setShowPaymentModal(true)
        return
      }

      if (e.key === 'Escape' && !showPaymentModal && !showCashConfirm) {
        if (cartItems.length > 0) {
          e.preventDefault()
          const lastItemId = cartItems[cartItems.length - 1]?.id
          if (lastItemId) removeFromCart(lastItemId)
        } else {
          e.preventDefault()
          navigate('/dashboard')
        }
      }

    },
    [showPaymentModal, showCashConfirm, cartItems, search, navigate]
  )

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  const handleStartCheckout = () => {
    if (cartItems.length === 0) {
      alert('No items in cart')
      return
    }
    setShowPaymentModal(true)
  }

  const handlePaymentConfirm = async () => {
    await submitSale('card')
  }

  const handleConfirmCashSale = async () => {
    await submitSale('cash')
  }

  const submitSale = async (paymentType: string) => {
    const timestamp = new Date().toISOString()
    const computedTotal = cartItems.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    )
    const total_amount = computedTotal.toFixed(2)

    const payload = {
      total_amount: parseFloat(total_amount),
      timestamp,
      payment_type: paymentType,
      items: cartItems.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price,
      })),
    }

    console.log('🚀 Submitting payload to /sales/sales/checkout:', payload)

    try {
      const response = await API.post('/sales/sales/checkout', payload)

      const newSale: SaleOut = {
        id: response.data.sale_id,
        total_amount: parseFloat(total_amount),
        timestamp,
        updated_at: timestamp,
        payment_type: paymentType,
        items: cartItems.map((item) => ({
          id: 0,
          product_id: item.id,
          name: item.name,
          sku: item.sku ?? '',
          quantity: item.quantity,
          price: item.price,
        })),
      }

      saveSaleToSession(newSale)
      setLastSale(newSale)
      clearCart()
      setSearch('')
      setShowPaymentModal(false)
      setShowCashConfirm(false)
      searchRef.current?.focus()
    } catch (err) {
      console.error('❌ Payment failed:', err)
      alert('Payment failed. Try again.')
    }
  }

  const filteredProducts =
    products?.filter(
      (p) =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.sku.toLowerCase().includes(search.toLowerCase())
    ) || []

  const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const tax = subtotal * 0.06
  const total = subtotal + tax

  return (
    <>
      {/* Floating Print Last Receipt Button */}
      {lastSale && (
        <button
          onClick={() => navigate('/receipt/last')}
          className="fixed bottom-4 left-[10px] z-50 bg-white border border-gray-300 rounded-full shadow-lg px-4 py-2 text-sm font-mono hover:bg-gray-100"
        >
          🧾 Print Last Receipt
        </button>
)}

      <div className="p-12 max-w-xl mx-auto">
        <div className="bg-white p-6 rounded shadow-md space-y-4">
          <CheckoutHeader />

          <ProductSearchBox
            search={search}
            setSearch={setSearch}
            searchRef={searchRef}
          />

          {search.trim().length > 0 && filteredProducts.length > 0 && (
            <ProductSuggestions
              products={filteredProducts}
              onSelect={(product) => addToCart({ ...product, quantity: 1 })}
              search={search}
              setSearch={setSearch}
              searchRef={searchRef}
            />
          )}

          <Cart
            items={cartItems}
            onQuantityChange={updateQuantity}
            onRemoveItem={removeFromCart}
          />

          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleStartCheckout()
            }}
          >
            <button
              type="submit"
              className="w-full bg-green-600 text-white text-lg font-mono py-3 rounded mt-2"
            >
              Complete Sale
            </button>
          </form>

          {lastSale && (
            <div className="grid grid-cols-2 gap-2">
            </div>
          )}
        </div>
      </div>

      <AnimatePresence>
        {showPaymentModal && (
          <PaymentModal
            onConfirm={handlePaymentConfirm}
            onCancel={() => setShowPaymentModal(false)}
            onCash={() => {
              setShowPaymentModal(false)
              setShowCashConfirm(true)
            }}
          />
        )}
        {showCashConfirm && (
          <CashConfirmModal
            onComplete={handleConfirmCashSale}
            onCancel={() => {
              setShowCashConfirm(false)
              searchRef.current?.focus()
            }}
            onChangeMethod={() => {
              setShowCashConfirm(false)
              setShowPaymentModal(true)
            }}
          />
        )}
      </AnimatePresence>
    </>
  )
}

export default POS
