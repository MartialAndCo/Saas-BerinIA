import { Cloud, Database, Globe, MessageSquare, Save, Slack, Webhook } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Paramètres</h2>
          <p className="text-muted-foreground">Configurez les paramètres système et les intégrations.</p>
        </div>
        <Button className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200">
          <Save className="mr-2 h-4 w-4" />
          Enregistrer les modifications
        </Button>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">Général</TabsTrigger>
          <TabsTrigger value="integrations">Intégrations</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="scheduling">Planification</TabsTrigger>
        </TabsList>
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Paramètres généraux</CardTitle>
              <CardDescription>Configurez les paramètres généraux du système</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="company-name">Nom de l'entreprise</Label>
                <Input id="company-name" defaultValue="BerinIA" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="admin-email">Email administrateur</Label>
                <Input id="admin-email" type="email" defaultValue="admin@berinia.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="timezone">Fuseau horaire</Label>
                <Select defaultValue="europe-paris">
                  <SelectTrigger id="timezone">
                    <SelectValue placeholder="Sélectionnez un fuseau horaire" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="europe-paris">Europe/Paris</SelectItem>
                    <SelectItem value="europe-london">Europe/London</SelectItem>
                    <SelectItem value="america-new_york">America/New_York</SelectItem>
                    <SelectItem value="asia-tokyo">Asia/Tokyo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="language">Langue</Label>
                <Select defaultValue="fr">
                  <SelectTrigger id="language">
                    <SelectValue placeholder="Sélectionnez une langue" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fr">Français</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="de">Deutsch</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Limites système</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="max-leads">Nombre maximum de leads par scrape</Label>
                    <Input id="max-leads" type="number" defaultValue="500" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max-campaigns">Nombre maximum de campagnes actives</Label>
                    <Input id="max-campaigns" type="number" defaultValue="20" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="conversion-threshold">Seuil de taux de conversion (%)</Label>
                    <Input id="conversion-threshold" type="number" defaultValue="5" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cpl-threshold">Seuil de coût par lead (€)</Label>
                    <Input id="cpl-threshold" type="number" defaultValue="3" />
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button variant="outline" className="mr-2">
                Annuler
              </Button>
              <Button>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="integrations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Intégrations</CardTitle>
              <CardDescription>Configurez les intégrations avec des services externes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <Slack className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">Slack</h3>
                      <p className="text-sm text-muted-foreground">Intégration pour les notifications</p>
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="pl-12 space-y-2">
                  <Label htmlFor="slack-webhook">URL du Webhook Slack</Label>
                  <Input
                    id="slack-webhook"
                    defaultValue="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
                  />
                  <div className="flex items-center space-x-2 mt-2">
                    <Label htmlFor="slack-channel" className="min-w-[100px]">
                      Canal
                    </Label>
                    <Input id="slack-channel" defaultValue="#berinia-alerts" />
                  </div>
                </div>
              </div>
              <Separator />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                      <Database className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">Airtable</h3>
                      <p className="text-sm text-muted-foreground">Intégration pour l'export de leads</p>
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="pl-12 space-y-2">
                  <Label htmlFor="airtable-api-key">Clé API Airtable</Label>
                  <Input id="airtable-api-key" defaultValue="key00000000000000" />
                  <div className="flex items-center space-x-2 mt-2">
                    <Label htmlFor="airtable-base-id" className="min-w-[100px]">
                      ID de la base
                    </Label>
                    <Input id="airtable-base-id" defaultValue="app00000000000000" />
                  </div>
                  <div className="flex items-center space-x-2 mt-2">
                    <Label htmlFor="airtable-table-name" className="min-w-[100px]">
                      Nom de la table
                    </Label>
                    <Input id="airtable-table-name" defaultValue="Leads" />
                  </div>
                </div>
              </div>
              <Separator />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                      <MessageSquare className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">Go High Level</h3>
                      <p className="text-sm text-muted-foreground">Intégration CRM</p>
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="pl-12 space-y-2">
                  <Label htmlFor="ghl-api-key">Clé API GHL</Label>
                  <Input id="ghl-api-key" defaultValue="ghl_00000000000000000000000000000000" />
                  <div className="flex items-center space-x-2 mt-2">
                    <Label htmlFor="ghl-location-id" className="min-w-[100px]">
                      ID de location
                    </Label>
                    <Input id="ghl-location-id" defaultValue="loc_00000000000" />
                  </div>
                </div>
              </div>
              <Separator />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-full bg-orange-100 dark:bg-orange-900 flex items-center justify-center">
                      <Globe className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">Apify</h3>
                      <p className="text-sm text-muted-foreground">Intégration pour le scraping</p>
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="pl-12 space-y-2">
                  <Label htmlFor="apify-api-key">Clé API Apify</Label>
                  <Input id="apify-api-key" defaultValue="apify_api_00000000000000000000000000000000" />
                </div>
              </div>
              <Separator />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <Cloud className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">OpenAI</h3>
                      <p className="text-sm text-muted-foreground">Intégration pour l'IA</p>
                    </div>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="pl-12 space-y-2">
                  <Label htmlFor="openai-api-key">Clé API OpenAI</Label>
                  <Input id="openai-api-key" defaultValue="sk-00000000000000000000000000000000" />
                  <div className="flex items-center space-x-2 mt-2">
                    <Label htmlFor="openai-model" className="min-w-[100px]">
                      Modèle
                    </Label>
                    <Select defaultValue="gpt-4">
                      <SelectTrigger id="openai-model">
                        <SelectValue placeholder="Sélectionnez un modèle" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gpt-4">GPT-4</SelectItem>
                        <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                        <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button variant="outline" className="mr-2">
                Annuler
              </Button>
              <Button>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuration API</CardTitle>
              <CardDescription>Gérez les clés API et les webhooks</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="api-key">Clé API BerinIA</Label>
                <div className="flex space-x-2">
                  <Input id="api-key" defaultValue="ber_00000000000000000000000000000000" readOnly />
                  <Button variant="outline">Régénérer</Button>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Cette clé vous permet d'accéder à l'API BerinIA. Ne la partagez pas.
                </p>
              </div>
              <Separator />
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Webhooks sortants</h3>
                <p className="text-sm text-muted-foreground">
                  Configurez des webhooks pour recevoir des notifications sur des événements spécifiques.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                        <Webhook className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div>
                        <h4 className="font-medium">Webhook de leads</h4>
                        <p className="text-sm text-muted-foreground">Notifié lors de la collecte de nouveaux leads</p>
                      </div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="pl-12 space-y-2">
                    <Label htmlFor="leads-webhook-url">URL du webhook</Label>
                    <Input id="leads-webhook-url" defaultValue="https://example.com/webhook/leads" />
                    <div className="flex items-center space-x-2 mt-2">
                      <Label htmlFor="leads-webhook-secret" className="min-w-[100px]">
                        Secret
                      </Label>
                      <Input id="leads-webhook-secret" defaultValue="whsec_00000000000000000000000000000000" />
                    </div>
                  </div>
                </div>
                <div className="space-y-4 mt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                        <Webhook className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div>
                        <h4 className="font-medium">Webhook de campagnes</h4>
                        <p className="text-sm text-muted-foreground">
                          Notifié lors des changements de statut des campagnes
                        </p>
                      </div>
                    </div>
                    <Switch />
                  </div>
                  <div className="pl-12 space-y-2">
                    <Label htmlFor="campaigns-webhook-url">URL du webhook</Label>
                    <Input id="campaigns-webhook-url" defaultValue="https://example.com/webhook/campaigns" />
                    <div className="flex items-center space-x-2 mt-2">
                      <Label htmlFor="campaigns-webhook-secret" className="min-w-[100px]">
                        Secret
                      </Label>
                      <Input id="campaigns-webhook-secret" defaultValue="whsec_00000000000000000000000000000000" />
                    </div>
                  </div>
                </div>
              </div>
              <Separator />
              <div className="space-y-2">
                <Label htmlFor="cors-origins">Origines CORS autorisées</Label>
                <Textarea
                  id="cors-origins"
                  placeholder="https://example.com
