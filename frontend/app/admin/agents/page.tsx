"use client"

import { useState, useEffect } from "react"
import { Bot, Clock, Download, Edit, Eye, MoreHorizontal, Play, Plus, RefreshCw, Search, Zap } from "lucide-react"
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
import { apiRequest } from "@/services/api-interceptor"
import { toast } from "@/components/ui/use-toast"

// Type pour les agents
interface Agent {
  id: number
  nom: string
  type: string
  statut: "active" | "inactive" | "warning" | "error"
  derniere_execution: string
  leads_generes: number | null
  campagnes_actives: number
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("all")
  const [newAgentForm, setNewAgentForm] = useState({
    name: "",
    type: ""
  });
  const [isNewAgentDialogOpen, setIsNewAgentDialogOpen] = useState(false);

  // Récupérer les agents depuis l'API
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true)
        const response = await apiRequest('/agents')
        setAgents(response)
        setFilteredAgents(response)
        setError(null)
      } catch (err) {
        console.error("Error fetching agents:", err)
        setError("Unable to load agents")
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
  }, [])

  // Filtrer les agents en fonction de la recherche et de l'onglet actif
  useEffect(() => {
    let filtered = agents;
    
    // Filtrer par statut si un onglet spécifique est sélectionné
    if (activeTab !== "all") {
      filtered = filtered.filter(agent => {
        if (activeTab === "active") return agent.statut === "active";
        if (activeTab === "inactive") return agent.statut === "inactive";
        if (activeTab === "error") return agent.statut === "error" || agent.statut === "warning";
        return true;
      });
    }
    
    // Filtrer par recherche
    if (searchQuery.trim() !== "") {
      filtered = filtered.filter(agent => 
        agent.nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.type.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    setFilteredAgents(filtered);
  }, [agents, searchQuery, activeTab]);

  // Gérer la recherche
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  // Gérer le changement d'onglet
  const handleTabChange = (value: string) => {
    setActiveTab(value);
  }

  // Gérer l'actualisation des agents
  const handleRefresh = async () => {
    try {
      setLoading(true)
      const response = await apiRequest('/agents')
      setAgents(response)
      setFilteredAgents(response)
      setError(null)
      
      toast({
        title: "Agents actualisés",
        description: "La liste des agents a été actualisée avec succès.",
      })
    } catch (err) {
      console.error("Error refreshing agents:", err)
      setError("Unable to refresh agents")
      
      toast({
        title: "Erreur",
        description: "Impossible d'actualiser les agents",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  // Gérer le redémarrage d'un agent
  const handleRestartAgent = async (id: number) => {
    try {
      const response = await apiRequest(`/agents/${id}/restart`, {
        method: 'POST',
      });
      
      // Mettre à jour l'agent dans la liste
      setAgents(
        agents.map((agent) => (agent.id === id ? { ...agent, statut: "active" } : agent))
      );
      
      toast({
        title: "Agent redémarré",
        description: "L'agent a été redémarré avec succès.",
      });
    } catch (error) {
      console.error("Error restarting agent:", error);
      toast({
        title: "Erreur",
        description: "Impossible de redémarrer l'agent",
        variant: "destructive",
      });
    }
  };

  // Gérer l'activation d'un agent
  const handleActivateAgent = async (id: number) => {
    try {
      const response = await apiRequest(`/agents/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ statut: "active" }),
      });
      
      setAgents(
        agents.map((agent) => (agent.id === id ? response : agent))
      );
      
      toast({
        title: "Agent activé",
        description: "L'agent a été activé avec succès.",
      });
    } catch (error) {
      console.error("Error activating agent:", error);
      toast({
        title: "Erreur",
        description: "Impossible d'activer l'agent",
        variant: "destructive",
      });
    }
  };

  // Gérer la désactivation d'un agent
  const handleDeactivateAgent = async (agentId: number) => {
    try {
      await apiRequest(`/agents/${agentId}/deactivate`, {
        method: 'POST',
      })
      
      // Mettre à jour l'agent dans la liste
      const updatedAgents = agents.map(agent => {
        if (agent.id === agentId) {
          return { ...agent, statut: "inactive" as const }
        }
        return agent
      })
      
      setAgents(updatedAgents)
      
      toast({
        title: "Agent désactivé",
        description: "L'agent a été désactivé avec succès.",
      })
    } catch (error) {
      console.error("Error deactivating agent:", error)
      toast({
        title: "Erreur",
        description: "Impossible de désactiver l'agent",
        variant: "destructive",
      })
    }
  }

  // Gérer la création d'un nouvel agent
  const handleCreateNewAgent = async () => {
    try {
      const agentData = {
        nom: newAgentForm.name,
        type: newAgentForm.type,
        statut: "active",
      }
      
      const response = await apiRequest('/agents', {
        method: 'POST',
        body: JSON.stringify(agentData),
      })
      
      setAgents([...agents, response])
      
      toast({
        title: "Agent créé",
        description: `L'agent "${newAgentForm.name}" a été créé avec succès.`,
      })
      
      // Réinitialiser le formulaire
      setNewAgentForm({
        name: "",
        type: "",
      })
      
      setIsNewAgentDialogOpen(false)
    } catch (error) {
      console.error("Error creating agent:", error)
      toast({
        title: "Erreur",
        description: "Impossible de créer l'agent",
        variant: "destructive",
      })
    }
  }

  // Gérer la suppression d'un agent
  const handleDeleteAgent = async (id: number) => {
    try {
      await apiRequest(`/agents/${id}`, {
        method: 'DELETE',
      });
      
      // Supprimer l'agent de la liste
      setAgents(agents.filter(agent => agent.id !== id));
      
      toast({
        title: "Agent supprimé",
        description: "L'agent a été supprimé avec succès.",
      });
    } catch (error) {
      console.error("Error deleting agent:", error);
      toast({
        title: "Erreur",
        description: "Impossible de supprimer l'agent",
        variant: "destructive",
      });
    }
  };

  // Ajoutez cette fonction dans le composant AgentsPage
  const handleViewAgentLogs = async (id: number) => {
    try {
      // Récupérer les logs de l'agent
      const logs = await apiRequest(`/agents/${id}/logs`);
      
      // Ici, vous pouvez afficher les logs dans un dialogue ou rediriger vers une page de logs
      console.log("Logs de l'agent:", logs);
      
      // Exemple: redirection vers une page de logs
      // router.push(`/admin/agents/${id}/logs`);
      
      toast({
        title: "Logs récupérés",
        description: `Les logs de l'agent ont été récupérés avec succès.`,
      });
    } catch (error) {
      console.error("Error fetching agent logs:", error);
      toast({
        title: "Erreur",
        description: "Impossible de récupérer les logs de l'agent",
        variant: "destructive",
      });
    }
  };

  // Ajoutez cette fonction dans le composant AgentsPage
  const handleUpdateAgent = async (id: number, data: { statut?: string, nom?: string, type?: string }) => {
    try {
      const response = await apiRequest(`/agents/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      
      // Mettre à jour l'agent dans la liste
      setAgents(
        agents.map((agent) => (agent.id === id ? response : agent))
      );
      
      toast({
        title: "Agent mis à jour",
        description: "L'agent a été mis à jour avec succès.",
      });
    } catch (error) {
      console.error("Error updating agent:", error);
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour l'agent",
        variant: "destructive",
      });
    }
  };

  if (loading) return <div className="p-4">Chargement des agents...</div>
  if (error) return <div className="p-4 text-red-500">Erreur: {error}</div>

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Agents IA</h2>
          <p className="text-muted-foreground">Gérez les agents d'automatisation qui collectent et traitent les données.</p>
        </div>
        <Button className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200">
          <Plus className="mr-2 h-4 w-4" />
          Nouvel agent
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Input 
          placeholder="Rechercher un agent..." 
          className="max-w-sm" 
          value={searchQuery}
          onChange={handleSearch}
        />
        <Button variant="outline" onClick={handleRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Actualiser
        </Button>
      </div>

      <Tabs defaultValue="all" className="space-y-4" onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="all">Tous</TabsTrigger>
          <TabsTrigger value="active">Actifs</TabsTrigger>
          <TabsTrigger value="inactive">Inactifs</TabsTrigger>
          <TabsTrigger value="error">En erreur</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="space-y-4">
          <Card className="w-full">
            <CardHeader className="py-4">
              <CardTitle>Liste des agents</CardTitle>
              <CardDescription>Tous vos agents IA et leur statut actuel</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Dernière exécution</TableHead>
                    <TableHead>Leads traités</TableHead>
                    <TableHead>Campagnes assignées</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAgents.map((agent) => (
                    <TableRow key={agent.id}>
                      <TableCell>
                        <div className="font-medium">{agent.nom}</div>
                        <div className="text-sm text-muted-foreground">{agent.type}</div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            agent.statut === "active"
                              ? "default"
                              : agent.statut === "inactive"
                              ? "outline"
                              : agent.statut === "warning"
                              ? "secondary"
                              : "destructive"
                          }
                        >
                          {agent.statut === "active"
                            ? "Actif"
                            : agent.statut === "inactive"
                            ? "Inactif"
                            : agent.statut === "warning"
                            ? "Avertissement"
                            : "Erreur"}
                        </Badge>
                      </TableCell>
                      <TableCell>{agent.derniere_execution || "Jamais"}</TableCell>
                      <TableCell>{agent.leads_generes !== undefined && agent.leads_generes !== null ? agent.leads_generes : "-"}</TableCell>
                      <TableCell>{agent.campagnes_actives !== undefined ? agent.campagnes_actives : 0}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Ouvrir le menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleViewAgentLogs(agent.id)}>
                              Voir les logs
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleRestartAgent(agent.id)}>
                              Redémarrer
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleUpdateAgent(agent.id, { statut: "inactive" })}>
                              Désactiver
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => handleDeleteAgent(agent.id)}
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
        </TabsContent>
        <TabsContent value="active" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Agents actifs</CardTitle>
              <CardDescription>Agents actuellement en fonctionnement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3 last:border-0 last:pb-0"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <p className="font-medium">{agent.nom}</p>
                        <p className="text-xs text-muted-foreground">
                          {agent.type} • {agent.derniere_execution}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {agent.leads_generes !== null && <div className="text-sm font-medium">{agent.leads_generes} leads</div>}
                      <Button variant="outline" size="sm">
                        <Eye className="mr-2 h-3 w-3" />
                        Détails
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="inactive" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Agents inactifs</CardTitle>
              <CardDescription>Agents actuellement désactivés</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3 last:border-0 last:pb-0"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div>
                        <p className="font-medium">{agent.nom}</p>
                        <p className="text-xs text-muted-foreground">
                          {agent.type} • {agent.derniere_execution}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Button variant="outline" size="sm" onClick={() => handleActivateAgent(agent.id)}>
                        <Play className="mr-2 h-3 w-3" />
                        Activer
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="error" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Agents en erreur</CardTitle>
              <CardDescription>Agents ayant rencontré des problèmes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3 last:border-0 last:pb-0"
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`h-8 w-8 rounded-full ${agent.statut === "warning" ? "bg-yellow-100 dark:bg-yellow-900" : "bg-red-100 dark:bg-red-900"} flex items-center justify-center`}
                      >
                        <Bot
                          className={`h-4 w-4 ${agent.statut === "warning" ? "text-yellow-600 dark:text-yellow-400" : "text-red-600 dark:text-red-400"}`}
                        />
                      </div>
                      <div>
                        <p className="font-medium">{agent.nom}</p>
                        <p className="text-xs text-muted-foreground">
                          {agent.type} • {agent.derniere_execution}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Button variant="outline" size="sm" onClick={() => handleRestartAgent(agent.id)}>
                        <RefreshCw className="mr-2 h-3 w-3" />
                        Relancer
                      </Button>
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
