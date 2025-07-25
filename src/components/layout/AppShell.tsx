// components/AppShell.tsx
import { ReactNode, useEffect, useState } from "react"
import { useLocation, Link } from "react-router-dom"
import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import API from "@/services/api"

interface AppShellProps {
  children: ReactNode
  className?: string
}

const navItems = [
  { name: "Dashboard", to: "/dashboard" },
  { name: "POS", to: "/pos" },
  { name: "Returns", to: "/return" },
  { name: "Receipt Lookup", to: "/receipt/search" },
  //{ name: "Reports", to: "/manager-closeout" },
]

interface CashierSession {
  cashier_id: number
  terminal_id?: string
  opened_at: string
  closed_at?: string
}

export function AppShell({ children, className }: AppShellProps) {
  const location = useLocation()
  const [session, setSession] = useState<CashierSession | null>(null)

  useEffect(() => {
  const fetchSession = async () => {
    const token = localStorage.getItem("token")
    if (!token) return // 👈 Skip call if not logged in

    try {
      const res = await API.get("/cashier_sessions/current")
      setSession(res.data)
    } catch {
      setSession(null)
    }
  }
  fetchSession()
}, [])

  return (
    <div className="min-h-screen bg-gradient-to-bl from-yellow-100 via-orange-120 to-blue-300 text-foreground flex flex-col">
      {/* Top Navigation */}
      <header className="h-16 border-b px-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">Anchor POS</h1>
        {session ? (
          <div className="text-sm text-muted-foreground">
            <span className="font-medium text-foreground">
              Cashier #{session.cashier_id}
            </span>{" "}
            on{" "}
            <span className="font-mono">
              {session.terminal_id || "Terminal"}
            </span>
          </div>
        ) : (
          <div className="text-sm text-red-500 font-medium">No session</div>
        )}
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar (visible on md and up) */}
        <aside className="hidden md:flex md:flex-col md:w-64 border-r px-4 py-6">
          <nav className="space-y-2">
            {navItems.map(({ name, to }) => (
              <Link
                key={to}
                to={to}
                className={cn(
                  "block px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  location.pathname === to
                    ? "bg-muted text-foreground"
                    : "text-muted-foreground hover:bg-muted"
                )}
              >
                {name}
              </Link>
            ))}
          </nav>
        </aside>

        {/* Scrollable Content */}
        <main className={cn("flex-1 overflow-hidden", className)}>
          <ScrollArea className="h-full px-4 py-6">
            <div className="bg-white/80 backdrop-blur-md rounded-xl shadow-xl p-6 max-w-4xl mx-auto">
              {children}
            </div>
          </ScrollArea>
        </main>

      </div>
    </div>
  )
}
