// src/components/KpiGrid.tsx
import { Card, CardContent } from "@/components/ui/card"
import { KpiSummary } from "@/schemas/KpiSummary"
import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Info } from "lucide-react"




type Props = {
  data: KpiSummary;
};

export function KpiGrid({ data }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="grid md:grid-cols-3 gap-4">
      {/* Total Sales with Modal + Tooltip */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm text-muted-foreground flex items-center gap-1">
              Total Sales
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Info className="w-4 h-4 cursor-pointer text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    Total dollar value of all sales in the selected period.
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </h2>
          </div>
          <p
            className="text-2xl font-bold cursor-pointer hover:underline"
            onClick={() => setOpen(true)}
          >
            ${data.total_sales.toFixed(2)}
          </p>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Total Sales</DialogTitle>
              </DialogHeader>
              <p>
                This represents the total amount of sales completed within the selected time frame. It includes all transactions before returns and discounts.
              </p>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Avg Daily Sales */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-sm text-muted-foreground">Avg Daily Sales</h2>
          <p className="text-2xl font-bold">${data.avg_daily_sales.toFixed(2)}</p>
        </CardContent>
      </Card>

      {/* Transactions */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-sm text-muted-foreground">Transactions</h2>
          <p className="text-2xl font-bold">{data.total_transactions}</p>
        </CardContent>
      </Card>

      {/* Avg Basket Size */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-sm text-muted-foreground">Avg Basket Size</h2>
          <p className="text-2xl font-bold">{data.avg_basket_size.toFixed(2)}</p>
        </CardContent>
      </Card>

      {/* Return Rate */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-sm text-muted-foreground">Return Rate</h2>
          <p className="text-2xl font-bold">{data.return_rate.toFixed(2)}%</p>
        </CardContent>
      </Card>

      {/* Top Category */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-sm text-muted-foreground">Top Category</h2>
          <p className="text-2xl font-bold">{data.top_category}</p>
        </CardContent>
      </Card>
    </div>
  );
}
