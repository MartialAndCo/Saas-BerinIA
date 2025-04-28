"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import {
  BarChart3,
  Bot,
  Calendar,
  ChevronDown,
  Cog,
  FolderOpen,
  Globe,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Shield,
  Users,
  Mail,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Sheet, SheetContent } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar"
import { AuthGuard } from "@/components/auth/auth-guard"
import { useAuth } from "@/lib/auth"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const pathname = usePathname()
  const { logout } = useAuth()

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileOpen(false)
  }, [pathname])

  // Mettre à jour les chemins de navigation
  const navigation = [
    {
      name: "Vue d'ensemble",
      href: "/admin",
      icon: LayoutDashboard,
      current: pathname === "/admin",
    },
    {
      name: "Campagnes",
      href: "/admin/campaigns",
      icon: FolderOpen,
      current: pathname === "/admin/campaigns",
    },
    {
      name: "Leads",
      href: "/admin/leads",
      icon: MessageSquare,
      current: pathname === "/admin/leads",
    },
    {
      name: "Messagerie",
      href: "/admin/messaging",
      icon: Mail,
      current: pathname === "/admin/messaging",
    },
    {
      name: "Agents",
      href: "/admin/agents",
      icon: Bot,
      current: pathname === "/admin/agents",
    },
    {
      name: "Niches",
      href: "/admin/niches",
      icon: Globe,
      current: pathname === "/admin/niches",
    },
    {
      name: "Statistiques",
      href: "/admin/analytics",
      icon: BarChart3,
      current: pathname === "/admin/analytics",
    },
    {
      name: "Tests & Logs",
      href: "/admin/logs",
      icon: Calendar,
      current: pathname === "/admin/logs",
    },
    {
      name: "Paramètres",
      href: "/admin/settings",
      icon: Cog,
      current: pathname === "/admin/settings",
    },
    {
      name: "Utilisateurs",
      href: "/admin/users",
      icon: Users,
      current: pathname === "/admin/users",
    },
    {
      name: "Sécurité",
      href: "/admin/security",
      icon: Shield,
      current: pathname === "/admin/security",
    },
  ]

  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
        <SidebarProvider>
          {/* Desktop sidebar */}
          <Sidebar className="hidden md:flex">
            <SidebarHeader className="p-4">
              <Link href="/" className="flex items-center space-x-2">
                <Image src="/images/logo.png" alt="BerinIA Logo" width={140} height={40} className="h-8 w-auto" />
              </Link>
            </SidebarHeader>
            <SidebarContent>
              <SidebarGroup>
                <SidebarGroupLabel>Menu principal</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {navigation.map((item) => (
                      <SidebarMenuItem key={item.name}>
                        <SidebarMenuButton asChild isActive={item.current}>
                          <Link href={item.href}>
                            <item.icon className="h-5 w-5" />
                            <span>{item.name}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            </SidebarContent>
            <SidebarFooter className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-sm font-medium">AD</span>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Admin</p>
                    <p className="text-gray-500 dark:text-gray-400 text-xs">admin@berinia.com</p>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Mon compte</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>Profil</DropdownMenuItem>
                    <DropdownMenuItem>Paramètres</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => logout()}>
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Déconnexion</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </SidebarFooter>
          </Sidebar>

          {/* Mobile sidebar */}
          <Sheet open={isMobileOpen} onOpenChange={setIsMobileOpen}>
            <SheetContent side="left" className="p-0 w-64">
              <div className="flex flex-col h-full">
                <div className="p-4 border-b">
                  <Link href="/" className="flex items-center space-x-2">
                    <Image src="/images/logo.png" alt="BerinIA Logo" width={140} height={40} className="h-8 w-auto" />
                  </Link>
                </div>
                <div className="flex-1 overflow-auto py-2">
                  <nav className="grid gap-1 px-2">
                    {navigation.map((item) => (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={cn(
                          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium",
                          item.current
                            ? "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-50"
                            : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800",
                        )}
                      >
                        <item.icon className="h-5 w-5" />
                        {item.name}
                      </Link>
                    ))}
                  </nav>
                </div>
                <div className="p-4 border-t">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-sm font-medium">AD</span>
                      </div>
                      <div className="text-sm">
                        <p className="font-medium">Admin</p>
                        <p className="text-gray-500 dark:text-gray-400 text-xs">admin@berinia.com</p>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => logout()}>
                      <LogOut className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </SheetContent>
          </Sheet>

          {/* Main content */}
          <div className="flex flex-col flex-1">
            {/* Header */}
            <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
              <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setIsMobileOpen(true)}>
                <Menu className="h-6 w-6" />
                <span className="sr-only">Toggle menu</span>
              </Button>
              <div className="flex-1">
                <h1 className="text-lg font-semibold">Administration BerinIA</h1>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
                  size="sm"
                >
                  <Bot className="mr-2 h-4 w-4" />
                  Lancer un agent
                </Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="rounded-full">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-sm font-medium">AD</span>
                      </div>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Mon compte</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>Profil</DropdownMenuItem>
                    <DropdownMenuItem>Paramètres</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => logout()}>
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Déconnexion</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </header>

            {/* Page content */}
            <main className="flex-1 p-4 md:p-6 overflow-auto">{children}</main>
          </div>
        </SidebarProvider>
      </div>
    </AuthGuard>
  )
}
