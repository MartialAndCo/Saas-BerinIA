"use client"

import type React from "react"

import { useState, useEffect } from "react"
import {
  Bot,
  Clock,
  Download,
  Edit,
  Eye,
  MoreHorizontal,
  Play,
  Plus,
  Trash2,
  RefreshCw,
  Search,
  Filter,
} from "lucide-react"
import { Button } from "../../../components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
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
import { Progress } from "@/components/ui/progress"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/use-toast"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { apiRequest } from "@/services/api-interceptor"

// Types
interface Campaign {
  id: number
  nom: string
  description: string
  statut: string
  niche_id: number
  target_leads: number
  agent: string
  date_creation: string
  leads: number
  conversion: number
  progress: number
  niche: string
  date: string
  agent: string
  targetLeads?: number
}

export default function CampaignsPage() {
  // États
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [filteredCampaigns, setFilteredCampaigns] = useState<Campaign[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("all")
  const [isLoading, setIsLoading] = useState(true)
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false)
  const [isNewCampaignDialogOpen, setIsNewCampaignDialogOpen] = useState(false)
  const [editForm, setEditForm] = useState({
    id: 0,
    name: "",
    description: "",
    targetLeads: 0,
    agent: ""
  })
  const [newCampaignForm, setNewCampaignForm] = useState({
    name: "",
    niche: "",
    description: "",
    targetLeads: 500,
    agent: "Scraper Agent",
  })
  const [niches, setNiches] = useState<{ id: number; nom: string }[]>([])

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const itemsPerPage = 8

  // Données mockées pour les campagnes
  const mockCampaigns: Campaign[] = [
    {
      id: 1,
      nom: "Agences immobilières Paris",
      description: "Campagne ciblant les agences immobilières de Paris et sa banlieue",
      statut: "active",
      niche_id: 1,
      target_leads: 500,
      agent: "Scraper Agent",
      date_creation: "01/05/2023",
      leads: 342,
      conversion: 7.8,
      progress: 78,
      niche: "Immobilier",
      date: "01/05/2023",
    },
    {
      id: 2,
      nom: "Avocats d'affaires Lyon",
      description: "Campagne ciblant les cabinets d'avocats spécialisés en droit des affaires à Lyon",
      statut: "active",
      niche_id: 2,
      target_leads: 400,
      agent: "Scraper Agent",
      date_creation: "15/05/2023",
      leads: 215,
      conversion: 5.2,
      progress: 45,
      niche: "Juridique",
      date: "15/05/2023",
    },
    {
      id: 3,
      nom: "Architectes Bordeaux",
      description: "Campagne ciblant les cabinets d'architectes à Bordeaux et sa région",
      statut: "active",
      niche_id: 3,
      target_leads: 200,
      agent: "Scraper Agent",
      date_creation: "10/05/2023",
      leads: 189,
      conversion: 9.1,
      progress: 92,
      niche: "Architecture",
      date: "10/05/2023",
    },
    {
      id: 4,
      nom: "Consultants RH Lille",
      description: "Campagne ciblant les consultants en ressources humaines à Lille",
      statut: "warning",
      niche_id: 4,
      target_leads: 300,
      agent: "Scraper Agent",
      date_creation: "20/05/2023",
      leads: 78,
      conversion: 3.2,
      progress: 24,
      niche: "Ressources Humaines",
      date: "20/05/2023",
    },
    {
      id: 5,
      nom: "Cliniques vétérinaires",
      description: "Campagne ciblant les cliniques vétérinaires en France",
      statut: "active",
      niche_id: 5,
      target_leads: 250,
      agent: "Scraper Agent",
      date_creation: "05/05/2023",
      leads: 156,
      conversion: 6.5,
      progress: 62,
      niche: "Santé",
      date: "05/05/2023",
    },
    {
      id: 6,
      nom: "Restaurants gastronomiques",
      description: "Campagne ciblant les restaurants gastronomiques en France",
      statut: "paused",
      niche_id: 6,
      target_leads: 200,
      agent: "Scraper Agent",
      date_creation: "25/04/2023",
      leads: 98,
      conversion: 4.8,
      progress: 50,
      niche: "Restauration",
      date: "25/04/2023",
    },
    {
      id: 7,
      nom: "Écoles de langues",
      description: "Campagne ciblant les écoles de langues en France",
      statut: "completed",
      niche_id: 7,
      target_leads: 200,
      agent: "Scraper Agent",
      date_creation: "15/04/2023",
      leads: 245,
      conversion: 8.3,
      progress: 100,
      niche: "Éducation",
      date: "15/04/2023",
    },
    {
      id: 8,
      nom: "Agences de voyage",
      description: "Campagne ciblant les agences de voyage en France",
      statut: "error",
      niche_id: 8,
      target_leads: 150,
      agent: "Scraper Agent",
      date_creation: "10/05/2023",
      leads: 45,
      conversion: 2.1,
      progress: 30,
      niche: "Tourisme",
      date: "10/05/2023",
    },
  ]

  // Chargement initial des données
  useEffect(() => {
    const loadCampaigns = async () => {
      setIsLoading(true)
      try {
        const response = await apiRequest('/campaigns')
        setCampaigns(response)
      } catch (error) {
        console.error("Error loading campaigns:", error)
        toast({
          title: "Erreur",
          description: "Impossible de charger les campagnes",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadCampaigns()
  }, [])

  // Filtrer les campagnes en fonction de l'onglet actif et de la recherche
  useEffect(() => {
    let filtered = [...campaigns]

    // Filtrer par statut (onglet)
    if (activeTab !== "all") {
      filtered = filtered.filter((campaign) => campaign.statut === activeTab)
    }

    // Filtrer par recherche
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (campaign) => campaign.nom.toLowerCase().includes(query) || campaign.niche.toLowerCase().includes(query),
      )
    }

    setFilteredCampaigns(filtered)

    // Calculer le nombre total de pages
    setTotalPages(Math.ceil(filtered.length / itemsPerPage))

    // Réinitialiser la page courante si nécessaire
    if (currentPage > Math.ceil(filtered.length / itemsPerPage)) {
      setCurrentPage(1)
    }
  }, [campaigns, activeTab, searchQuery, currentPage])

  // Obtenir les campagnes pour la page actuelle
  const getCurrentPageCampaigns = () => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    return filteredCampaigns.slice(startIndex, endIndex)
  }

  // Gestionnaires d'événements
  const handleTabChange = (value: string) => {
    setActiveTab(value)
    setCurrentPage(1) // Réinitialiser la pagination lors du changement d'onglet
  }

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    setCurrentPage(1) // Réinitialiser la pagination lors de la recherche
  }

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  // Actions sur les campagnes
  const handleViewDetails = (campaign: Campaign) => {
    setSelectedCampaign(campaign)
    setIsDetailsDialogOpen(true)
  }

  const handleEditCampaign = (campaign: Campaign) => {
    setEditForm({
      id: campaign.id,
      name: campaign.nom || "",
      description: campaign.description || "",
      targetLeads: campaign.target_leads !== undefined ? campaign.target_leads : 0,
      agent: campaign.agent || ""
    })
    setIsEditDialogOpen(true)
  }

  const handleDeleteCampaign = async (id: number) => {
    try {
      await apiRequest(`/campaigns/${id}`, {
        method: 'DELETE',
      })
      
      // Mettre à jour la liste des campagnes
      setCampaigns(campaigns.filter((campaign) => campaign.id !== id))
      
      toast({
        title: "Campagne supprimée",
        description: "La campagne a été supprimée avec succès.",
      })
    } catch (error) {
      console.error("Error deleting campaign:", error)
      toast({
        title: "Erreur",
        description: "Impossible de supprimer la campagne",
        variant: "destructive",
      })
    }
  }

  const handleUpdateCampaignStatus = async (id: number, status: string) => {
    try {
      const response = await apiRequest(`/campaigns/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify({ statut: status }),
      })
      
      setCampaigns(
        campaigns.map((campaign) => (campaign.id === id ? response : campaign))
      )
      
      toast({
        title: "Statut mis à jour",
        description: "Le statut de la campagne a été mis à jour avec succès.",
      })
    } catch (error) {
      console.error("Error updating campaign status:", error)
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour le statut de la campagne",
        variant: "destructive",
      })
    }
  }

  const handleSaveEditCampaign = async () => {
    try {
      const campaignData = {
        nom: editForm.name,
        description: editForm.description,
        target_leads: editForm.targetLeads,
        agent: editForm.agent,
      }
      
      const response = await apiRequest(`/campaigns/${editForm.id}`, {
        method: 'PUT',
        body: JSON.stringify(campaignData),
      })
      
      setCampaigns(
        campaigns.map((campaign) => (campaign.id === editForm.id ? response : campaign))
      )
      
      toast({
        title: "Campagne mise à jour",
        description: `La campagne "${editForm.name}" a été mise à jour avec succès.`,
      })
      
      setIsEditDialogOpen(false)
    } catch (error) {
      console.error("Error updating campaign:", error)
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour la campagne",
        variant: "destructive",
      })
    }
  }

  const handleCreateNewCampaign = async () => {
    try {
      const campaignData = {
        nom: newCampaignForm.name,
        description: newCampaignForm.description,
        niche_id: parseInt(newCampaignForm.niche) || 0,
        target_leads: newCampaignForm.targetLeads || 0,
        agent: newCampaignForm.agent
      }
      
      const response = await apiRequest('/campaigns', {
        method: 'POST',
        body: JSON.stringify(campaignData),
      })
      
      setCampaigns([...campaigns, response])
      
      toast({
        title: "Campagne créée",
        description: `La campagne "${newCampaignForm.name}" a été créée avec succès.`,
      })
      
      // Réinitialiser le formulaire
      setNewCampaignForm({
        name: "",
        niche: "",
        description: "",
        targetLeads: 500,
        agent: "Scraper Agent",
      })
      
      setIsNewCampaignDialogOpen(false)
    } catch (error) {
      console.error("Error creating campaign:", error)
      toast({
        title: "Erreur",
        description: "Impossible de créer la campagne",
        variant: "destructive",
      })
    }
  }

  const handleExportLeads = async (campaign: Campaign) => {
    try {
      await apiRequest(`/campaigns/${campaign.id}/export`, {
        method: 'GET',
      })
      
      toast({
        title: "Export des leads",
        description: `Les leads de la campagne "${campaign.nom}" ont été exportés avec succès.`,
      })
    } catch (error) {
      console.error("Error exporting leads:", error)
      toast({
        title: "Erreur",
        description: "Impossible d'exporter les leads",
        variant: "destructive",
      })
    }
  }

  const handleRestartCampaign = (campaign: Campaign) => {
    // Redémarrer une campagne en erreur
    const updatedCampaigns = campaigns.map((c) => {
      if (c.id === campaign.id) {
        return { ...c, statut: "active" }
      }
      return c
    })
    setCampaigns(updatedCampaigns as Campaign[])

    toast({
      title: "Campagne redémarrée",
      description: `La campagne "${campaign.nom}" a été redémarrée avec succès.`,
    })
  }

  // Ajouter un useEffect pour charger les niches depuis l'API
  useEffect(() => {
    const fetchNiches = async () => {
      try {
        const response = await apiRequest('/niches')
        setNiches(response)
      } catch (error) {
        console.error("Error fetching niches:", error)
        toast({
          title: "Erreur",
          description: "Impossible de charger la liste des niches",
          variant: "destructive",
        })
      }
    }

    fetchNiches()
  }, [])

  // Rendu conditionnel pour l'état de chargement
  if (isLoading) {
    return (
      <div className="flex flex-col gap-5 w-full">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Campagnes</h2>
            <p className="text-muted-foreground">Gérez vos campagnes d'automatisation et suivez leurs performances.</p>
          </div>
          <Button className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200">
            <Plus className="mr-2 h-4 w-4" />
            Nouvelle campagne
          </Button>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center">
            <RefreshCw className="h-8 w-8 animate-spin text-purple-600 mb-4" />
            <p className="text-muted-foreground">Chargement des campagnes...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Campagnes</h2>
          <p className="text-muted-foreground">Gérez vos campagnes d'automatisation et suivez leurs performances.</p>
        </div>
        <Button
          className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
          onClick={() => setIsNewCampaignDialogOpen(true)}
        >
          <Plus className="mr-2 h-4 w-4" />
          Nouvelle campagne
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher une campagne..."
            className="pl-8"
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filtres
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-[200px]">
            <DropdownMenuLabel>Filtrer par statut</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => handleTabChange("active")}>Actives</DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleTabChange("paused")}>En pause</DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleTabChange("completed")}>Terminées</DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleTabChange("error")}>En erreur</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuLabel>Filtrer par niche</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => setSearchQuery("Immobilier")}>Immobilier</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSearchQuery("Juridique")}>Juridique</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSearchQuery("Architecture")}>Architecture</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSearchQuery("Ressources Humaines")}>
              Ressources Humaines
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSearchQuery("Santé")}>Santé</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={handleTabChange} className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">Toutes</TabsTrigger>
          <TabsTrigger value="active">Actives</TabsTrigger>
          <TabsTrigger value="paused">En pause</TabsTrigger>
          <TabsTrigger value="completed">Terminées</TabsTrigger>
          <TabsTrigger value="error">En erreur</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="space-y-4">
          <Card className="w-full">
            <CardHeader className="py-4">
              <CardTitle>Liste des campagnes</CardTitle>
              <CardDescription>Toutes vos campagnes d'automatisation</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>Niche</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Leads</TableHead>
                    <TableHead>Taux de conversion</TableHead>
                    <TableHead>Date de lancement</TableHead>
                    <TableHead>Agent assigné</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {getCurrentPageCampaigns().map((campaign) => (
                    <TableRow key={campaign.id}>
                      <TableCell className="font-medium">{campaign.nom || "Sans nom"}</TableCell>
                      <TableCell>{campaign.niche || "Sans niche"}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            campaign.statut === "active"
                              ? "default"
                              : campaign.statut === "paused"
                                ? "outline"
                                : campaign.statut === "completed"
                                  ? "secondary"
                                  : campaign.statut === "warning"
                                    ? "secondary"
                                    : "destructive"
                          }
                          className={
                            campaign.statut === "active"
                              ? "bg-green-500 hover:bg-green-600"
                              : campaign.statut === "warning"
                                ? "bg-yellow-500 hover:bg-yellow-600"
                                : ""
                          }
                        >
                          {campaign.statut === "active"
                            ? "Active"
                            : campaign.statut === "paused"
                              ? "En pause"
                              : campaign.statut === "completed"
                                ? "Terminée"
                                : campaign.statut === "warning"
                                  ? "Avertissement"
                                  : "Erreur"}
                        </Badge>
                      </TableCell>
                      <TableCell>{campaign.leads || 0}</TableCell>
                      <TableCell>{campaign.conversion !== undefined ? campaign.conversion.toFixed(2) : "N/A"}%</TableCell>
                      <TableCell>{campaign.date_creation || "N/A"}</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Bot className="h-4 w-4 text-muted-foreground" />
                          <span>{campaign.agent || "Sans agent"}</span>
                        </div>
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
                            <DropdownMenuItem onClick={() => handleViewDetails(campaign)}>
                              <Eye className="mr-2 h-4 w-4" />
                              Voir les détails
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEditCampaign(campaign)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Modifier
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {campaign.statut === "active" ? (
                              <DropdownMenuItem onClick={() => handleUpdateCampaignStatus(campaign.id, "paused")}>
                                <Clock className="mr-2 h-4 w-4" />
                                Mettre en pause
                              </DropdownMenuItem>
                            ) : campaign.statut === "paused" ? (
                              <DropdownMenuItem onClick={() => handleUpdateCampaignStatus(campaign.id, "active")}>
                                <Play className="mr-2 h-4 w-4" />
                                Reprendre
                              </DropdownMenuItem>
                            ) : campaign.statut === "error" ? (
                              <DropdownMenuItem onClick={() => handleRestartCampaign(campaign)}>
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Relancer
                              </DropdownMenuItem>
                            ) : null}
                            <DropdownMenuItem onClick={() => handleExportLeads(campaign)}>
                              <Download className="mr-2 h-4 w-4" />
                              Exporter les leads
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600 dark:text-red-400"
                              onClick={() => handleDeleteCampaign(campaign.id)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Supprimer
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
            <CardFooter className="flex justify-between py-4">
              <div className="text-sm text-muted-foreground">
                Affichage de {Math.min(itemsPerPage, filteredCampaigns.length)} campagnes sur {filteredCampaigns.length}
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={handlePreviousPage} disabled={currentPage === 1}>
                  Précédent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNextPage}
                  disabled={currentPage === totalPages || totalPages === 0}
                >
                  Suivant
                </Button>
              </div>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="active" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Campagnes actives</CardTitle>
              <CardDescription>Campagnes en cours d'exécution</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredCampaigns.map((campaign) => (
                  <div key={campaign.nom} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div
                          className={`h-2 w-2 rounded-full ${
                            campaign.statut === "active"
                              ? "bg-green-500"
                              : campaign.statut === "warning"
                                ? "bg-yellow-500"
                                : "bg-red-500"
                          }`}
                        />
                        <span className="font-medium">{campaign.nom || "Sans nom"}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">{campaign.progress}%</span>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => handleViewDetails(campaign)}>
                              <Eye className="mr-2 h-4 w-4" />
                              Voir les détails
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleUpdateCampaignStatus(campaign.id, "paused")}>
                              <Clock className="mr-2 h-4 w-4" />
                              Mettre en pause
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    <Progress value={campaign.progress} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="paused" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Campagnes en pause</CardTitle>
              <CardDescription>Campagnes temporairement suspendues</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredCampaigns.map((campaign) => (
                  <div key={campaign.nom} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 rounded-full bg-gray-500" />
                        <span className="font-medium">{campaign.nom || "Sans nom"}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">{campaign.progress}%</span>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => handleViewDetails(campaign)}>
                              <Eye className="mr-2 h-4 w-4" />
                              Voir les détails
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleUpdateCampaignStatus(campaign.id, "active")}>
                              <Play className="mr-2 h-4 w-4" />
                              Reprendre
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    <Progress value={campaign.progress} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="completed" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Campagnes terminées</CardTitle>
              <CardDescription>Campagnes complétées avec succès</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredCampaigns.map((campaign) => (
                  <div key={campaign.nom} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 rounded-full bg-green-500" />
                        <span className="font-medium">{campaign.nom || "Sans nom"}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">{campaign.progress}%</span>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => handleViewDetails(campaign)}>
                              <Eye className="mr-2 h-4 w-4" />
                              Voir les détails
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleExportLeads(campaign)}>
                              <Download className="mr-2 h-4 w-4" />
                              Exporter les leads
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    <Progress value={campaign.progress} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="error" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Campagnes en erreur</CardTitle>
              <CardDescription>Campagnes ayant rencontré des problèmes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredCampaigns.map((campaign) => (
                  <div key={campaign.nom} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 rounded-full bg-red-500" />
                        <span className="font-medium">{campaign.nom || "Sans nom"}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">{campaign.progress}%</span>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => handleViewDetails(campaign)}>
                              <Eye className="mr-2 h-4 w-4" />
                              Voir les détails
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleRestartCampaign(campaign)}>
                              <RefreshCw className="mr-2 h-4 w-4" />
                              Relancer
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    <Progress value={campaign.progress} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialogue de détails de la campagne */}
      <Dialog open={isDetailsDialogOpen} onOpenChange={setIsDetailsDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Détails de la campagne</DialogTitle>
            <DialogDescription>Informations détaillées sur la campagne</DialogDescription>
          </DialogHeader>
          {selectedCampaign && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold">{selectedCampaign.nom || "Sans nom"}</h3>
                <Badge
                  variant={
                    selectedCampaign.statut === "active"
                      ? "default"
                      : selectedCampaign.statut === "paused"
                        ? "outline"
                        : selectedCampaign.statut === "completed"
                          ? "secondary"
                          : selectedCampaign.statut === "warning"
                            ? "secondary"
                            : "destructive"
                  }
                  className={
                    selectedCampaign.statut === "active"
                      ? "bg-green-500 hover:bg-green-600 mt-2"
                      : selectedCampaign.statut === "warning"
                        ? "bg-yellow-500 hover:bg-yellow-600 mt-2"
                        : "mt-2"
                  }
                >
                  {selectedCampaign.statut === "active"
                    ? "Active"
                    : selectedCampaign.statut === "paused"
                      ? "En pause"
                      : selectedCampaign.statut === "completed"
                        ? "Terminée"
                        : selectedCampaign.statut === "warning"
                          ? "Avertissement"
                          : "Erreur"}
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Niche</p>
                  <p className="font-medium">{selectedCampaign.niche || "Sans niche"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Date de lancement</p>
                  <p className="font-medium">{selectedCampaign.date_creation || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Leads collectés</p>
                  <p className="font-medium">{selectedCampaign.leads || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Taux de conversion</p>
                  <p className="font-medium">{selectedCampaign.conversion !== undefined ? selectedCampaign.conversion.toFixed(2) : "N/A"}%</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Agent assigné</p>
                  <p className="font-medium">{selectedCampaign.agent || "Sans agent"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Objectif de leads</p>
                  <p className="font-medium">{selectedCampaign.target_leads !== undefined ? selectedCampaign.target_leads : 0}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="text-sm">{selectedCampaign.description || "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Progression</p>
                <div className="flex items-center space-x-2 mt-1">
                  <Progress value={selectedCampaign.progress} className="h-2 flex-1" />
                  <span className="text-sm font-medium">{selectedCampaign.progress}%</span>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDetailsDialogOpen(false)}>
              Fermer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialogue de modification de la campagne */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Modifier la campagne</DialogTitle>
            <DialogDescription>Modifiez les informations de la campagne</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Nom de la campagne</Label>
              <Input
                id="edit-name"
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-target-leads">Objectif de leads</Label>
              <Input
                id="edit-target-leads"
                type="number"
                value={editForm.targetLeads}
                onChange={(e) => setEditForm({ ...editForm, targetLeads: Number.parseInt(e.target.value) })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-agent">Agent assigné</Label>
              <Select value={editForm.agent} onValueChange={(value) => setEditForm({ ...editForm, agent: value })}>
                <SelectTrigger id="edit-agent">
                  <SelectValue placeholder="Sélectionner un agent" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Scraper Agent">Scraper Agent</SelectItem>
                  <SelectItem value="Cleaner Agent">Cleaner Agent</SelectItem>
                  <SelectItem value="Analytics Agent">Analytics Agent</SelectItem>
                  <SelectItem value="Pivot Agent">Pivot Agent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleSaveEditCampaign}>Enregistrer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialogue de création d'une nouvelle campagne */}
      <Dialog open={isNewCampaignDialogOpen} onOpenChange={setIsNewCampaignDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Nouvelle campagne</DialogTitle>
            <DialogDescription>Créez une nouvelle campagne d'automatisation</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new-name">Nom de la campagne</Label>
              <Input
                id="new-name"
                value={newCampaignForm.name}
                onChange={(e) => setNewCampaignForm({ ...newCampaignForm, name: e.target.value })}
                placeholder="Ex: Agences immobilières Paris"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-niche">Niche</Label>
              <Select
                value={newCampaignForm.niche}
                onValueChange={(value) => setNewCampaignForm({ ...newCampaignForm, niche: value })}
              >
                <SelectTrigger id="new-niche">
                  <SelectValue placeholder="Sélectionner une niche" />
                </SelectTrigger>
                <SelectContent>
                  {niches.length > 0 ? (
                    niches.map((niche) => (
                      <SelectItem key={niche.id} value={niche.nom}>
                        {niche.nom}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="loading" disabled>
                      Chargement des niches...
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-description">Description</Label>
              <Textarea
                id="new-description"
                value={newCampaignForm.description}
                onChange={(e) => setNewCampaignForm({ ...newCampaignForm, description: e.target.value })}
                placeholder="Description de la campagne et de ses objectifs"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-target-leads">Objectif de leads</Label>
              <Input
                id="new-target-leads"
                type="number"
                value={newCampaignForm.targetLeads}
                onChange={(e) =>
                  setNewCampaignForm({ ...newCampaignForm, targetLeads: Number.parseInt(e.target.value) })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-agent">Agent assigné</Label>
              <Select
                value={newCampaignForm.agent}
                onValueChange={(value) => setNewCampaignForm({ ...newCampaignForm, agent: value })}
              >
                <SelectTrigger id="new-agent">
                  <SelectValue placeholder="Sélectionner un agent" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Scraper Agent">Scraper Agent</SelectItem>
                  <SelectItem value="Cleaner Agent">Cleaner Agent</SelectItem>
                  <SelectItem value="Analytics Agent">Analytics Agent</SelectItem>
                  <SelectItem value="Pivot Agent">Pivot Agent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsNewCampaignDialogOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateNewCampaign} disabled={!newCampaignForm.name || !newCampaignForm.niche}>
              Créer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialogue de confirmation de suppression */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Êtes-vous sûr de vouloir supprimer cette campagne ?</AlertDialogTitle>
            <AlertDialogDescription>
              Cette action est irréversible. Toutes les données associées à cette campagne seront définitivement
              supprimées.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction onClick={() => handleDeleteCampaign(selectedCampaign?.id || 0)} className="bg-red-600 hover:bg-red-700 text-white">
              Supprimer
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
