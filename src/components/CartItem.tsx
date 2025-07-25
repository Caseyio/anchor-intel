// src/components/CartItem.tsx
import { useCallback } from "react"

interface CartItemProps {
  id: number
  name: string
  price: number
  quantity: number
  onQuantityChange: (id: number, quantity: number) => void
  onRemove: (id: number) => void
}

const CartItem: React.FC<CartItemProps> = ({
  id,
  name,
  price,
  quantity,
  onQuantityChange,
  onRemove,
}) => {
  const handleDecrease = useCallback(() => {
    if (quantity > 1) onQuantityChange(id, quantity - 1)
  }, [id, quantity, onQuantityChange])

  const handleIncrease = useCallback(() => {
    onQuantityChange(id, quantity + 1)
  }, [id, quantity, onQuantityChange])

  return (
    <div className="flex justify-between items-center border-b py-3 gap-4">
      <div className="flex-1">
        <div className="font-medium text-base leading-tight">{name}</div>
        <div className="text-sm text-muted-foreground">${price.toFixed(2)}</div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={handleDecrease}
          className="px-2 py-1 border rounded text-lg bg-muted"
        >
          −
        </button>
        <span className="min-w-[2ch] text-center">{quantity}</span>
        <button
          onClick={handleIncrease}
          className="px-2 py-1 border rounded text-lg bg-muted"
        >
          +
        </button>
        <button
          onClick={() => onRemove(id)}
          className="text-red-500 text-xl hover:text-red-600 px-2"
          aria-label="Remove item"
        >
          ❌
        </button>
      </div>
    </div>
  )
}

export default CartItem
