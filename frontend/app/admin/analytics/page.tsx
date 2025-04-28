"use client"

import { useState, useEffect } from "react"
import { ArrowDown, ArrowUp, BarChart3, Calendar, Download, Filter, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ConversionChart } from "@/components/dashboard/conversion-chart"
import { LeadsChart } from "@/components/dashboard/leads-chart"
import { CampaignComparisonChart } from "@/components/dashboard/campaign-comparison-chart"
import { NicheComparisonChart } from "@/components/dashboard/niche-comparison-chart"
import { apiRequest } from "@/services/api-interceptor"
import { toast } from "@/components/ui/use-toast"

// Types pour les statistiques
interface OverviewStats {
  leadsCollected: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  conversionRate: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  openRate: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
  costPerLead: {
    value: number
    change: number
    trend: "up" | "down" | "neutral"
  }
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [conversionData, setConversionData] = useState([])
  const [leadsData, setLeadsData] = useState([])
  const [campaignsData, setCampaignsData] = useState([])
  const [nichesData, setNichesData] = useState([])
  const [period, setPeriod] = useState("30d")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Récupérer les statistiques générales
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await apiRequest('/stats/overview')
        setStats(response)
        setError(null)
      } catch (err) {
        console.error("Error fetching stats:", err)
        setError("Unable to load statistics")
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  // Récupérer les données pour les graphiques en fonction de la période
  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setLoading(true)
        
        // Utilisation de Promise.all pour charger les données en parallèle
        const [conv, leads, camps, niches] = await Promise.all([
          apiRequest(`/stats/conversion?period=${period}`),
          apiRequest(`/stats/leads?period=${period}`),
          apiRequest(`/stats/campaigns?period=${period}`),
          apiRequest(`/stats/niches?period=${period}`)
        ])
        
        setConversionData(conv)
        setLeadsData(leads)
        setCampaignsData(camps)
        setNichesData(niches)
        
        setError(null)
      } catch (err) {
        console.error("Error fetching chart data:", err)
        setError("Unable to load chart data")
      } finally {
        setLoading(false)
      }
    }

    fetchChartData()
  }, [period])

  // Gérer le changement de période
  const handlePeriodChange = (value: string) => {
    setPeriod(value)
  }

  // Gérer l'actualisation des données
  const handleRefresh = async () => {
    try {
      setLoading(true)
      
      // Récupérer les statistiques générales et les données pour les graphiques en parallèle
      const [statsResponse, conv, leads, camps, niches] = await Promise.all([
        apiRequest('/stats/overview'),
        apiRequest(`/stats/conversion?period=${period}`),
        apiRequest(`/stats/leads?period=${period}`),
        apiRequest(`/stats/campaigns?period=${period}`),
        apiRequest(`/stats/niches?period=${period}`)
      ])
      
      setStats(statsResponse)
      setConversionData(conv)
      setLeadsData(leads)
      setCampaignsData(camps)
      setNichesData(niches)
      
      setError(null)
      
      toast({
        title: "Données actualisées",
        description: "Les statistiques ont été actualisées avec succès.",
      })
    } catch (err) {
      console.error("Error refreshing data:", err)
      setError("Unable to refresh data")
      
      toast({
        title: "Erreur",
        description: "Impossible d'actualiser les données",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  // Gérer l'export des données
  const handleExport = async () => {
    try {
      await apiRequest(`/stats/export?period=${period}`, {
        method: 'GET',
      })
      
      toast({
        title: "Export des données",
        description: "Les statistiques ont été exportées avec succès.",
      })
    } catch (error) {
      console.error("Error exporting stats:", error)
      toast({
        title: "Erreur",
        description: "Impossible d'exporter les statistiques",
        variant: "destructive",
      })
    }
  }

  if (loading && !stats) return <div className="p-4">Chargement des statistiques...</div>
  if (error && !stats) return <div className="p-4 text-red-500">Erreur: {error}</div>

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Statistiques</h2>
          <p className="text-muted-foreground">Analysez les performances de vos campagnes et niches.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Calendar className="mr-2 h-4 w-4" />
            Période
          </Button>
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            Filtres
          </Button>
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Actualiser
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Exporter
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="w-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Leads collectés</CardTitle>
            <div className={`rounded-md ${stats?.leadsCollected.trend === 'up' ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} p-1`}>
              {stats?.leadsCollected.trend === 'up' ? (
                <ArrowUp className="h-4 w-4 text-green-600 dark:text-green-400" />
              ) : (
                <ArrowDown className="h-4 w-4 text-red-600 dark:text-red-400" />
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.leadsCollected.value}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.leadsCollected?.change !== undefined ? (
                <>
                  {stats.leadsCollected.change > 0 ? '+' : ''}
                  {stats.leadsCollected.change}% par rapport au mois dernier
                </>
              ) : (
                '0% par rapport au mois dernier'
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="w-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taux de conversion</CardTitle>
            <div className={`rounded-md ${stats?.conversionRate.trend === 'up' ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} p-1`}>
              {stats?.conversionRate.trend === 'up' ? (
                <ArrowUp className="h-4 w-4 text-green-600 dark:text-green-400" />
              ) : (
                <ArrowDown className="h-4 w-4 text-red-600 dark:text-red-400" />
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.conversionRate.value}%</div>
            <p className="text-xs text-muted-foreground">
              {stats?.conversionRate?.change !== undefined ? (
                <>
                  {stats.conversionRate.change > 0 ? '+' : ''}
                  {stats.conversionRate.change}% par rapport au mois dernier
                </>
              ) : (
                '0% par rapport au mois dernier'
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="w-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taux d'ouverture</CardTitle>
            <div className={`rounded-md ${stats?.openRate.trend === 'up' ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} p-1`}>
              {stats?.openRate.trend === 'up' ? (
                <ArrowUp className="h-4 w-4 text-green-600 dark:text-green-400" />
              ) : (
                <ArrowDown className="h-4 w-4 text-red-600 dark:text-red-400" />
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.openRate.value}%</div>
            <p className="text-xs text-muted-foreground">
              {stats?.openRate?.change !== undefined ? (
                <>
                  {stats.openRate.change > 0 ? '+' : ''}
                  {stats.openRate.change}% par rapport au mois dernier
                </>
              ) : (
                '0% par rapport au mois dernier'
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="w-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Coût par lead</CardTitle>
            <div className={`rounded-md ${stats?.costPerLead.trend === 'down' ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} p-1`}>
              {stats?.costPerLead.trend === 'down' ? (
                <ArrowDown className="h-4 w-4 text-green-600 dark:text-green-400" />
              ) : (
                <ArrowUp className="h-4 w-4 text-red-600 dark:text-red-400" />
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.costPerLead.value}€</div>
            <p className="text-xs text-muted-foreground">
              {stats?.costPerLead.trend === 'down' ? '-' : '+'}{Math.abs(stats?.costPerLead.change || 0)}€ par rapport au mois dernier
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="campaigns">Campagnes</TabsTrigger>
          <TabsTrigger value="niches">Niches</TabsTrigger>
          <TabsTrigger value="leads">Leads</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Taux de conversion</CardTitle>
                  <CardDescription>Évolution du taux de conversion sur les 30 derniers jours</CardDescription>
                </div>
                <Select defaultValue={period} onValueChange={handlePeriodChange}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="Période" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7d">7 jours</SelectItem>
                    <SelectItem value="30d">30 jours</SelectItem>
                    <SelectItem value="90d">90 jours</SelectItem>
                    <SelectItem value="1y">1 an</SelectItem>
                  </SelectContent>
                </Select>
              </CardHeader>
              <CardContent>
                {Array.isArray(conversionData) && conversionData.length > 0 ? (
                  <ConversionChart data={conversionData} />
                ) : (
                  <div className="text-sm text-muted-foreground">Aucune donnée de conversion disponible.</div>
                )}
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Leads collectés</CardTitle>
                  <CardDescription>Nombre de leads collectés par jour</CardDescription>
                </div>
                <Select defaultValue={period} onValueChange={handlePeriodChange}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="Période" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7d">7 jours</SelectItem>
                    <SelectItem value="30d">30 jours</SelectItem>
                    <SelectItem value="90d">90 jours</SelectItem>
                    <SelectItem value="1y">1 an</SelectItem>
                  </SelectContent>
                </Select>
              </CardHeader>
              <CardContent>
                {Array.isArray(leadsData) && leadsData.length > 0 ? (
                  <LeadsChart data={leadsData} />
                ) : (
                  <div className="text-sm text-muted-foreground">Aucune donnée de leads disponible.</div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="campaigns" className="space-y-4">
          <Card className="w-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Comparaison des campagnes</CardTitle>
                <CardDescription>Performance des campagnes actives</CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <BarChart3 className="mr-2 h-4 w-4" />
                Voir le détail
              </Button>
            </CardHeader>
            <CardContent>
              {Array.isArray(campaignsData) && campaignsData.length > 0 ? (
                <CampaignComparisonChart data={campaignsData} />
              ) : (
                <div className="text-sm text-muted-foreground">Aucune donnée de campagne disponible.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="niches" className="space-y-4">
          <Card className="w-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Comparaison des niches</CardTitle>
                <CardDescription>Performance des niches par taux de conversion et coût</CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <BarChart3 className="mr-2 h-4 w-4" />
                Voir le détail
              </Button>
            </CardHeader>
            <CardContent>
              {Array.isArray(nichesData) && nichesData.length > 0 ? (
                <NicheComparisonChart data={nichesData} />
              ) : (
                <div className="text-sm text-muted-foreground">Aucune donnée de niche disponible.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="leads" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Analyse des leads</CardTitle>
              <CardDescription>Répartition et qualité des leads collectés</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <p className="text-muted-foreground">Chargement des données...</p>
                </div>
              ) : error ? (
                <div className="h-[300px] flex items-center justify-center">
                  <p className="text-red-500">Erreur: {error}</p>
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  Graphiques d'analyse des leads à venir...
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
