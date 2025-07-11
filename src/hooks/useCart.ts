import { useState, useEffect } from 'react';

export interface CartItem {
  id: number;
  name: string;
  price: number;
  sku?: string;
  quantity: number;
  [key: string]: any; // For flexibility (e.g., category, tags, etc.)
}

// Load cart items from localStorage
const loadCartFromStorage = (): CartItem[] => {
  try {
    const data = localStorage.getItem('cartItems');
    const parsed = data ? JSON.parse(data) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    console.error('❌ Failed to load cart from localStorage:', err);
    return [];
  }
};

// Save cart items to localStorage
const saveCartToStorage = (cart: CartItem[]) => {
  try {
    localStorage.setItem('cartItems', JSON.stringify(cart));
  } catch (err) {
    console.error('❌ Failed to save cart to localStorage:', err);
  }
};

export const useCart = () => {
  const [cartItems, setCartItems] = useState<CartItem[]>(loadCartFromStorage());

  // Sync to storage on cart change
  useEffect(() => {
    saveCartToStorage(cartItems);
  }, [cartItems]);

  const addToCart = (product: CartItem) => {
    setCartItems((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const removeFromCart = (productId: number) => {
    setCartItems((prev) => prev.filter((item) => item.id !== productId));
  };

  const updateQuantity = (productId: number, qty: number) => {
    if (qty < 1) return;
    setCartItems((prev) =>
      prev.map((item) =>
        item.id === productId ? { ...item, quantity: qty } : item
      )
    );
  };

  const clearCart = () => {
    setCartItems([]);
    localStorage.removeItem('cartItems');
  };

  return {
    cartItems,
    setCartItems,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    loadCartFromStorage, // Exposed utility
  };
};
