// src/schemas/KpiSummary.ts
import { z } from "zod";

export const KpiSummarySchema = z.object({
  total_sales: z.number().default(0),
  avg_daily_sales: z.number().default(0),
  total_transactions: z.number().int().default(0),
  avg_basket_size: z.number().default(0),
  return_rate: z.number().default(0),
  top_category: z.string().default("N/A"),
});

export type KpiSummary = z.infer<typeof KpiSummarySchema>;
