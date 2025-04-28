import { Calendar, Download, Eye, Key, Lock, RefreshCw, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"

export default function SecurityPage() {
  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Sécurité</h2>
          <p className="text-muted-foreground">Gérez la sécurité et les accès au système.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Calendar className="mr-2 h-4 w-4" />
            Période
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Exporter
          </Button>
          <Button className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200">
            <RefreshCw className="mr-2 h-4 w-4" />
            Actualiser
          </Button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Rechercher dans les logs..." className="pl-8" />
        </div>
        <Select defaultValue="all">
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Type d'événement" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les événements</SelectItem>
            <SelectItem value="login">Connexions</SelectItem>
            <SelectItem value="logout">Déconnexions</SelectItem>
            <SelectItem value="failed">Échecs de connexion</SelectItem>
            <SelectItem value="password">Changements de mot de passe</SelectItem>
          </SelectContent>
        </Select>
        <Select defaultValue="all">
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Utilisateur" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les utilisateurs</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="jean">Jean Dupont</SelectItem>
            <SelectItem value="marie">Marie Martin</SelectItem>
            <SelectItem value="pierre">Pierre Durand</SelectItem>
            <SelectItem value="sophie">Sophie Lefebvre</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="logs" className="space-y-4">
        <TabsList>
          <TabsTrigger value="logs">Logs de connexion</TabsTrigger>
          <TabsTrigger value="api">Jetons API</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
        </TabsList>
        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Journal de connexion</CardTitle>
              <CardDescription>Historique des connexions et tentatives d'accès</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] w-full rounded-md border">
                <div className="p-4">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date et heure</TableHead>
                        <TableHead>Utilisateur</TableHead>
                        <TableHead>Événement</TableHead>
                        <TableHead>Adresse IP</TableHead>
                        <TableHead>Navigateur</TableHead>
                        <TableHead>Statut</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[
                        {
                          timestamp: "2023-06-10 15:45:23",
                          user: "admin@berinia.com",
                          event: "login",
                          ip: "192.168.1.1",
                          browser: "Chrome 114.0.0 / Windows",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-10 14:30:15",
                          user: "jean.dupont@berinia.com",
                          event: "login",
                          ip: "192.168.1.2",
                          browser: "Firefox 113.0 / macOS",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-10 13:15:42",
                          user: "marie.martin@berinia.com",
                          event: "login",
                          ip: "192.168.1.3",
                          browser: "Safari 16.5 / iOS",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-10 12:45:10",
                          user: "unknown@example.com",
                          event: "login",
                          ip: "203.0.113.1",
                          browser: "Chrome 114.0.0 / Windows",
                          status: "failed",
                        },
                        {
                          timestamp: "2023-06-10 11:30:05",
                          user: "pierre.durand@berinia.com",
                          event: "password_change",
                          ip: "192.168.1.4",
                          browser: "Edge 114.0.0 / Windows",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-10 10:15:30",
                          user: "admin@berinia.com",
                          event: "logout",
                          ip: "192.168.1.1",
                          browser: "Chrome 114.0.0 / Windows",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-10 09:45:12",
                          user: "admin@berinia.com",
                          event: "login",
                          ip: "192.168.1.1",
                          browser: "Chrome 114.0.0 / Windows",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-09 17:30:45",
                          user: "unknown@example.com",
                          event: "login",
                          ip: "203.0.113.2",
                          browser: "Chrome 114.0.0 / Linux",
                          status: "failed",
                        },
                        {
                          timestamp: "2023-06-09 16:15:22",
                          user: "sophie.lefebvre@berinia.com",
                          event: "login",
                          ip: "192.168.1.5",
                          browser: "Chrome 114.0.0 / Windows",
                          status: "success",
                        },
                        {
                          timestamp: "2023-06-09 15:45:10",
                          user: "jean.dupont@berinia.com",
                          event: "logout",
                          ip: "192.168.1.2",
                          browser: "Firefox 113.0 / macOS",
                          status: "success",
                        },
                      ].map((log, index) => (
                        <TableRow key={index}>
                          <TableCell>{log.timestamp}</TableCell>
                          <TableCell>{log.user}</TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={
                                log.event === "login"
                                  ? "border-blue-500 text-blue-500"
                                  : log.event === "logout"
                                    ? "border-gray-500 text-gray-500"
                                    : log.event === "password_change"
                                      ? "border-purple-500 text-purple-500"
                                      : "border-red-500 text-red-500"
                              }
                            >
                              {log.event === "login"
                                ? "Connexion"
                                : log.event === "logout"
                                  ? "Déconnexion"
                                  : log.event === "password_change"
                                    ? "Changement de mot de passe"
                                    : "Tentative de connexion"}
                            </Badge>
                          </TableCell>
                          <TableCell>{log.ip}</TableCell>
                          <TableCell>{log.browser}</TableCell>
                          <TableCell>
                            <Badge
                              variant={log.status === "success" ? "default" : "destructive"}
                              className={log.status === "success" ? "bg-green-500 hover:bg-green-600" : ""}
                            >
                              {log.status === "success" ? "Succès" : "Échec"}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Jetons API</CardTitle>
              <CardDescription>Gérez les jetons d'accès à l'API</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex justify-end">
                  <Button>
                    <Key className="mr-2 h-4 w-4" />
                    Créer un nouveau jeton
                  </Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nom</TableHead>
                      <TableHead>Créé par</TableHead>
                      <TableHead>Date de création</TableHead>
                      <TableHead>Dernière utilisation</TableHead>
                      <TableHead>Expiration</TableHead>
                      <TableHead>Statut</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {[
                      {
                        name: "Jeton principal",
                        createdBy: "admin@berinia.com",
                        createdAt: "01/01/2023",
                        lastUsed: "10/06/2023 15:30",
                        expiration: "01/01/2024",
                        status: "active",
                      },
                      {
                        name: "Jeton d'intégration GHL",
                        createdBy: "admin@berinia.com",
                        createdAt: "15/03/2023",
                        lastUsed: "10/06/2023 14:45",
                        expiration: "15/03/2024",
                        status: "active",
                      },
                      {
                        name: "Jeton de test",
                        createdBy: "jean.dupont@berinia.com",
                        createdAt: "10/05/2023",
                        lastUsed: "15/05/2023 10:20",
                        expiration: "10/06/2023",
                        status: "expired",
                      },
                      {
                        name: "Jeton d'export",
                        createdBy: "admin@berinia.com",
                        createdAt: "01/06/2023",
                        lastUsed: "09/06/2023 16:15",
                        expiration: "01/12/2023",
                        status: "active",
                      },
                    ].map((token, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{token.name}</TableCell>
                        <TableCell>{token.createdBy}</TableCell>
                        <TableCell>{token.createdAt}</TableCell>
                        <TableCell>{token.lastUsed}</TableCell>
                        <TableCell>{token.expiration}</TableCell>
                        <TableCell>
                          <Badge
                            variant={token.status === "active" ? "default" : "outline"}
                            className={token.status === "active" ? "bg-green-500 hover:bg-green-600" : ""}
                          >
                            {token.status === "active" ? "Actif" : "Expiré"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end space-x-2">
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm">
                              <RefreshCw className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm" className="text-red-500">
                              <Lock className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Paramètres de sécurité</CardTitle>
              <CardDescription>Configurez les paramètres de sécurité du système</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Authentification</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Authentification à deux facteurs (2FA)</p>
                      <p className="text-sm text-muted-foreground">
                        Exiger l'authentification à deux facteurs pour tous les utilisateurs
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Verrouillage de compte</p>
                      <p className="text-sm text-muted-foreground">
                        Verrouiller le compte après 5 tentatives de connexion échouées
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Expiration de session</p>
                      <p className="text-sm text-muted-foreground">
                        Déconnecter automatiquement après 30 minutes d'inactivité
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Politique de mot de passe</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Complexité du mot de passe</p>
                      <p className="text-sm text-muted-foreground">
                        Exiger des mots de passe complexes (majuscules, minuscules, chiffres, caractères spéciaux)
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Longueur minimale</p>
                      <p className="text-sm text-muted-foreground">Exiger des mots de passe d'au moins 12 caractères</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Expiration du mot de passe</p>
                      <p className="text-sm text-muted-foreground">
                        Exiger un changement de mot de passe tous les 90 jours
                      </p>
                    </div>
                    <Switch />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Historique des mots de passe</p>
                      <p className="text-sm text-muted-foreground">
                        Empêcher la réutilisation des 5 derniers mots de passe
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Restrictions d'accès</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Restriction par adresse IP</p>
                      <p className="text-sm text-muted-foreground">
                        Limiter l'accès à des adresses IP spécifiques ou plages d'adresses
                      </p>
                    </div>
                    <Switch />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Restriction par localisation</p>
                      <p className="text-sm text-muted-foreground">Limiter l'accès à des pays ou régions spécifiques</p>
                    </div>
                    <Switch />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Restriction par horaire</p>
                      <p className="text-sm text-muted-foreground">Limiter l'accès à des plages horaires spécifiques</p>
                    </div>
                    <Switch />
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Journalisation et surveillance</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Journalisation des connexions</p>
                      <p className="text-sm text-muted-foreground">
                        Enregistrer toutes les tentatives de connexion réussies et échouées
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Journalisation des actions</p>
                      <p className="text-sm text-muted-foreground">
                        Enregistrer toutes les actions effectuées par les utilisateurs
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Alertes de sécurité</p>
                      <p className="text-sm text-muted-foreground">Envoyer des alertes en cas d'activité suspecte</p>
                    </div>
                    <Switch defaultChecked />
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
