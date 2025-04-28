"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, RefreshCw, Send, Trash2, Reply } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { messagesService } from "@/services/api/messages-service"
import { toast } from "@/components/ui/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Type pour les messages de conversation
interface ConversationMessage {
  id: number
  sender: "us" | "lead"
  content: string
  timestamp: string
  status: string
}

export default function MessageDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [message, setMessage] = useState<any>(null)
  const [conversation, setConversation] = useState<ConversationMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [replyText, setReplyText] = useState("")

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        setLoading(true)
        
        // Simuler la récupération du message
        const mockMessage = {
          id: parseInt(params.id),
          lead_id: 101,
          lead_name: "Jean Dupont",
          lead_email: "jean.dupont@example.com",
          subject: "Votre solution de chatbot IA",
          content: "Bonjour Jean, suite à notre analyse de votre site web, nous pensons que l'intégration d'un chatbot IA pourrait augmenter votre taux de conversion de 25%. Notre solution s'intègre facilement à votre site existant et peut être personnalisée pour répondre aux questions spécifiques de vos clients. Seriez-vous disponible pour une démonstration cette semaine ?",
          status: "replied",
          campaign_id: 1,
          campaign_name: "Avocats Paris",
          sent_date: "2023-06-15T10:30:00Z",
          open_date: "2023-06-15T14:22:00Z",
          reply_date: "2023-06-15T16:45:00Z"
        };
        
        // Simuler l'historique de conversation
        const mockConversation: ConversationMessage[] = [
          {
            id: 1,
            sender: "us",
            content: "Bonjour Jean, suite à notre analyse de votre site web, nous pensons que l'intégration d'un chatbot IA pourrait augmenter votre taux de conversion de 25%. Notre solution s'intègre facilement à votre site existant et peut être personnalisée pour répondre aux questions spécifiques de vos clients. Seriez-vous disponible pour une démonstration cette semaine ?",
            timestamp: "2023-06-15T10:30:00Z",
            status: "sent"
          },
          {
            id: 2,
            sender: "lead",
            content: "Bonjour, merci pour votre message. Je serais intéressé par une démonstration. Pouvez-vous me proposer quelques créneaux ?",
            timestamp: "2023-06-15T16:45:00Z",
            status: "received"
          },
          {
            id: 3,
            sender: "us",
            content: "Bonjour Jean, merci pour votre réponse. Nous pouvons vous proposer une démonstration ce jeudi à 14h ou vendredi à 11h. Quelle date vous conviendrait le mieux ?",
            timestamp: "2023-06-16T09:15:00Z",
            status: "sent"
          },
          {
            id: 4,
            sender: "lead",
            content: "Jeudi 14h me convient parfaitement. Comment se déroulera la démonstration ?",
            timestamp: "2023-06-16T10:30:00Z",
            status: "received"
          }
        ];
        
        setMessage(mockMessage);
        setConversation(mockConversation);
        setError(null);
      } catch (err) {
        console.error("Error fetching message:", err);
        setError("Erreur lors du chargement du message");
      } finally {
        setLoading(false);
      }
    };

    fetchMessage();
  }, [params.id]);

  const handleResendMessage = async () => {
    try {
      toast({
        title: "Message renvoyé",
        description: "Le message a été renvoyé avec succès."
      });
    } catch (err) {
      toast({
        title: "Erreur",
        description: "Impossible de renvoyer le message.",
        variant: "destructive"
      });
      console.error(err);
    }
  };

  const handleDeleteMessage = async () => {
    try {
      toast({
        title: "Message supprimé",
        description: "Le message a été supprimé avec succès."
      });
      router.push("/admin/messaging");
    } catch (err) {
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le message.",
        variant: "destructive"
      });
      console.error(err);
    }
  };

  const handleSendReply = () => {
    if (!replyText.trim()) {
      toast({
        title: "Erreur",
        description: "Le message ne peut pas être vide.",
        variant: "destructive"
      });
      return;
    }

    // Ajouter le nouveau message à la conversation
    const newMessage: ConversationMessage = {
      id: conversation.length + 1,
      sender: "us",
      content: replyText,
      timestamp: new Date().toISOString(),
      status: "sent"
    };

    setConversation([...conversation, newMessage]);
    setReplyText("");

    toast({
      title: "Message envoyé",
      description: "Votre réponse a été envoyée avec succès."
    });
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "sent":
        return <Badge variant="outline">Envoyé</Badge>;
      case "delivered":
        return <Badge variant="secondary">Délivré</Badge>;
      case "opened":
        return <Badge variant="default">Ouvert</Badge>;
      case "clicked":
        return <Badge className="bg-blue-500">Cliqué</Badge>;
      case "replied":
        return <Badge className="bg-green-500">Répondu</Badge>;
      case "bounced":
        return <Badge variant="destructive">Rebond</Badge>;
      case "failed":
        return <Badge variant="destructive">Échec</Badge>;
      default:
        return <Badge variant="outline">Inconnu</Badge>;
    }
  };

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center gap-2">
        <Button variant="outline" onClick={() => router.push("/admin/messaging")}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour
        </Button>
        <h2 className="text-3xl font-bold tracking-tight ml-4">Conversation</h2>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin" />
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : message ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="md:col-span-2 flex flex-col gap-5">
            <Card>
              <CardHeader>
                <CardTitle>{message.subject}</CardTitle>
                <CardDescription>
                  Conversation avec {message.lead_name} &lt;{message.lead_email}&gt;
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {conversation.map((msg) => (
                  <div 
                    key={msg.id} 
                    className={`flex ${msg.sender === "us" ? "justify-end" : "justify-start"}`}
                  >
                    <div 
                      className={`flex gap-2 max-w-[80%] ${
                        msg.sender === "us" 
                          ? "flex-row-reverse" 
                          : "flex-row"
                      }`}
                    >
                      <Avatar className={msg.sender === "us" ? "bg-blue-500" : "bg-gray-300"}>
                        <AvatarFallback>
                          {msg.sender === "us" ? "BE" : message.lead_name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div 
                        className={`rounded-lg p-3 ${
                          msg.sender === "us" 
                            ? "bg-blue-500 text-white" 
                            : "bg-gray-100 dark:bg-gray-800"
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        <p 
                          className={`text-xs mt-1 ${
                            msg.sender === "us" 
                              ? "text-blue-100" 
                              : "text-gray-500"
                          }`}
                        >
                          {formatDate(msg.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
              <CardFooter className="flex flex-col gap-3">
                <Textarea 
                  placeholder="Écrivez votre réponse ici..." 
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  className="w-full"
                  rows={4}
                />
                <div className="flex justify-end w-full">
                  <Button onClick={handleSendReply}>
                    <Send className="mr-2 h-4 w-4" />
                    Envoyer
                  </Button>
                </div>
              </CardFooter>
            </Card>
          </div>

          <div className="flex flex-col gap-5">
            <Card>
              <CardHeader>
                <CardTitle>Informations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium">Statut</p>
                    <div className="mt-1">{getStatusBadge(message.status)}</div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium">Destinataire</p>
                    <p className="text-sm">{message.lead_name}</p>
                    <p className="text-sm text-muted-foreground">{message.lead_email}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium">Campagne</p>
                    <p className="text-sm">{message.campaign_name}</p>
                  </div>
                  
                  <Separator />
                  
                  <div>
                    <p className="text-sm font-medium">Premier message</p>
                    <p className="text-sm">{formatDate(message.sent_date)}</p>
                  </div>
                  
                  {message.open_date && (
                    <div>
                      <p className="text-sm font-medium">Date d'ouverture</p>
                      <p className="text-sm">{formatDate(message.open_date)}</p>
                    </div>
                  )}
                  
                  {message.reply_date && (
                    <div>
                      <p className="text-sm font-medium">Première réponse</p>
                      <p className="text-sm">{formatDate(message.reply_date)}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline"
                    className="w-full"
                    onClick={handleResendMessage}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Renvoyer le message
                  </Button>
                  <Button 
                    variant="destructive" 
                    className="w-full"
                    onClick={handleDeleteMessage}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Supprimer la conversation
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <Alert>
          <AlertTitle>Message non trouvé</AlertTitle>
          <AlertDescription>Le message demandé n'existe pas ou a été supprimé.</AlertDescription>
        </Alert>
      )}
    </div>
  )
} 