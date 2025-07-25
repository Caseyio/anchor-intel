// src/pages/Analytics.tsx
import { format } from "date-fns"
import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import API from "@/services/api"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

interface DailySalesSummary {
  sale_date: string
  day_of_week: string
  total_sales_count: number
  total_sales_value: number
  avg_sale_value: number
}

export default function Analytics() {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<DailySalesSummary[]>([])

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await API.get("/analytics/sales-summary", {
          params: {
            start_date: new Date(Date.now() - 30 * 86400000).toISOString().split("T")[0],
            end_date: new Date().toISOString().split("T")[0],
            granularity: "day",
          },
        })

        console.log("✅ Analytics response:", res.data)
        setSummary(res.data)
      } catch (err) {
        console.error("❌ Failed to fetch summary", err)
      } finally {
        setLoading(false)
      }
    }

    fetchSummary()
  }, [])

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Analytics & Business Intelligence</h1>
        <p className="text-muted-foreground">Last 30 days</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <h2 className="text-sm text-muted-foreground">Total Sales Value</h2>
            <p className="text-2xl font-bold">
              {loading ? <Loader2 className="animate-spin" /> : `$${summary.reduce((sum, d) => sum + d.total_sales_value, 0).toFixed(2)}`}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <h2 className="text-sm text-muted-foreground">Average Daily Sales</h2>
            <p className="text-2xl font-bold">
              {loading ? (
                <Loader2 className="animate-spin" />
              ) : (
                `$${(
                  summary.reduce((sum, d) => sum + d.avg_sale_value, 0) / summary.length
                ).toFixed(2)}`
              )}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <h2 className="text-sm text-muted-foreground">Days Tracked</h2>
            <p className="text-2xl font-bold">{summary.length}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-6">
          <h2 className="text-lg font-semibold mb-4">Sales Trend</h2>
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary}>
                <XAxis dataKey="sale_date" tickFormatter={(d) => format(new Date(d), "MMM d")} />
                <YAxis />
                <Tooltip formatter={(value) => `$${value}`} />
                <Line type="monotone" dataKey="total_sales_value" stroke="#10b981" strokeWidth={2} />
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
