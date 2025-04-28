"use client"

import { useState, useEffect } from "react"
import { Download, Filter, MoreHorizontal, Search, Send } from "lucide-react"
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
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { apiRequest } from "@/services/api-interceptor"
import { toast } from "@/components/ui/use-toast"

// Type pour les leads
interface Lead {
  id: number
  nom: string
  email: string
  telephone: string
  entreprise: string
  statut: string
  date_creation: string
  campagne_id: number
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [filteredLeads, setFilteredLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedLeads, setSelectedLeads] = useState<number[]>([])
  const [selectAll, setSelectAll] = useState(false)

  // Récupérer les leads depuis l'API
  useEffect(() => {
    const fetchLeads = async () => {
      try {
        setLoading(true)
        const response = await apiRequest('/leads')
        setLeads(response)
        setFilteredLeads(response)
        setError(null)
      } catch (err) {
        console.error("Error fetching leads:", err)
        setError("Unable to load leads")
      } finally {
        setLoading(false)
      }
    }

    fetchLeads()
  }, [])

  // Filtrer les leads en fonction de la recherche
  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredLeads(leads)
    } else {
      const filtered = leads.filter(lead => 
        lead.nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
        lead.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        lead.entreprise.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredLeads(filtered)
    }
  }, [leads, searchQuery])

  // Gérer la sélection de tous les leads
  useEffect(() => {
    if (selectAll) {
      setSelectedLeads(filteredLeads.map(lead => lead.id))
    } else {
      setSelectedLeads([])
    }
  }, [selectAll, filteredLeads])

  // Gérer la recherche
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  // Gérer la sélection d'un lead
  const handleSelectLead = (id: number) => {
    if (selectedLeads.includes(id)) {
      setSelectedLeads(selectedLeads.filter(leadId => leadId !== id))
    } else {
      setSelectedLeads([...selectedLeads, id])
    }
  }

  // Gérer l'export CSV
  const handleExportCSV = async () => {
    try {
      const ids = selectedLeads.length > 0 ? selectedLeads : filteredLeads.map(lead => lead.id)
      await apiRequest(`/api/leads/export/csv?ids=${ids.join(',')}`, {
        method: 'GET',
      })
      
      toast({
        title: "Export CSV",
        description: "Les leads ont été exportés avec succès.",
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

  // Gérer l'envoi vers GHL
  const handleSendToGHL = async () => {
    try {
      const ids = selectedLeads.length > 0 ? selectedLeads : filteredLeads.map(lead => lead.id)
      await apiRequest(`/api/leads/sync-ghl`, {
        method: 'POST',
        body: JSON.stringify({ ids }),
      })
      
      toast({
        title: "Envoi vers GHL",
        description: "Les leads ont été envoyés avec succès vers GHL.",
      })
    } catch (error) {
      console.error("Error sending leads to GHL:", error)
      toast({
        title: "Erreur",
        description: "Impossible d'envoyer les leads vers GHL",
        variant: "destructive",
      })
    }
  }

  // Dans la fonction handleCreateNewLead
  const handleCreateNewLead = async () => {
    try {
      const leadData = {
        nom: newLeadForm.name,
        email: newLeadForm.email,
        telephone: newLeadForm.phone,
        entreprise: newLeadForm.company,
        campagne_id: parseInt(newLeadForm.campaignId),
      }
      
      const response = await apiRequest('/leads', {
        method: 'POST',
        body: JSON.stringify(leadData),
      })
      
      setLeads([...leads, response])
      
      toast({
        title: "Lead créé",
        description: `Le lead "${newLeadForm.name}" a été créé avec succès.`,
      })
      
      // Réinitialiser le formulaire
      setNewLeadForm({
        name: "",
        email: "",
        phone: "",
        company: "",
        campaignId: "",
      })
      
      setIsNewLeadDialogOpen(false)
    } catch (error) {
      console.error("Error creating lead:", error)
      toast({
        title: "Erreur",
        description: "Impossible de créer le lead",
        variant: "destructive",
      })
    }
  }

  // Dans la fonction handleUpdateLeadStatus
  const handleUpdateLeadStatus = async (id: number, status: string) => {
    try {
      const response = await apiRequest(`/leads/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify({ statut: status }),
      })
      
      // Mettre à jour la liste des leads
      setLeads(
        leads.map((lead) => (lead.id === id ? response : lead))
      )
      
      toast({
        title: "Statut mis à jour",
        description: `Le statut du lead a été mis à jour avec succès.`,
      })
    } catch (error) {
      console.error("Error updating lead status:", error)
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour le statut du lead",
        variant: "destructive",
      })
    }
  }

  // Ajouter la fonction manquante handleViewLead
  const handleViewLead = async (id: number) => {
    try {
      const lead = await apiRequest(`/leads/${id}`);
      // Afficher les détails du lead (par exemple dans un dialogue)
      console.log("Détails du lead:", lead);
      
      toast({
        title: "Détails du lead",
        description: "Les détails du lead ont été récupérés avec succès.",
      });
    } catch (error) {
      console.error("Error fetching lead details:", error);
      toast({
        title: "Erreur",
        description: "Impossible de récupérer les détails du lead",
        variant: "destructive",
      });
    }
  };

  if (loading) return <div className="p-4">Chargement des leads...</div>
  if (error) return <div className="p-4 text-red-500">Erreur: {error}</div>

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Leads</h2>
          <p className="text-muted-foreground">Gérez et exportez les leads collectés par vos campagnes.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExportCSV}>
            <Download className="mr-2 h-4 w-4" />
            Exporter CSV
          </Button>
          <Button 
            className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
            onClick={handleSendToGHL}
          >
            <Send className="mr-2 h-4 w-4" />
            Envoyer vers GHL
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Input 
          placeholder="Rechercher un lead..." 
          className="max-w-sm" 
          value={searchQuery}
          onChange={handleSearch}
        />
        <Button variant="outline">
          <Filter className="mr-2 h-4 w-4" />
          Filtres
        </Button>
      </div>

      <Card className="w-full">
        <CardHeader className="py-4">
          <CardTitle>Liste des leads</CardTitle>
          <CardDescription>Tous les leads collectés par vos campagnes</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]">
                  <Checkbox 
                    checked={selectAll} 
                    onCheckedChange={() => setSelectAll(!selectAll)}
                  />
                </TableHead>
                <TableHead>Nom</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Téléphone</TableHead>
                <TableHead>Entreprise</TableHead>
                <TableHead>Campagne</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLeads.map((lead) => (
                <TableRow key={lead.id}>
                  <TableCell>
                    <Checkbox 
                      checked={selectedLeads.includes(lead.id)}
                      onCheckedChange={() => handleSelectLead(lead.id)}
                    />
                  </TableCell>
                  <TableCell className="font-medium">{lead.nom || "Sans nom"}</TableCell>
                  <TableCell>{lead.email || "Pas d'email"}</TableCell>
                  <TableCell>{lead.telephone}</TableCell>
                  <TableCell>{lead.entreprise}</TableCell>
                  <TableCell>{lead.campagne_id}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        lead.statut === "new"
                          ? "default"
                          : lead.statut === "contacted"
                            ? "outline"
                            : lead.statut === "qualified"
                              ? "secondary"
                              : lead.statut === "converted"
                                ? "success"
                                : "destructive"
                      }
                      className={
                        lead.statut === "new"
                          ? "bg-blue-500 hover:bg-blue-600"
                          : lead.statut === "converted"
                            ? "bg-green-500 hover:bg-green-600"
                            : ""
                      }
                    >
                      {lead.statut === "new"
                        ? "Nouveau"
                        : lead.statut === "contacted"
                          ? "Contacté"
                          : lead.statut === "qualified"
                            ? "Qualifié"
                            : lead.statut === "converted"
                              ? "Converti"
                              : "Perdu"}
                    </Badge>
                  </TableCell>
                  <TableCell>{lead.date_creation}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <span className="sr-only">Open menu</span>
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem onClick={() => handleViewLead(lead.id)}>
                          Voir les détails
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleUpdateLeadStatus(lead.id, "contacted")}>
                          Marquer comme contacté
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleUpdateLeadStatus(lead.id, "qualified")}>
                          Marquer comme qualifié
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleUpdateLeadStatus(lead.id, "converted")}>
                          Marquer comme converti
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleUpdateLeadStatus(lead.id, "lost")}>
                          Marquer comme perdu
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-red-600"
                          onClick={() => handleDeleteLead(lead.id)}
                        >
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
      </Card>
    </div>
  )
}
