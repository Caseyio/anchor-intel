// src/schemas/cashier.ts
import { z } from 'zod'

export const CashierSessionCreateSchema = z.object({
  opening_cash: z.number().nonnegative(),
  terminal_id: z.string().optional(),
  notes: z.string().optional(),
})

export const CashierSessionCloseSchema = z.object({
  closing_cash: z.number().nonnegative(),
  notes: z.string().optional(),
})

export const CashierSessionOutSchema = z.object({
  id: z.number(),
  cashier_id: z.number(),
  terminal_id: z.string().optional(),
  opened_at: z.string(),
  closed_at: z.string().optional(),
  opening_cash: z.number(),
  closing_cash: z.number().optional(),
  system_cash_total: z.number().optional(),
  cash_difference: z.number().optional(),
  is_over_short: z.boolean().optional(),
  notes: z.string().optional(),
})

export type CashierSessionCreate = z.infer<typeof CashierSessionCreateSchema>
export type CashierSessionClose = z.infer<typeof CashierSessionCloseSchema>
export type CashierSessionOut = z.infer<typeof CashierSessionOutSchema>

export function validateCashierSessionOut(data: unknown): CashierSessionOut | null {
  const result = CashierSessionOutSchema.safeParse(data)
  return result.success ? result.data : null
}
