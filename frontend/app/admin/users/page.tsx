import { Check, Edit, Key, MoreHorizontal, Plus, Shield, Trash2, User } from "lucide-react"
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
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function UsersPage() {
  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Utilisateurs</h2>
          <p className="text-muted-foreground">Gérez les utilisateurs et leurs permissions.</p>
        </div>
        <Button className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200">
          <Plus className="mr-2 h-4 w-4" />
          Nouvel utilisateur
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Input placeholder="Rechercher un utilisateur..." className="max-w-sm" />
      </div>

      <Card>
        <CardHeader className="py-4">
          <CardTitle>Liste des utilisateurs</CardTitle>
          <CardDescription>Tous les utilisateurs ayant accès au système</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Utilisateur</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Rôle</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Dernière connexion</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[
                {
                  id: 1,
                  name: "Admin",
                  email: "admin@berinia.com",
                  role: "admin",
                  status: "active",
                  lastLogin: "10/06/2023 15:45",
                  avatar: "A",
                },
                {
                  id: 2,
                  name: "Jean Dupont",
                  email: "jean.dupont@berinia.com",
                  role: "manager",
                  status: "active",
                  lastLogin: "10/06/2023 14:30",
                  avatar: "JD",
                },
                {
                  id: 3,
                  name: "Marie Martin",
                  email: "marie.martin@berinia.com",
                  role: "analyst",
                  status: "active",
                  lastLogin: "10/06/2023 10:15",
                  avatar: "MM",
                },
                {
                  id: 4,
                  name: "Pierre Durand",
                  email: "pierre.durand@berinia.com",
                  role: "viewer",
                  status: "active",
                  lastLogin: "09/06/2023 16:20",
                  avatar: "PD",
                },
                {
                  id: 5,
                  name: "Sophie Lefebvre",
                  email: "sophie.lefebvre@berinia.com",
                  role: "analyst",
                  status: "inactive",
                  lastLogin: "01/06/2023 09:45",
                  avatar: "SL",
                },
              ].map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <Avatar>
                        <AvatarImage src={`/placeholder.svg?height=40&width=40&text=${user.avatar}`} />
                        <AvatarFallback>{user.avatar}</AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{user.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {user.role === "admin" ? (
                        <Shield className="h-4 w-4 text-red-500" />
                      ) : user.role === "manager" ? (
                        <Shield className="h-4 w-4 text-purple-500" />
                      ) : user.role === "analyst" ? (
                        <User className="h-4 w-4 text-blue-500" />
                      ) : (
                        <User className="h-4 w-4 text-gray-500" />
                      )}
                      <span>
                        {user.role === "admin"
                          ? "Administrateur"
                          : user.role === "manager"
                            ? "Manager"
                            : user.role === "analyst"
                              ? "Analyste"
                              : "Lecteur"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={user.status === "active" ? "default" : "outline"}
                      className={user.status === "active" ? "bg-green-500 hover:bg-green-600" : ""}
                    >
                      {user.status === "active" ? "Actif" : "Inactif"}
                    </Badge>
                  </TableCell>
                  <TableCell>{user.lastLogin}</TableCell>
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
                          <Edit className="mr-2 h-4 w-4" />
                          Modifier
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Key className="mr-2 h-4 w-4" />
                          Réinitialiser le mot de passe
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        {user.status === "active" ? (
                          <DropdownMenuItem>
                            <User className="mr-2 h-4 w-4" />
                            Désactiver
                          </DropdownMenuItem>
                        ) : (
                          <DropdownMenuItem>
                            <Check className="mr-2 h-4 w-4" />
                            Activer
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-red-600 dark:text-red-400">
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
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Rôles et permissions</CardTitle>
          <CardDescription>Définition des rôles et des permissions associées</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-red-500" />
                <h3 className="text-lg font-medium">Administrateur</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Accès complet à toutes les fonctionnalités du système. Peut gérer les utilisateurs, les paramètres et
                toutes les données.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                <Badge variant="outline" className="justify-center">
                  Gestion des utilisateurs
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Paramètres système
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des campagnes
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des agents
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des niches
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des leads
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Accès aux logs
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Accès à l'API
                </Badge>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-purple-500" />
                <h3 className="text-lg font-medium">Manager</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Peut gérer les campagnes, les agents et les niches. Accès limité aux paramètres système.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                <Badge variant="outline" className="justify-center">
                  Gestion des campagnes
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des agents
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des niches
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Gestion des leads
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Accès aux statistiques
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Accès limité aux logs
                </Badge>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-blue-500" />
                <h3 className="text-lg font-medium">Analyste</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Peut analyser les données et les performances. Accès en lecture seule aux campagnes et aux niches.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                <Badge variant="outline" className="justify-center">
                  Lecture des campagnes
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Lecture des niches
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Lecture des leads
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Accès aux statistiques
                </Badge>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-500" />
                <h3 className="text-lg font-medium">Lecteur</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Accès en lecture seule aux données. Ne peut pas modifier les campagnes, les agents ou les niches.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                <Badge variant="outline" className="justify-center">
                  Lecture des campagnes
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Lecture des niches
                </Badge>
                <Badge variant="outline" className="justify-center">
                  Lecture des leads
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