https://app.example.com"
                  defaultValue="https://berinia.com
https://app.berinia.com"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Une origine par ligne. Laissez vide pour autoriser toutes les origines.
                </p>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button variant="outline" className="mr-2">
                Annuler
              </Button>
              <Button>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Paramètres de notifications</CardTitle>
              <CardDescription>Configurez les notifications système et par email</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Notifications système</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="notify-new-leads">Nouveaux leads</Label>
                    <Switch id="notify-new-leads" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="notify-campaign-status">Changement de statut des campagnes</Label>
                    <Switch id="notify-campaign-status" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="notify-agent-error">Erreurs des agents</Label>
                    <Switch id="notify-agent-error" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="notify-pivot-recommendation">Recommandations de pivot</Label>
                    <Switch id="notify-pivot-recommendation" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="notify-system-error">Erreurs système</Label>
                    <Switch id="notify-system-error" defaultChecked />
                  </div>
                </div>
              </div>
              <Separator />
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Notifications par email</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="email-new-leads">Nouveaux leads</Label>
                    <Switch id="email-new-leads" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="email-campaign-status">Changement de statut des campagnes</Label>
                    <Switch id="email-campaign-status" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="email-agent-error">Erreurs des agents</Label>
                    <Switch id="email-agent-error" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="email-daily-report">Rapport quotidien</Label>
                    <Switch id="email-daily-report" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="email-weekly-report">Rapport hebdomadaire</Label>
                    <Switch id="email-weekly-report" defaultChecked />
                  </div>
                </div>
                <div className="space-y-2 mt-4">
                  <Label htmlFor="email-recipients">Destinataires des emails</Label>
                  <Textarea
                    id="email-recipients"
                    placeholder="email@example.com
