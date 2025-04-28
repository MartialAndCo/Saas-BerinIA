"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { ArrowDown, ArrowUp, Bot, FolderOpen, Globe, MessageSquare, MoreHorizontal, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DashboardChart } from "@/components/dashboard/dashboard-chart"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { StatusCard } from "@/components/dashboard/status-card"
import { apiRequest } from "@/services/api-interceptor"
import { useAuth } from "@/lib/auth"

// Types pour les données du dashboard
interface DashboardData {
  campaigns: {
    active: number
    pending: number
    trend: "up" | "down" | "neutral"
    trendValue: string
  }
  leads: {
    total: number
    today: number
    trend: "up" | "down" | "neutral"
    trendValue: string
  }
  niches: {
    explored: number
    profitable: number
    trend: "up" | "down" | "neutral"
    trendValue: string
  }
  agents: {
    active: number
    total: number
    error: number
    trend: "up" | "down" | "neutral"
  }
}

interface RecentActivityItem {
  id: number
  type: "campaign" | "lead" | "niche" | "agent"
  action: string
  description: string
  timestamp: string
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [recentActivity, setRecentActivity] = useState<RecentActivityItem[]>([])
  const [conversionData, setConversionData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()

  // Récupérer les données du dashboard
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        
        // Récupérer les données générales du dashboard
        const dashboardResponse = await apiRequest('/dashboard/metrics')
        setDashboardData(dashboardResponse)
        
        // Récupérer les activités récentes
        const activityResponse = await apiRequest('/logs/recent')
        setRecentActivity(activityResponse)
        
        // Récupérer les données de conversion pour le graphique
        const conversionResponse = await apiRequest('/stats/conversion?period=30d')
        setConversionData(conversionResponse)
        
        setError(null)
      } catch (err) {
        console.error("Error fetching dashboard data:", err)
        setError("Unable to load dashboard data")
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) return <div className="p-4">Chargement du tableau de bord...</div>
  if (error) return <div className="p-4 text-red-500">Erreur: {error}</div>

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Vue d'ensemble</h2>
        <p className="text-muted-foreground">
          Bienvenue {user?.name || user?.email} sur le tableau de bord d'administration BerinIA.
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="analytics">Performances</TabsTrigger>
          <TabsTrigger value="reports">Rapports</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatusCard
              title="Campagnes actives"
              value={dashboardData?.campaigns?.active?.toString() || "0"}
              description={`${dashboardData?.campaigns?.pending || 0} campagnes en attente`}
              trend={dashboardData?.campaigns?.trend || "neutral"}
              trendValue={dashboardData?.campaigns?.trendValue || "0"}
              icon={<FolderOpen className="h-4 w-4 text-muted-foreground" />}
            />
            <StatusCard
              title="Leads collectés"
              value={(dashboardData?.leads?.total || 0).toString()}
              description="Aujourd'hui"
              trend={dashboardData?.leads?.trend || "neutral"}
              trendValue={dashboardData?.leads?.trendValue || "0%"}
              icon={<MessageSquare className="h-4 w-4 text-muted-foreground" />}
            />
            <StatusCard
              title="Niches explorées"
              value={dashboardData?.niches?.explored?.toString() || "0"}
              description={`${dashboardData?.niches?.profitable || 0} niches rentables`}
              trend={dashboardData?.niches?.trend || "neutral"}
              trendValue={dashboardData?.niches?.trendValue || "0"}
              icon={<Globe className="h-4 w-4 text-muted-foreground" />}
            />
            <StatusCard
              title="Agents actifs"
              value={`${dashboardData?.agents?.active || 0}/${dashboardData?.agents?.total || 0}`}
              description={`${dashboardData?.agents?.error || 0} agents en erreur`}
              trend={dashboardData?.agents?.trend || "neutral"}
              icon={<Bot className="h-4 w-4 text-muted-foreground" />}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <DashboardChart className="col-span-4" data={conversionData} />
            <RecentActivity className="col-span-3" data={recentActivity} />
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <Card className="col-span-3">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="space-y-1">
                  <CardTitle>Campagnes en cours</CardTitle>
                  <CardDescription>Statut des campagnes actives</CardDescription>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <span className="sr-only">Menu</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuItem>Voir toutes les campagnes</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>Créer une campagne</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: "Agences immobilières Paris", progress: 78, status: "active" },
                    { name: "Avocats d'affaires Lyon", progress: 45, status: "active" },
                    { name: "Architectes Bordeaux", progress: 92, status: "active" },
                    { name: "Consultants RH Lille", progress: 24, status: "warning" },
                    { name: "Cliniques vétérinaires", progress: 62, status: "active" },
                  ].map((campaign) => (
                    <div key={campaign.name} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div
                            className={`h-2 w-2 rounded-full ${
                              campaign.status === "active"
                                ? "bg-green-500"
                                : campaign.status === "warning"
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                            }`}
                          />
                          <span className="text-sm font-medium">{campaign.name}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">{campaign.progress}%</span>
                      </div>
                      <Progress value={campaign.progress} className="h-1" />
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full" asChild>
                  <Link href="/admin/campaigns">
                    <FolderOpen className="mr-2 h-4 w-4" />
                    Voir toutes les campagnes
                  </Link>
                </Button>
              </CardFooter>
            </Card>
            <Card className="col-span-4">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="space-y-1">
                  <CardTitle>Statut des agents</CardTitle>
                  <CardDescription>Activité et performance des agents IA</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <RefreshCw className="mr-2 h-3 w-3" />
                  Actualiser
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: "Scraper Agent", status: "active", lastRun: "Il y a 5 minutes", leads: 342 },
                    { name: "Cleaner Agent", status: "active", lastRun: "Il y a 12 minutes", leads: 342 },
                    { name: "Pivot Agent", status: "active", lastRun: "Il y a 30 minutes", leads: null },
                    { name: "Analytics Agent", status: "error", lastRun: "Il y a 1 heure", leads: null },
                    { name: "Outreach Agent", status: "active", lastRun: "Il y a 15 minutes", leads: 128 },
                    { name: "Monitoring Agent", status: "warning", lastRun: "Il y a 45 minutes", leads: null },
                  ].map((agent) => (
                    <div
                      key={agent.name}
                      className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3 last:border-0 last:pb-0"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className={`h-8 w-8 rounded-full flex items-center justify-center ${
                            agent.status === "active"
                              ? "bg-green-100 dark:bg-green-900"
                              : agent.status === "warning"
                                ? "bg-yellow-100 dark:bg-yellow-900"
                                : "bg-red-100 dark:bg-red-900"
                          }`}
                        >
                          <Bot
                            className={`h-4 w-4 ${
                              agent.status === "active"
                                ? "text-green-600 dark:text-green-400"
                                : agent.status === "warning"
                                  ? "text-yellow-600 dark:text-yellow-400"
                                  : "text-red-600 dark:text-red-400"
                            }`}
                          />
                        </div>
                        <div>
                          <p className="text-sm font-medium">{agent.name}</p>
                          <p className="text-xs text-muted-foreground">{agent.lastRun}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        {agent.leads !== null && <div className="text-sm font-medium">{agent.leads} leads</div>}
                        <Button
                          variant="ghost"
                          size="sm"
                          className={`h-8 ${
                            agent.status === "active"
                              ? "text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
                              : agent.status === "warning"
                                ? "text-yellow-600 hover:text-yellow-700 dark:text-yellow-400 dark:hover:text-yellow-300"
                                : "text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                          }`}
                        >
                          {agent.status === "active"
                            ? "Actif"
                            : agent.status === "warning"
                              ? "Avertissement"
                              : "Erreur"}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full" asChild>
                  <Link href="/dashboard/agents">
                    <Bot className="mr-2 h-4 w-4" />
                    Gérer les agents
                  </Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux de conversion</CardTitle>
                <div className="rounded-md bg-green-100 dark:bg-green-900 p-1">
                  <ArrowUp className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8.2%</div>
                <p className="text-xs text-muted-foreground">+2.1% par rapport au mois dernier</p>
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux d'ouverture</CardTitle>
                <div className="rounded-md bg-green-100 dark:bg-green-900 p-1">
                  <ArrowUp className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24.5%</div>
                <p className="text-xs text-muted-foreground">+4.3% par rapport au mois dernier</p>
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux de réponse</CardTitle>
                <div className="rounded-md bg-red-100 dark:bg-red-900 p-1">
                  <ArrowDown className="h-4 w-4 text-red-600 dark:text-red-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12.8%</div>
                <p className="text-xs text-muted-foreground">-1.5% par rapport au mois dernier</p>
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Coût par lead</CardTitle>
                <div className="rounded-md bg-green-100 dark:bg-green-900 p-1">
                  <ArrowDown className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2.35€</div>
                <p className="text-xs text-muted-foreground">-0.45€ par rapport au mois dernier</p>
              </CardContent>
            </Card>
          </div>
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Performances détaillées</CardTitle>
              <CardDescription>Analyse des performances par campagne et par niche</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Contenu détaillé des performances à venir...</p>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="reports" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Rapports générés</CardTitle>
              <CardDescription>Rapports hebdomadaires et mensuels</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Liste des rapports à venir...</p>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="notifications" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Notifications système</CardTitle>
              <CardDescription>Alertes et notifications importantes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-100 dark:border-red-800">
                  <div className="rounded-full bg-red-100 dark:bg-red-900 p-1">
                    <Bot className="h-4 w-4 text-red-600 dark:text-red-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Analytics Agent en erreur</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      L'agent Analytics a rencontré une erreur lors de l'analyse des données. Erreur: API timeout.
                    </p>
                    <div className="mt-2">
                      <Button size="sm" variant="outline" className="h-7 text-xs">
                        <RefreshCw className="mr-1 h-3 w-3" />
                        Relancer l'agent
                      </Button>
                    </div>
                  </div>
                </div>
                <div className="flex items-start space-x-4 rounded-md bg-yellow-50 dark:bg-yellow-900/20 p-4 border border-yellow-100 dark:border-yellow-800">
                  <div className="rounded-full bg-yellow-100 dark:bg-yellow-900 p-1">
                    <Bot className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Monitoring Agent: Avertissement</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Le taux de réponse pour la campagne "Consultants RH Lille" est inférieur au seuil défini.
                    </p>
                    <div className="mt-2">
                      <Button size="sm" variant="outline" className="h-7 text-xs">
                        Voir la campagne
                      </Button>
                    </div>
                  </div>
                </div>
                <div className="flex items-start space-x-4 rounded-md bg-green-50 dark:bg-green-900/20 p-4 border border-green-100 dark:border-green-800">
                  <div className="rounded-full bg-green-100 dark:bg-green-900 p-1">
                    <Bot className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Pivot Agent: Recommandation</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      La niche "Architectes Bordeaux" montre un excellent potentiel. Recommandation d'augmenter le
                      budget.
                    </p>
                    <div className="mt-2">
                      <Button size="sm" variant="outline" className="h-7 text-xs">
                        Appliquer la recommandation
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
