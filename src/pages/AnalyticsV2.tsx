import { useKpiSummary } from "@/hooks/useKpiSummary"
import { KpiGrid } from "@/components/KpiGrid"
import { format } from "date-fns"
import {
  Card,
  CardContent
} from "@/components/ui/card"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { useEffect, useState } from "react"
import API from "@/services/api"

interface DailySalesSummary {
  sale_date: string
  day_of_week: string
  total_sales_count: number
  total_sales_value: number
  avg_sale_value: number
}

export default function AnalyticsV2() {
  // ✅ Use dynamic UTC-based date range
  const today = new Date()
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(today.getDate() - 30)

  const start = thirtyDaysAgo.toISOString().slice(0, 10)
  const end = today.toISOString().slice(0, 10)

  const { data: kpis, isLoading: loadingKpis, error } = useKpiSummary(start, end)
  const [summary, setSummary] = useState<DailySalesSummary[]>([])

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await API.get("/analytics/sales-summary", {
          params: {
            start_date: start,
            end_date: end,
            granularity: "day",
          },
        })
        setSummary(res.data)
      } catch (err) {
        console.error("❌ Failed to fetch sales summary:", err)
      }
    }

    fetchSummary()
  }, [start, end])

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Analytics & Business Intelligence</h1>
        <p className="text-muted-foreground">Last 30 days ({start} → {end})</p>
      </div>

      {kpis ? <KpiGrid data={kpis} /> : <p className="text-muted">Loading KPIs...</p>}

      <Card>
        <CardContent className="p-6">
          <h2 className="text-lg font-semibold mb-4">Sales Trend</h2>
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary}>
                <XAxis
                  dataKey="sale_date"
                  tickFormatter={(d) => format(new Date(d), "MMM d")}
                />
                <YAxis />
                <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                <Line
                  type="monotone"
                  dataKey="total_sales_value"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6 space-y-2">
          <h2 className="text-lg font-semibold">Anchor AI Assistant</h2>
          <div className="border p-4 rounded bg-muted text-muted-foreground">
            <p><strong>Coming Soon:</strong> Ask questions like:</p>
            <ul className="list-disc list-inside pl-2">
              <li>"Which category had the highest sales last week?"</li>
              <li>"Show me return rates by cashier."</li>
              <li>"What were the top 5 margin products this month?"</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