another@example.com"
                    defaultValue="admin@berinia.com
alerts@berinia.com"
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Un email par ligne. Tous les destinataires recevront toutes les notifications activées.
                  </p>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button variant="outline" className="mr-2">
                Annuler
              </Button>
              <Button>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="scheduling" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Planification</CardTitle>
              <CardDescription>Configurez les tâches planifiées et les cycles d'exécution</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Cycles d'exécution des agents</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="scraper-frequency">Fréquence du Scraper Agent</Label>
                    <Select defaultValue="daily">
                      <SelectTrigger id="scraper-frequency">
                        <SelectValue placeholder="Sélectionnez une fréquence" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hourly">Toutes les heures</SelectItem>
                        <SelectItem value="daily">Quotidien</SelectItem>
                        <SelectItem value="weekly">Hebdomadaire</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="scraper-time">Heure d'exécution</Label>
                    <Select defaultValue="08:00">
                      <SelectTrigger id="scraper-time">
                        <SelectValue placeholder="Sélectionnez une heure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="00:00">00:00</SelectItem>
                        <SelectItem value="04:00">04:00</SelectItem>
                        <SelectItem value="08:00">08:00</SelectItem>
                        <SelectItem value="12:00">12:00</SelectItem>
                        <SelectItem value="16:00">16:00</SelectItem>
                        <SelectItem value="20:00">20:00</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cleaner-frequency">Fréquence du Cleaner Agent</Label>
                    <Select defaultValue="daily">
                      <SelectTrigger id="cleaner-frequency">
                        <SelectValue placeholder="Sélectionnez une fréquence" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hourly">Toutes les heures</SelectItem>
                        <SelectItem value="daily">Quotidien</SelectItem>
                        <SelectItem value="weekly">Hebdomadaire</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cleaner-time">Heure d'exécution</Label>
                    <Select defaultValue="09:00">
                      <SelectTrigger id="cleaner-time">
                        <SelectValue placeholder="Sélectionnez une heure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="00:00">00:00</SelectItem>
                        <SelectItem value="04:00">04:00</SelectItem>
                        <SelectItem value="09:00">09:00</SelectItem>
                        <SelectItem value="12:00">12:00</SelectItem>
                        <SelectItem value="16:00">16:00</SelectItem>
                        <SelectItem value="20:00">20:00</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="analytics-frequency">Fréquence de l'Analytics Agent</Label>
                    <Select defaultValue="daily">
                      <SelectTrigger id="analytics-frequency">
                        <SelectValue placeholder="Sélectionnez une fréquence" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hourly">Toutes les heures</SelectItem>
                        <SelectItem value="daily">Quotidien</SelectItem>
                        <SelectItem value="weekly">Hebdomadaire</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="analytics-time">Heure d'exécution</Label>
                    <Select defaultValue="16:00">
                      <SelectTrigger id="analytics-time">
                        <SelectValue placeholder="Sélectionnez une heure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="00:00">00:00</SelectItem>
                        <SelectItem value="04:00">04:00</SelectItem>
                        <SelectItem value="08:00">08:00</SelectItem>
                        <SelectItem value="12:00">12:00</SelectItem>
                        <SelectItem value="16:00">16:00</SelectItem>
                        <SelectItem value="20:00">20:00</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pivot-frequency">Fréquence du Pivot Agent</Label>
                    <Select defaultValue="weekly">
                      <SelectTrigger id="pivot-frequency">
                        <SelectValue placeholder="Sélectionnez une fréquence" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">Quotidien</SelectItem>
                        <SelectItem value="weekly">Hebdomadaire</SelectItem>
                        <SelectItem value="monthly">Mensuel</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pivot-time">Jour et heure d'exécution</Label>
                    <Select defaultValue="monday-09:00">
                      <SelectTrigger id="pivot-time">
                        <SelectValue placeholder="Sélectionnez un jour et une heure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monday-09:00">Lundi à 09:00</SelectItem>
                        <SelectItem value="wednesday-09:00">Mercredi à 09:00</SelectItem>
                        <SelectItem value="friday-09:00">Vendredi à 09:00</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
              <Separator />
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Rapports automatiques</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="daily-report">Rapport quotidien</Label>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Activer</span>
                      <Switch id="daily-report" defaultChecked />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="daily-report-time">Heure d'envoi</Label>
                    <Select defaultValue="18:00">
                      <SelectTrigger id="daily-report-time">
                        <SelectValue placeholder="Sélectionnez une heure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="08:00">08:00</SelectItem>
                        <SelectItem value="12:00">12:00</SelectItem>
                        <SelectItem value="18:00">18:00</SelectItem>
                        <SelectItem value="22:00">22:00</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="weekly-report">Rapport hebdomadaire</Label>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Activer</span>
                      <Switch id="weekly-report" defaultChecked />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="weekly-report-day">Jour d'envoi</Label>
                    <Select defaultValue="friday">
                      <SelectTrigger id="weekly-report-day">
                        <SelectValue placeholder="Sélectionnez un jour" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monday">Lundi</SelectItem>
                        <SelectItem value="wednesday">Mercredi</SelectItem>
                        <SelectItem value="friday">Vendredi</SelectItem>
                        <SelectItem value="sunday">Dimanche</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="monthly-report">Rapport mensuel</Label>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Activer</span>
                      <Switch id="monthly-report" defaultChecked />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="monthly-report-day">Jour d'envoi</Label>
                    <Select defaultValue="1">
                      <SelectTrigger id="monthly-report-day">
                        <SelectValue placeholder="Sélectionnez un jour" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1er du mois</SelectItem>
                        <SelectItem value="15">15 du mois</SelectItem>
                        <SelectItem value="last">Dernier jour du mois</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button variant="outline" className="mr-2">
                Annuler
              </Button>
              <Button>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
