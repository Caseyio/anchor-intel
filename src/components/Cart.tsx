// src/components/Cart.tsx
import React from 'react'
import CartItem from './CartItem'

type CartItemType = {
  id: number
  name: string
  price: number
  quantity: number
}

type CartProps = {
  items: CartItemType[]
  onQuantityChange: (productId: number, quantity: number) => void
  onRemoveItem: (productId: number) => void
}

const Cart: React.FC<CartProps> = ({ items, onQuantityChange, onRemoveItem }) => {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const taxRate = 0.06
  const tax = subtotal * taxRate
  const total = subtotal + tax

  return (
    <div>
      {/* Cart List */}
      {items.length === 0 ? (
        <p className="text-gray-500">Cart is empty</p>
      ) : (
        <div className="mb-4">
          {items.map((item) => (
            <CartItem
              key={item.id}
              id={item.id}
              name={item.name}
              price={item.price}
              quantity={item.quantity}
              onQuantityChange={onQuantityChange}
              onRemove={onRemoveItem}
            />
          ))}
        </div>
      )}

      {/* Totals */}
      <div className="mb-4 border-t pt-2">
        <div className="flex justify-between">
          <span>Subtotal:</span>
          <span>${subtotal.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span>Tax (6%):</span>
          <span>${tax.toFixed(2)}</span>
        </div>
        <div className="flex justify-between font-bold text-lg">
          <span>Total:</span>
          <span>${total.toFixed(2)}</span>
        </div>
      </div>
    </div>
  )
}

export default Cart
