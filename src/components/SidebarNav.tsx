// components/SidebarNav.tsx
import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"

const navItems = [
  { name: "POS", to: "/" },
  { name: "Returns", to: "/returns" },
  { name: "Lookup", to: "/lookup" },
  { name: "Reports", to: "/reports" },
]

export function SidebarNav() {
  const location = useLocation()

  return (
    <nav className="space-y-2 px-4 py-6">
      {navItems.map(({ name, to }) => (
        <Link
          key={to}
          to={to}
          className={cn(
            "block text-sm font-medium px-3 py-2 rounded-md transition-colors",
            location.pathname === to
              ? "bg-muted text-foreground"
              : "text-muted-foreground hover:bg-muted"
          )}
        >
          {name}
        </Link>
      ))}
    </nav>
  )
}
