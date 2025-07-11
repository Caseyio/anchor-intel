import { z } from 'zod';

// 🔁 ReturnItem (used for UI + backend input)
export const ReturnItemSchema = z.object({
  product_id: z.number(),
  quantity: z.number().int().positive(),
  restock: z.boolean().optional().default(true),
  reason: z.string().min(1),
  notes: z.string().optional(),
});

// 📨 ReturnCreate = ReturnItem
export const ReturnCreateSchema = ReturnItemSchema;

// 📦 Batch return payload
export const ReturnCreateBatchSchema = z.object({
  sale_id: z.number().optional(),
  returns: z.array(ReturnCreateSchema),
});

// 📜 Stored return record
export const ReturnRecordSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  quantity: z.number(),
  reason: z.string(),
  notes: z.string().optional(),
  created_at: z.string().optional(),
});

// 🧾 Types
export type ReturnItem = z.infer<typeof ReturnItemSchema>;
export type ReturnCreate = z.infer<typeof ReturnCreateSchema>;
export type ReturnCreateBatch = z.infer<typeof ReturnCreateBatchSchema>;
export type ReturnRecord = z.infer<typeof ReturnRecordSchema>;

// ✅ UI-only extended type (used in frontend)
export type ReturnItemUI = ReturnItem & {
  id?: number;
  name: string;
  sku: string;
  price: number;
};

// 🧪 Safe checker
export function validateReturnRecord(data: unknown): ReturnRecord | null {
  const result = ReturnRecordSchema.safeParse(data);
  return result.success ? result.data : null;
}
