export type DailySalesSummary = {
  sale_date: string
  day_of_week: string
  total_sales_count: number
  total_sales_value: number
  avg_sale_value: number
}

export type TopProductTrend = {
  period: string
  product_id: number
  product_name: string
  total_units_sold: number
  total_revenue: number
}

export type InventorySnapshot = {
  product_id: number
  name: string
  sku: string
  category: string
  stock_quantity: number
}

export type InventoryMovement = {
  product_id: number
  name: string
  category: string
  total_added: number
  total_removed: number
  net_change: number
}

export type TopMarginProduct = {
  product_id: number
  name: string
  category: string
  units_sold: number
  revenue: number
  cost_basis: number
  margin_dollars: number
  margin_percent: number
}

export type CategorySales = {
  category: string
  total_units_sold: number
  total_revenue: number
  avg_price: number
}

export type LowStockAlert = {
  product_id: number
  name: string
  category: string
  stock_quantity: number
}

// Return analytics
export type ProductReturnRate = {
  product_id: number
  product_name: string
  total_sold: number
  total_returned: number
  return_rate: number
}

export type SaleReturnRate = {
  sale_id: number
  total_items_sold: number
  total_items_returned: number
  return_rate: number
}

export type CashierReturnRate = {
  user_id: number
  username: string
  total_returns: number
  total_sales: number
  return_ratio: number
}
