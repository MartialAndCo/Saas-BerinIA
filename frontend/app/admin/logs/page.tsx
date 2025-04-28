"use client"

import { useState, useEffect } from "react"
import { Bot, Calendar, Download, RefreshCw, Search, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { logsService, type LogEntry } from "@/services/api/logs-service"
import { toast } from "@/components/ui/use-toast"

export default function LogsPage() {
  const [allLogs, setAllLogs] = useState<LogEntry[]>([]);
  const [systemLogs, setSystemLogs] = useState<LogEntry[]>([]);
  const [agentLogs, setAgentLogs] = useState<LogEntry[]>([]);
  const [errorLogs, setErrorLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [logType, setLogType] = useState("all");
  const [logSource, setLogSource] = useState("all");
  const [activeTab, setActiveTab] = useState("all");

  // Charger les logs au chargement de la page
  useEffect(() => {
    fetchAllLogs();
  }, []);

  // Récupérer tous les types de logs
  const fetchAllLogs = async () => {
    setLoading(true);
    try {
      // Récupérer tous les logs
      const allLogsResponse = await logsService.getAllLogs();
      setAllLogs(allLogsResponse.data);
      
      // Récupérer les logs système
      const systemLogsResponse = await logsService.getSystemLogs();
      setSystemLogs(systemLogsResponse.data);
      
      // Récupérer les logs d'agents
      const agentLogsResponse = await logsService.getAgentLogs();
      setAgentLogs(agentLogsResponse.data);
      
      // Récupérer les logs d'erreur
      const errorLogsResponse = await logsService.getErrorLogs();
      setErrorLogs(errorLogsResponse.data);
      
      setLoading(false);
    } catch (error) {
      console.error("Erreur lors du chargement des logs:", error);
      toast({
        title: "Erreur",
        description: "Impossible de charger les logs. Veuillez réessayer.",
        variant: "destructive",
      });
      setLoading(false);
    }
  };

  // Filtrer les logs selon les critères de recherche
  const getFilteredLogs = (logs: LogEntry[]) => {
    return logs.filter(log => {
      // Filtrer par type de log
      if (logType !== "all" && log.level !== logType) {
        return false;
      }
      
      // Filtrer par source
      if (logSource !== "all" && log.source !== logSource) {
        return false;
      }
      
      // Filtrer par recherche textuelle
      if (searchQuery) {
        return (
          log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (log.agent && log.agent.toLowerCase().includes(searchQuery.toLowerCase()))
        );
      }
      
      return true;
    });
  };

  // Gérer la recherche
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Gérer le changement de type de log
  const handleLogTypeChange = (value: string) => {
    setLogType(value);
  };

  // Gérer le changement de source
  const handleSourceChange = (value: string) => {
    setLogSource(value);
  };

  // Gérer l'actualisation des logs
  const handleRefresh = () => {
    fetchAllLogs();
    toast({
      title: "Logs actualisés",
      description: "Les logs ont été mis à jour avec succès.",
    });
  };

  // Gérer le changement d'onglet
  const handleTabChange = (value: string) => {
    setActiveTab(value);
  };

  // Rendu d'une entrée de log
  const renderLogEntry = (log: LogEntry, index: number) => (
    <div
      key={index}
      className="flex items-start space-x-3 border-b border-gray-100 dark:border-gray-800 pb-4 last:border-0 last:pb-0"
    >
      <div
        className={`mt-0.5 rounded-full p-1 ${
          log.level === "info"
            ? "bg-blue-100 dark:bg-blue-900"
            : log.level === "success"
              ? "bg-green-100 dark:bg-green-900"
              : log.level === "warning"
                ? "bg-yellow-100 dark:bg-yellow-900"
                : "bg-red-100 dark:bg-red-900"
        }`}
      >
        {log.source === "agent" ? (
          <Bot
            className={`h-3 w-3 ${
              log.level === "info"
                ? "text-blue-600 dark:text-blue-400"
                : log.level === "success"
                  ? "text-green-600 dark:text-green-400"
                  : log.level === "warning"
                    ? "text-yellow-600 dark:text-yellow-400"
                    : "text-red-600 dark:text-red-400"
            }`}
          />
        ) : (
          <Terminal
            className={`h-3 w-3 ${
              log.level === "info"
                ? "text-blue-600 dark:text-blue-400"
                : log.level === "success"
                  ? "text-green-600 dark:text-green-400"
                  : log.level === "warning"
                    ? "text-yellow-600 dark:text-yellow-400"
                    : "text-red-600 dark:text-red-400"
            }`}
          />
        )}
      </div>
      <div className="flex-1">
        <div className="flex items-center">
          <span className="text-xs text-muted-foreground mr-2">{log.timestamp}</span>
          <Badge
            variant="outline"
            className={`text-xs ${
              log.level === "info"
                ? "border-blue-500 text-blue-500"
                : log.level === "success"
                  ? "border-green-500 text-green-500"
                  : log.level === "warning"
                    ? "border-yellow-500 text-yellow-500"
                    : "border-red-500 text-red-500"
            }`}
          >
            {logsService.getLevelText(log.level)}
          </Badge>
          <Badge variant="secondary" className="ml-2 text-xs">
            {logsService.getSourceText(log.source)}
          </Badge>
          {log.agent && (
            <span className="ml-2 text-xs font-medium text-muted-foreground">{log.agent}</span>
          )}
        </div>
        <p className="text-sm mt-1">{log.message}</p>
        {log.details && (
          <div className="mt-1 text-xs text-muted-foreground">
            {JSON.stringify(log.details)}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Tests & Logs</h2>
          <p className="text-muted-foreground">Consultez les logs système et des agents.</p>
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
          <Button 
            className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 transition-all duration-200"
            onClick={handleRefresh}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Actualiser Logs
          </Button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Rechercher dans les logs..." 
            className="pl-8" 
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>
        <Select defaultValue="all" onValueChange={handleLogTypeChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Type de log" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les logs</SelectItem>
            <SelectItem value="info">Information</SelectItem>
            <SelectItem value="warning">Avertissement</SelectItem>
            <SelectItem value="error">Erreur</SelectItem>
            <SelectItem value="success">Succès</SelectItem>
          </SelectContent>
        </Select>
        <Select defaultValue="all" onValueChange={handleSourceChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Source" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes les sources</SelectItem>
            <SelectItem value="system">Système</SelectItem>
            <SelectItem value="agent">Agents</SelectItem>
            <SelectItem value="cron">Tâches planifiées</SelectItem>
            <SelectItem value="api">API</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="all" className="space-y-4" onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="all">Tous les logs</TabsTrigger>
          <TabsTrigger value="system">Système</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="errors">Erreurs</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Journal d'activité</CardTitle>
              <CardDescription>Tous les logs système et des agents</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] w-full rounded-md border">
                <div className="p-4 space-y-4">
                  {loading ? (
                    <div className="text-center py-8">Chargement des logs...</div>
                  ) : getFilteredLogs(allLogs).length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Aucun log ne correspond à vos critères.
                    </div>
                  ) : (
                    getFilteredLogs(allLogs).map((log, index) => renderLogEntry(log, index))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="system" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Logs système</CardTitle>
              <CardDescription>Logs du système BerinIA</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] w-full rounded-md border">
                <div className="p-4 space-y-4">
                  {loading ? (
                    <div className="text-center py-8">Chargement des logs système...</div>
                  ) : getFilteredLogs(systemLogs).length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Aucun log système ne correspond à vos critères.
                    </div>
                  ) : (
                    getFilteredLogs(systemLogs).map((log, index) => renderLogEntry(log, index))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="agents" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Logs des agents</CardTitle>
              <CardDescription>Activité des agents IA</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] w-full rounded-md border">
                <div className="p-4 space-y-4">
                  {loading ? (
                    <div className="text-center py-8">Chargement des logs des agents...</div>
                  ) : getFilteredLogs(agentLogs).length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Aucun log d'agent ne correspond à vos critères.
                    </div>
                  ) : (
                    getFilteredLogs(agentLogs).map((log, index) => renderLogEntry(log, index))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="errors" className="space-y-4">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Logs d'erreurs</CardTitle>
              <CardDescription>Erreurs système et des agents</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] w-full rounded-md border">
                <div className="p-4 space-y-4">
                  {loading ? (
                    <div className="text-center py-8">Chargement des logs d'erreur...</div>
                  ) : getFilteredLogs(errorLogs).length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Aucun log d'erreur ne correspond à vos critères.
                    </div>
                  ) : (
                    getFilteredLogs(errorLogs).map((log, index) => renderLogEntry(log, index))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
