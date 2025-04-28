import Link from "next/link"
import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface DashboardButtonProps {
  href: string
  icon: LucideIcon
  label: string
  active?: boolean
  className?: string
}

export default function DashboardButton({ href, icon: Icon, label, active = false, className }: DashboardButtonProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-xl bg-white text-gray-700 shadow-[0_0_10px_rgba(0,0,0,0.08)] border border-gray-100 transition-all duration-200",
        "dark:bg-gray-900 dark:text-gray-200 dark:border-gray-800 dark:shadow-[0_0_10px_rgba(0,0,0,0.15)]",
        "hover:shadow-[0_0_12px_rgba(0,0,0,0.12)] dark:hover:shadow-[0_0_12px_rgba(0,0,0,0.2)]",
        active && "bg-gray-50 dark:bg-gray-800",
        className,
      )}
    >
      <Icon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
      <span className="font-medium">{label}</span>
    </Link>
  )
}
