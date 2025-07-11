// src/hooks/useKpiSummary.ts
import { useQuery } from "@tanstack/react-query";
import { fetchKpiSummary } from "@/services/api";
import { KpiSummary } from "@/schemas/KpiSummary";

/**
 * Custom hook to fetch KPI summary from the backend.
 * Automatically refetches every 10 seconds and logs the response.
 */
export const useKpiSummary = (start: string, end: string) =>
  useQuery<KpiSummary>({
    queryKey: ["kpi-summary", start, end],
    queryFn: async () => {
      const data = await fetchKpiSummary(start, end);
      console.log("📊 KPI Summary Response:", data);
      return data;
    },
    refetchInterval: 10_000, // auto-refresh every 10s
    staleTime: 5_000,        // consider fresh for 5s
  });
