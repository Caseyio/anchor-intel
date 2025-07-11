// src/schemas/product.ts
import { z } from 'zod'

// 🛒 ProductCreate (POST input)
export const ProductCreateSchema = z.object({
  name: z.string().min(1),
  sku: z.string().min(1),
  price: z.number().nonnegative(),
  category: z.string().min(1),
  stock_quantity: z.number().int().nonnegative(),
})

// 📦 ProductOut (GET response)
export const ProductOutSchema = z.object({
  id: z.number(),
  name: z.string(),
  sku: z.string(),
  price: z.number(),
  category: z.string(),
  stock_quantity: z.number(),
})

// 🧾 Inferred Types
export type ProductCreate = z.infer<typeof ProductCreateSchema>
export type ProductOut = z.infer<typeof ProductOutSchema>

// 🔍 Safe Validation Helper
export function validateProductOut(data: unknown): ProductOut | null {
  const result = ProductOutSchema.safeParse(data)
  return result.success ? result.data : null
}
