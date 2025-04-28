"use client"

import { useState, useEffect } from "react"
import { Search, Filter, MoreHorizontal, Send, RefreshCw } from "lucide-react"
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
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { messagesService } from "@/services/api/messages-service"
import { toast } from "@/components/ui/use-toast"

// Type pour les messages
interface Message {
  id: number
  lead_id: number
  lead_name: string
  lead_email: string
  subject: string
  content: string
  status: "sent" | "delivered" | "opened" | "clicked" | "replied" | "bounced" | "failed"
  campaign_id: number
  campaign_name: string
  sent_date: string
  open_date?: string
  reply_date?: string
}

export default function MessagingPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [filteredMessages, setFilteredMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("all")

  // Récupérer les messages depuis l'API
  useEffect(() => {
    const fetchMessages = async () => {
      try {
        setLoading(true)
        
        // Pour le moment, utilisons des données mockées
        const mockMessages: Message[] = [
          {
            id: 1,
            lead_id: 101,
            lead_name: "Jean Dupont",
            lead_email: "jean.dupont@example.com",
            subject: "Votre solution de chatbot IA",
            content: "Bonjour Jean, suite à notre analyse de votre site web, nous pensons que l'intégration d'un chatbot IA pourrait augmenter votre taux de conversion de 25%...",
            status: "opened",
            campaign_id: 1,
            campaign_name: "Avocats Paris",
            sent_date: "2023-06-15T10:30:00Z",
            open_date: "2023-06-15T14:22:00Z"
          },
          {
            id: 2,
            lead_id: 102,
            lead_name: "Marie Martin",
            lead_email: "marie.martin@example.com",
            subject: "Optimisez votre accueil client",
            content: "Bonjour Marie, nous avons remarqué que votre cabinet pourrait bénéficier d'une solution de répondeur IA pour gérer les appels en dehors des heures d'ouverture...",
            status: "replied",
            campaign_id: 2,
            campaign_name: "Dentistes Lyon",
            sent_date: "2023-06-14T09:15:00Z",
            open_date: "2023-06-14T11:05:00Z",
            reply_date: "2023-06-14T16:30:00Z"
          },
          {
            id: 3,
            lead_id: 103,
            lead_name: "Pierre Durand",
            lead_email: "pierre.durand@example.com",
            subject: "Automatisez vos rendez-vous",
            content: "Bonjour Pierre, découvrez comment notre solution d'IA peut vous aider à gérer automatiquement vos prises de rendez-vous et réduire les no-shows de 40%...",
            status: "delivered",
            campaign_id: 3,
            campaign_name: "Architectes Bordeaux",
            sent_date: "2023-06-16T08:45:00Z"
          },
          {
            id: 4,
            lead_id: 104,
            lead_name: "Sophie Lefebvre",
            lead_email: "sophie.lefebvre@example.com",
            subject: "Améliorez votre processus de recrutement",
            content: "Bonjour Sophie, notre IA de pré-qualification des candidats pourrait vous faire gagner jusqu'à 15 heures par semaine dans votre processus de recrutement...",
            status: "clicked",
            campaign_id: 4,
            campaign_name: "Consultants RH",
            sent_date: "2023-06-13T14:20:00Z",
            open_date: "2023-06-13T15:45:00Z"
          },
          {
            id: 5,
            lead_id: 105,
            lead_name: "Thomas Bernard",
            lead_email: "thomas.bernard@example.com",
            subject: "Solution de prise de rendez-vous en ligne",
            content: "Bonjour Thomas, notre solution de prise de rendez-vous en ligne spécialement conçue pour les cliniques vétérinaires pourrait réduire votre charge administrative...",
            status: "bounced",
            campaign_id: 5,
            campaign_name: "Cliniques vétérinaires",
            sent_date: "2023-06-12T11:10:00Z"
          }
        ];
        
        setMessages(mockMessages)
        setFilteredMessages(mockMessages)
        setError(null)
      } catch (err) {
        console.error("Error fetching messages:", err)
        setError("Impossible de charger les messages")
      } finally {
        setLoading(false)
      }
    }

    fetchMessages()
  }, [])

  // Filtrer les messages en fonction de la recherche et de l'onglet actif
  useEffect(() => {
    let filtered = [...messages]
    
    // Filtrer par recherche
    if (searchQuery.trim() !== "") {
      filtered = filtered.filter(message => 
        message.lead_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.lead_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }
    
    // Filtrer par statut (onglet)
    if (activeTab !== "all") {
      filtered = filtered.filter(message => message.status === activeTab)
    }
    
    setFilteredMessages(filtered)
  }, [messages, searchQuery, activeTab])

  // Gérer la recherche
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  // Gérer le changement d'onglet
  const handleTabChange = (value: string) => {
    setActiveTab(value)
  }

  // Gérer le renvoi d'un message
  const handleResendMessage = async (id: number) => {
    try {
      toast({
        title: "Message renvoyé",
        description: "Le message a été renvoyé avec succès."
      })
    } catch (err) {
      toast({
        title: "Erreur",
        description: "Impossible de renvoyer le message.",
        variant: "destructive"
      })
      console.error(err)
    }
  }

  // Fonction pour formater la date
  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A"
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  if (loading) return <div className="p-4">Chargement des messages...</div>
  if (error) return <div className="p-4 text-red-500">Erreur: {error}</div>

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Messagerie</h2>
          <p className="text-muted-foreground">Gérez les messages envoyés à vos leads.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setActiveTab("all")}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Actualiser
          </Button>
          <Button 
            className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
          >
            <Send className="mr-2 h-4 w-4" />
            Nouveau message
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Input 
          placeholder="Rechercher un message..." 
          className="max-w-sm" 
          value={searchQuery}
          onChange={handleSearch}
        />
        <Button variant="outline">
          <Filter className="mr-2 h-4 w-4" />
          Filtres
        </Button>
      </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="all">Tous</TabsTrigger>
          <TabsTrigger value="sent">Envoyés</TabsTrigger>
          <TabsTrigger value="delivered">Délivrés</TabsTrigger>
          <TabsTrigger value="opened">Ouverts</TabsTrigger>
          <TabsTrigger value="clicked">Cliqués</TabsTrigger>
          <TabsTrigger value="replied">Répondus</TabsTrigger>
          <TabsTrigger value="bounced">Rebonds</TabsTrigger>
          <TabsTrigger value="failed">Échecs</TabsTrigger>
        </TabsList>
        
        <TabsContent value={activeTab}>
          <Card className="w-full">
            <CardHeader className="py-4">
              <CardTitle>Messages {activeTab !== "all" ? `(${activeTab})` : ""}</CardTitle>
              <CardDescription>
                {activeTab === "all" 
                  ? "Tous les messages envoyés aux leads" 
                  : activeTab === "sent" 
                    ? "Messages envoyés mais pas encore délivrés"
                    : activeTab === "delivered"
                      ? "Messages délivrés mais pas encore ouverts"
                      : activeTab === "opened"
                        ? "Messages ouverts par les destinataires"
                        : activeTab === "clicked"
                          ? "Messages avec liens cliqués"
                          : activeTab === "replied"
                            ? "Messages ayant reçu une réponse"
                            : activeTab === "bounced"
                              ? "Messages ayant rebondi"
                              : "Messages dont l'envoi a échoué"
                }
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Destinataire</TableHead>
                    <TableHead>Sujet</TableHead>
                    <TableHead>Campagne</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Date d'envoi</TableHead>
                    <TableHead>Date d'ouverture</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredMessages.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-4">
                        Aucun message trouvé
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredMessages.map((message) => (
                      <TableRow key={message.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{message.lead_name}</p>
                            <p className="text-sm text-muted-foreground">{message.lead_email}</p>
                          </div>
                        </TableCell>
                        <TableCell>{message.subject}</TableCell>
                        <TableCell>{message.campaign_name}</TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              message.status === "replied"
                                ? "default"
                                : message.status === "opened" || message.status === "clicked"
                                  ? "secondary"
                                  : message.status === "delivered" || message.status === "sent"
                                    ? "outline"
                                    : "destructive"
                            }
                            className={
                              message.status === "replied"
                                ? "bg-green-500 hover:bg-green-600"
                                : message.status === "clicked"
                                  ? "bg-blue-500 hover:bg-blue-600"
                                  : ""
                            }
                          >
                            {message.status === "sent"
                              ? "Envoyé"
                              : message.status === "delivered"
                                ? "Délivré"
                                : message.status === "opened"
                                  ? "Ouvert"
                                  : message.status === "clicked"
                                    ? "Cliqué"
                                    : message.status === "replied"
                                      ? "Répondu"
                                      : message.status === "bounced"
                                        ? "Rebond"
                                        : "Échec"}
                          </Badge>
                        </TableCell>
                        <TableCell>{formatDate(message.sent_date)}</TableCell>
                        <TableCell>{formatDate(message.open_date)}</TableCell>
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
                              <DropdownMenuItem onClick={() => window.open(`/admin/messaging/${message.id}`)}>
                                Voir les détails
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleResendMessage(message.id)}>
                                Renvoyer
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="text-red-600"
                                onClick={() => {
                                  // Logique de suppression
                                  toast({
                                    title: "Message supprimé",
                                    description: "Le message a été supprimé avec succès."
                                  })
                                }}
                              >
                                Supprimer
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
} 