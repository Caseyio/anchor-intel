// src/schemas/inventory.ts
import { z } from 'zod'

// 🔼 Inventory event input (adjustment, restock, etc.)
export const InventoryEventInSchema = z.object({
  product_id: z.number(),
  change: z.number().int(),
  reason: z.string().optional(),
})

// 📘 Inventory event from backend (GET response)
export const InventoryEventOutSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  change: z.number(),
  reason: z.string().optional(),
  created_at: z.string(),
})

// 🧾 Types
export type InventoryEventIn = z.infer<typeof InventoryEventInSchema>
export type InventoryEventOut = z.infer<typeof InventoryEventOutSchema>

// 🧪 Validator
export function validateInventoryEventOut(data: unknown): InventoryEventOut | null {
  const result = InventoryEventOutSchema.safeParse(data)
  return result.success ? result.data : null
}
