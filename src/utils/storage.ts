// src/utils/storage.ts

import { SaleOut } from '@/schemas/sale'

// Session storage key constants
const SALE_KEY = 'latestSale'
const SALE_HISTORY_KEY = 'recentSales'

// Save latest completed sale
export const saveSaleToSession = (sale: SaleOut): void => {
  sessionStorage.setItem(SALE_KEY, JSON.stringify(sale))
}

// Retrieve last sale from session
export function getSaleFromSession(): SaleOut | null {
  const raw = sessionStorage.getItem(SALE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as SaleOut
  } catch (err) {
    console.error('❌ Failed to parse cached sale:', err)
    return null
  }
}

// Clear current session sale
export const clearSaleFromSession = (): void => {
  sessionStorage.removeItem(SALE_KEY)
}

// Save recent sale to history list (max 5)
export const saveRecentSale = (sale: SaleOut): void => {
  const recent: SaleOut[] = JSON.parse(sessionStorage.getItem(SALE_HISTORY_KEY) || '[]')
  recent.unshift(sale)
  sessionStorage.setItem(SALE_HISTORY_KEY, JSON.stringify(recent.slice(0, 5)))
}

// Get list of recent sales
export const getRecentSales = (): SaleOut[] => {
  const data = sessionStorage.getItem(SALE_HISTORY_KEY)
  return data ? (JSON.parse(data) as SaleOut[]) : []
}

// Clear recent sales history
export const clearRecentSales = (): void => {
  sessionStorage.removeItem(SALE_HISTORY_KEY)
}
