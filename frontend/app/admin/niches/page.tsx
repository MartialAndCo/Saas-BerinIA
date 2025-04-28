"use client"

import { useEffect, useState } from "react"
import { ArrowDown, ArrowUp, BarChart3, Globe, MoreHorizontal, Plus, RefreshCw, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { NichePerformanceChart } from "@/components/dashboard/niche-performance-chart"
import { apiRequest } from "@/services/api-interceptor"
import { toast } from "@/components/ui/use-toast"
import { CreateNicheDialog } from "@/components/niches/create-niche-dialog"

// Type pour les données de niche
interface Niche {
  id: number
  nom: string
  description: string
  statut: string
  taux_conversion: number
  cout_par_lead: number
  recommandation: string
  date_creation: string
  campaigns?: any[]
  leads?: any[]
}

// Définissez d'abord l'interface pour les données du formulaire
interface NicheFormData {
  nom: string;
  description: string;
  statut: string;
  taux_conversion: number;
  cout_par_lead: number;
  recommandation: string;
}

export default function NichesPage() {
  const [niches, setNiches] = useState<Niche[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filteredNiches, setFilteredNiches] = useState<Niche[]>([])
  const [searchQuery, setSearchQuery] = useState("")

  // Récupérer les données des niches depuis l'API
  useEffect(() => {
    const fetchNiches = async () => {
      try {
        setLoading(true)
        const response = await apiRequest('/niches')
        setNiches(response)
        setFilteredNiches(response)
        setError(null)
      } catch (err) {
        console.error("Error fetching niches:", err)
        setError("Impossible de charger les niches")
      } finally {
        setLoading(false)
      }
    }

    fetchNiches()
  }, [])

  // Ajout de la fonction pour actualiser les niches
  const refreshNiches = async () => {
    setLoading(true)
    try {
      const response = await apiRequest('/niches')
      setNiches(response)
      setFilteredNiches(response)
    } catch (error) {
      console.error("Error fetching niches:", error)
      setError("Impossible de charger les niches")
    } finally {
      setLoading(false)
    }
  }

  // Ajout de la fonction pour rechercher des niches
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  // Filtrer les niches en fonction de la recherche
  useEffect(() => {
    if (searchQuery.trim() === "") {
      // Si la recherche est vide, on utilise toutes les niches
      setFilteredNiches(niches)
    } else {
      // Sinon, on filtre les niches par nom
      const filtered = niches.filter(niche => 
        niche.nom.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredNiches(filtered)
    }
  }, [niches, searchQuery])

  // Fonction pour traduire le statut en anglais (pour les classes CSS)
  const getStatusClass = (statut: string) => {
    switch (statut) {
      case "Rentable": return "profitable"
      case "En test": return "testing"
      case "Abandonnée": return "abandoned"
      default: return "testing"
    }
  }

  // Fonction pour traduire la recommandation en anglais (pour les classes CSS)
  const getRecommendationClass = (recommandation: string) => {
    switch (recommandation) {
      case "Continuer": return "continue"
      case "Développer": return "scale"
      case "Optimiser": return "optimize"
      case "Pivoter": return "pivot"
      default: return "continue"
    }
  }

  // Dans la fonction handleCreateNiche
  const handleCreateNiche = async (formData: NicheFormData) => {
    try {
      await apiRequest('/niches', {
        method: 'POST',
        body: JSON.stringify(formData)
      })
      
      toast({
        title: "Niche créée",
        description: `La niche "${formData.nom}" a été créée avec succès.`
      })
      
      refreshNiches()
    } catch (error) {
      console.error("Error creating niche:", error)
      toast({
        title: "Erreur",
        description: "Impossible de créer la niche",
        variant: "destructive"
      })
    }
  }

  // Dans la fonction handleUpdateNiche
  const handleUpdateNiche = async (id: number, data: any) => {
    try {
      const response = await apiRequest(`/niches/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      
      // Mettre à jour la liste des niches
      setNiches(
        niches.map((niche) => (niche.id === id ? response : niche))
      )
      
      toast({
        title: "Niche mise à jour",
        description: `La niche a été mise à jour avec succès.`,
      })
    } catch (error) {
      console.error("Error updating niche:", error)
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour la niche",
        variant: "destructive",
      })
    }
  }

  if (loading) return <div className="p-4">Chargement des niches...</div>
  if (error) return <div className="p-4 text-red-500">Erreur: {error}</div>

  // Filtrer les niches par statut
  const profitableNiches = niches.filter(niche => niche.statut === "Rentable")
  const testingNiches = niches.filter(niche => niche.statut === "En test")
  const abandonedNiches = niches.filter(niche => niche.statut === "Abandonnée")

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Niches</h2>
          <p className="text-muted-foreground">Analysez les performances des niches et suivez les recommandations.</p>
        </div>
        <CreateNicheDialog onNicheCreated={refreshNiches} />
      </div>

      <div className="flex items-center space-x-2">
        <Input
          placeholder="Rechercher une niche..."
          value={searchQuery}
          onChange={handleSearch}
          className="max-w-sm"
        />
        <Button variant="outline" onClick={refreshNiches}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Actualiser
        </Button>
      </div>

      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">Toutes</TabsTrigger>
          <TabsTrigger value="profitable">Rentables</TabsTrigger>
          <TabsTrigger value="testing">En test</TabsTrigger>
          <TabsTrigger value="abandoned">Abandonnées</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Niches analysées</CardTitle>
                <Globe className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8</div>
                <p className="text-xs text-muted-foreground">3 niches rentables identifiées</p>
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux de conversion moyen</CardTitle>
                <div className="rounded-md bg-green-100 dark:bg-green-900 p-1">
                  <ArrowUp className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">6.8%</div>
                <p className="text-xs text-muted-foreground">+1.2% par rapport au mois dernier</p>
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Coût par lead moyen</CardTitle>
                <div className="rounded-md bg-green-100 dark:bg-green-900 p-1">
                  <ArrowDown className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2.35€</div>
                <p className="text-xs text-muted-foreground">-0.45€ par rapport au mois dernier</p>
              </CardContent>
            </Card>
            <Card className="w-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Décisions de pivot</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">5</div>
                <p className="text-xs text-muted-foreground">2 pivots ce mois-ci</p>
              </CardContent>
            </Card>
          </div>

          <Card className="w-full">
            <CardHeader>
              <CardTitle>Performance des niches</CardTitle>
              <CardDescription>Comparaison des taux de conversion et coûts par lead</CardDescription>
            </CardHeader>
            <CardContent>
              <NichePerformanceChart />
            </CardContent>
          </Card>

          <Card className="w-full">
            <CardHeader className="py-4">
              <CardTitle>Liste des niches</CardTitle>
              <CardDescription>Toutes les niches analysées et leur performance</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Campagnes</TableHead>
                    <TableHead>Leads</TableHead>
                    <TableHead>Taux de conversion</TableHead>
                    <TableHead>Coût par lead</TableHead>
                    <TableHead>Recommandation</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredNiches.map((niche) => (
                    <TableRow key={niche.id}>
                      <TableCell className="font-medium">{niche.nom || "Sans nom"}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            niche.statut === "profitable"
                              ? "default"
                              : niche.statut === "testing"
                                ? "secondary"
                                : "outline"
                          }
                          className={
                            niche.statut === "profitable"
                              ? "bg-green-500 hover:bg-green-600"
                              : niche.statut === "testing"
                                ? "bg-blue-500 hover:bg-blue-600"
                                : "border-red-500 text-red-500"
                          }
                        >
                          {niche.statut || "En test"}
                        </Badge>
                      </TableCell>
                      <TableCell>{niche.campaigns ? niche.campaigns.length : 0}</TableCell>
                      <TableCell>{niche.leads ? niche.leads.length : 0}</TableCell>
                      <TableCell>{niche.taux_conversion !== undefined ? niche.taux_conversion : 0}%</TableCell>
                      <TableCell>{niche.cout_par_lead !== undefined ? niche.cout_par_lead : 0}€</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                              ? "default"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                                ? "secondary"
                                : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                  ? "outline"
                                  : "destructive"
                          }
                          className={
                            getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                              ? "bg-green-500 hover:bg-green-600"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                                ? "bg-blue-500 hover:bg-blue-600"
                                : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                  ? "border-yellow-500 text-yellow-500"
                                  : "bg-red-500 hover:bg-red-600"
                          }
                        >
                          {niche.recommandation || "Continuer"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem>
                              <BarChart3 className="mr-2 h-4 w-4" />
                              Voir les détails
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Globe className="mr-2 h-4 w-4" />
                              Voir les campagnes
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Zap className="mr-2 h-4 w-4" />
                              Appliquer la recommandation
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="profitable" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Niches rentables</CardTitle>
              <CardDescription>Niches avec un bon retour sur investissement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                {profitableNiches.map((niche) => (
                  <div key={niche.id} className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{niche.nom || "Sans nom"}</h3>
                      <p className="text-sm text-gray-500">
                        {niche.campaigns ? niche.campaigns.length : 0} campagne{niche.campaigns && niche.campaigns.length > 1 ? 's' : ''} • {niche.leads ? niche.leads.length : 0} leads
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="font-medium">{niche.taux_conversion !== undefined ? niche.taux_conversion : 0}%</p>
                        <p className="text-sm text-gray-500">Taux de conversion</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{niche.cout_par_lead !== undefined ? niche.cout_par_lead : 0}€</p>
                        <p className="text-sm text-gray-500">Coût par lead</p>
                      </div>
                      <Badge
                        variant={
                          getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                            ? "default"
                            : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                              ? "secondary"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                ? "outline"
                                : "destructive"
                        }
                        className={
                          getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                            ? "bg-green-500 hover:bg-green-600"
                            : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                              ? "bg-blue-500 hover:bg-blue-600"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                ? "border-yellow-500 text-yellow-500"
                                : "bg-red-500 hover:bg-red-600"
                        }
                      >
                        {niche.recommandation || "Continuer"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="testing" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Niches en test</CardTitle>
              <CardDescription>Niches en cours d'évaluation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                {testingNiches.map((niche) => (
                  <div key={niche.id} className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{niche.nom || "Sans nom"}</h3>
                      <p className="text-sm text-gray-500">
                        {niche.campaigns ? niche.campaigns.length : 0} campagne{niche.campaigns && niche.campaigns.length > 1 ? 's' : ''} • {niche.leads ? niche.leads.length : 0} leads
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="font-medium">{niche.taux_conversion !== undefined ? niche.taux_conversion : 0}%</p>
                        <p className="text-sm text-gray-500">Taux de conversion</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{niche.cout_par_lead !== undefined ? niche.cout_par_lead : 0}€</p>
                        <p className="text-sm text-gray-500">Coût par lead</p>
                      </div>
                      <Badge
                        variant={
                          getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                            ? "default"
                            : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                              ? "secondary"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                ? "outline"
                                : "destructive"
                        }
                        className={
                          getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                            ? "bg-green-500 hover:bg-green-600"
                            : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                              ? "bg-blue-500 hover:bg-blue-600"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                ? "border-yellow-500 text-yellow-500"
                                : "bg-red-500 hover:bg-red-600"
                        }
                      >
                        {niche.recommandation || "Continuer"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="abandoned" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Niches abandonnées</CardTitle>
              <CardDescription>Niches non rentables ou pivotées</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                {abandonedNiches.map((niche) => (
                  <div key={niche.id} className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{niche.nom || "Sans nom"}</h3>
                      <p className="text-sm text-gray-500">
                        {niche.campaigns ? niche.campaigns.length : 0} campagne{niche.campaigns && niche.campaigns.length > 1 ? 's' : ''} • {niche.leads ? niche.leads.length : 0} leads
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="font-medium">{niche.taux_conversion !== undefined ? niche.taux_conversion : 0}%</p>
                        <p className="text-sm text-gray-500">Taux de conversion</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{niche.cout_par_lead !== undefined ? niche.cout_par_lead : 0}€</p>
                        <p className="text-sm text-gray-500">Coût par lead</p>
                      </div>
                      <Badge
                        variant={
                          getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                            ? "default"
                            : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                              ? "secondary"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                ? "outline"
                                : "destructive"
                        }
                        className={
                          getRecommendationClass(niche.recommandation || "Continuer") === "scale" 
                            ? "bg-green-500 hover:bg-green-600"
                            : getRecommendationClass(niche.recommandation || "Continuer") === "continue" 
                              ? "bg-blue-500 hover:bg-blue-600"
                              : getRecommendationClass(niche.recommandation || "Continuer") === "optimize" 
                                ? "border-yellow-500 text-yellow-500"
                                : "bg-red-500 hover:bg-red-600"
                        }
                      >
                        {niche.recommandation || "Continuer"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
