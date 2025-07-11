// src/schemas/sale.ts
import { z } from 'zod';

// 🧾 SaleItemOut (from receipts, responses)
export const SaleItemOutSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  name: z.string().optional(),
  sku: z.string().optional(),
  quantity: z.number(),
  price: z.number(),
});

// 🧾 SaleOut (receipt or GET /sale/:id)
export const SaleOutSchema = z.object({
  id: z.number(),
  total_amount: z.number(),
  timestamp: z.string(),
  updated_at: z.string().optional(),
  payment_type: z.string(),
  items: z.array(SaleItemOutSchema),
});

// 🧾 SaleItemInput (POST input, minimal)
export const SaleItemInputSchema = z.object({
  product_id: z.number(),
  quantity: z.number(),
});

// 🧾 SaleItem (used in create payload)
export const SaleItemSchema = z.object({
  product_id: z.number(),
  quantity: z.number(),
  price: z.number(),
});

// 🧾 SaleCreate (used in POST body)
export const SaleCreateSchema = z.object({
  total_amount: z.number(),
  timestamp: z.string().optional(),
  payment_type: z.string(),
  items: z.array(SaleItemSchema),
});

// 🔁 Unified Types
export type SaleItemOut = z.infer<typeof SaleItemOutSchema>;
export type SaleOut = z.infer<typeof SaleOutSchema>;
export type SaleItem = z.infer<typeof SaleItemSchema>;
export type SaleItemInput = z.infer<typeof SaleItemInputSchema>;
export type SaleCreate = z.infer<typeof SaleCreateSchema>;

// ✅ Safe validation helper
export function validateSaleOut(data: unknown): SaleOut | null {
  const result = SaleOutSchema.safeParse(data);
  return result.success ? result.data : null;
}
