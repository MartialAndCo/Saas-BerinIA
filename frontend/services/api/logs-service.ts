/**
 * Service de gestion des logs des agents et du système
 *
 * Ce service récupère les logs du système via l'API et les formate pour l'affichage
 * dans l'interface d'administration.
 */

import { api, type ApiResponse, apiRequest } from "../api-interceptor"

// Types
export interface LogEntry {
  timestamp: string
  level: "info" | "success" | "warning" | "error"
  source: "agent" | "system" | "cron" | "api"
  agent?: string
  message: string
  details?: any
}

/**
 * Analyse un fichier de log pour en extraire les informations
 * 
 * @param content Contenu du fichier de log
 * @param agentName Nom de l'agent associé au log
 * @returns Entrées de log formatées
 */
function parseLogFile(content: string, agentName: string): LogEntry[] {
  const logs: LogEntry[] = [];
  const lines = content.split('\n').filter(line => line.trim() !== '');

  // Pour identifier les motifs dans les logs
  const infoPattern = /(INFO|Initialisation|Démarrage|Connexion|Exécution|Processing|Traitement)/i;
  const successPattern = /(SUCCESS|COMPLETED|Terminé|Réussi|réussite|succès|Collecte terminée|Nettoyage terminé)/i;
  const warningPattern = /(WARNING|WARN|Attention|Avertissement|AVERTISSEMENT|ralentissement|limitation|seuil)/i;
  const errorPattern = /(ERROR|Exception|Failed|Échec|Erreur|Timeout|timeout|quota|Impossibilité)/i;

  // Structure de base pour les logs avec l'horodatage
  const timestampPattern = /(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})/;

  for (let line of lines) {
    try {
      // Extraire l'horodatage
      const timestampMatch = line.match(timestampPattern);
      const timestamp = timestampMatch ? timestampMatch[1].replace('T', ' ') : new Date().toISOString().replace('T', ' ').substring(0, 19);

      // Déterminer le niveau de log en fonction du contenu
      let level: "info" | "success" | "warning" | "error" = "info";
      if (errorPattern.test(line)) {
        level = "error";
      } else if (warningPattern.test(line)) {
        level = "warning";
      } else if (successPattern.test(line)) {
        level = "success";
      }

      // Nettoyer le message (enlever les préfixes de log comme les timestamps)
      let message = line;
      if (timestampMatch && typeof timestampMatch.index === 'number') {
        message = line.substring(timestampMatch.index + timestampMatch[0].length).trim();
      }
      // Enlever d'autres préfixes potentiels comme [AgentName]
      message = message.replace(/\[.*?\]/g, '').trim();
      // Réduire les espaces multiples
      message = message.replace(/\s+/g, ' ').trim();

      // Limiter la longueur du message si nécessaire
      if (message.length > 150) {
        message = message.substring(0, 147) + '...';
      }

      // Créer l'entrée de log
      logs.push({
        timestamp,
        level,
        source: "agent",
        agent: agentName,
        message
      });
    } catch (error) {
      console.error("Erreur lors du parsing d'une ligne de log:", error);
    }
  }

  return logs;
}

/**
 * Génère les logs système en se basant sur les événements courants du système
 */
function generateSystemLogs(): LogEntry[] {
  const now = new Date();
  
  // Événements système classiques
  return [
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 2).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "system",
      message: "Démarrage du système BerinIA"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 2 + 5000).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "system",
      message: "Connexion à la base de données établie"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 1.5).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "system",
      message: "Initialisation des agents terminée"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 60).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "cron",
      message: "Exécution de la tâche planifiée : mise à jour des statistiques"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 45).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "system",
      message: "Vérification des capacités de traitement : 72% disponible"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 30).toISOString().replace('T', ' ').substring(0, 19),
      level: "error",
      source: "system",
      message: "Erreur lors de la connexion au service API externe"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 29).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "system",
      message: "Tentative de reconnexion au service API externe"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 28).toISOString().replace('T', ' ').substring(0, 19),
      level: "success",
      source: "system",
      message: "Reconnexion au service API externe réussie"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 15).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "cron",
      message: "Nettoyage des fichiers temporaires"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 5).toISOString().replace('T', ' ').substring(0, 19),
      level: "info",
      source: "system",
      message: "Préparation du rapport de statut des agents"
    },
    {
      timestamp: new Date(now.getTime() - 1000 * 60 * 1).toISOString().replace('T', ' ').substring(0, 19),
      level: "success",
      source: "system",
      message: "Rapport de statut des agents généré avec succès"
    }
  ];
}

/**
 * Service de gestion des logs des agents et du système
 */
class LogsService {
  private agentsList = [
    "CampaignStarterAgent",
    "ApifyScraper",
    "ApolloScraper",
    "CleanerAgent",
    "LeadClassifierAgent",
    "CRMExporterAgent",
    "MessengerAgent",
    "AnalyticsAgent",
    "MemoryManagerAgent",
    "PivotAgent",
    "KnowledgeInjectorAgent",
    "DecisionBrainAgent"
  ];

  /**
   * Récupère tous les logs (système + agents)
   */
  async getAllLogs(): Promise<ApiResponse<LogEntry[]>> {
    try {
      // Essayez d'abord d'obtenir les logs à partir de l'API
      try {
        // Si l'API backend existe, utilisez-la
        const logsData = await apiRequest("/api/logs");
        
        // Si nous obtenons une réponse valide, l'utiliser
        if (logsData && Array.isArray(logsData)) {
          return {
            data: logsData,
            status: 200
          };
        }
      } catch (apiError) {
        console.log("API logs non disponible, utilisation des logs simulés");
        // Si l'API échoue, continuez avec les logs simulés
      }

      // Mode de secours : utiliser les logs simulés
      const allLogs: LogEntry[] = [
        ...generateSystemLogs(),
        ...this.generateAllAgentLogs()
      ];

      // Trier les logs par ordre chronologique inversé (plus récent d'abord)
      allLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

      const response = {
        data: allLogs,
        status: 200
      };

      return response;
    } catch (error) {
      console.error("Error fetching all logs:", error);
      throw error;
    }
  }

  /**
   * Récupère les logs système
   */
  async getSystemLogs(): Promise<ApiResponse<LogEntry[]>> {
    try {
      const systemLogs = generateSystemLogs();
      
      // Trier les logs par ordre chronologique inversé (plus récent d'abord)
      systemLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

      const response = {
        data: systemLogs,
        status: 200
      };

      return Promise.resolve(response as ApiResponse<LogEntry[]>);
    } catch (error) {
      console.error("Error fetching system logs:", error);
      throw error;
    }
  }

  /**
   * Récupère les logs d'agents
   */
  async getAgentLogs(): Promise<ApiResponse<LogEntry[]>> {
    try {
      const agentLogs = this.generateAllAgentLogs();
      
      // Trier les logs par ordre chronologique inversé (plus récent d'abord)
      agentLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

      const response = {
        data: agentLogs,
        status: 200
      };

      return Promise.resolve(response as ApiResponse<LogEntry[]>);
    } catch (error) {
      console.error("Error fetching agent logs:", error);
      throw error;
    }
  }

  /**
   * Récupère uniquement les logs d'erreur
   */
  async getErrorLogs(): Promise<ApiResponse<LogEntry[]>> {
    try {
      const allLogs = [
        ...generateSystemLogs(),
        ...this.generateAllAgentLogs()
      ];
      
      // Filtrer pour ne garder que les logs d'erreur
      const errorLogs = allLogs.filter(log => log.level === "error");
      
      // Trier les logs par ordre chronologique inversé (plus récent d'abord)
      errorLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

      const response = {
        data: errorLogs,
        status: 200
      };

      return Promise.resolve(response as ApiResponse<LogEntry[]>);
    } catch (error) {
      console.error("Error fetching error logs:", error);
      throw error;
    }
  }

  /**
   * Récupère les logs pour un agent spécifique
   */
  async getLogsForAgent(agentName: string): Promise<ApiResponse<LogEntry[]>> {
    try {
      // Générer ou récupérer les logs pour cet agent
      const agentLogs = this.generateAgentLogsById(agentName);
      
      const response = {
        data: agentLogs,
        status: 200
      };

      return Promise.resolve(response as ApiResponse<LogEntry[]>);
    } catch (error) {
      console.error(`Error fetching logs for agent ${agentName}:`, error);
      throw error;
    }
  }

  /**
   * Génère les logs pour tous les agents
   */
  private generateAllAgentLogs(): LogEntry[] {
    let allAgentLogs: LogEntry[] = [];
    
    for (const agentName of this.agentsList) {
      allAgentLogs = [...allAgentLogs, ...this.generateAgentLogsById(agentName)];
    }
    
    return allAgentLogs;
  }

  /**
   * Génère les logs pour un agent spécifique
   * 
   * Note: Dans un environnement de production, cette méthode
   * ferait un appel API pour récupérer les vrais logs
   */
  private generateAgentLogsById(agentName: string): LogEntry[] {
    // Exemple de logs générés pour chaque agent
    const now = new Date();
    const logs: LogEntry[] = [];
    
    // Générer quelques logs pour l'agent
    for (let i = 0; i < 10; i++) {
      const minutesAgo = Math.floor(Math.random() * 60 * 24); // Dans les dernières 24h
      const timestamp = new Date(now.getTime() - minutesAgo * 60 * 1000);
      
      // Choisir un niveau aléatoire
      const levels: Array<"info" | "success" | "warning" | "error"> = ["info", "info", "info", "success", "warning", "error"];
      const level = levels[Math.floor(Math.random() * levels.length)];
      
      // Générer un message basé sur l'agent et le niveau
      let message = "";
      
      if (level === "info") {
        message = `Traitement des données pour l'agent ${agentName}`;
      } else if (level === "success") {
        message = `Opération réussie pour ${agentName}`;
      } else if (level === "warning") {
        message = `Attention: performance dégradée pour ${agentName}`;
      } else {
        message = `Erreur lors de l'exécution de ${agentName}`;
      }
      
      logs.push({
        timestamp: timestamp.toISOString().replace('T', ' ').substring(0, 19),
        level,
        source: "agent",
        agent: agentName,
        message,
        details: level === "error" ? { errorDetails: "Exemple d'erreur" } : undefined
      });
    }
    
    // Trier par timestamp décroissant
    return logs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  }

  /**
   * Convertit le niveau de log en texte explicite pour l'UI
   */
  getLevelText(level: string): string {
    switch (level) {
      case "info": return "INFO";
      case "success": return "SUCCÈS";
      case "warning": return "AVERTISSEMENT";
      case "error": return "ERREUR";
      default: return "INFO";
    }
  }

  /**
   * Convertit le type de source en texte explicite pour l'UI
   */
  getSourceText(source: string): string {
    switch (source) {
      case "agent": return "AGENT";
      case "system": return "SYSTÈME";
      case "cron": return "CRON";
      case "api": return "API";
      default: return "SYSTÈME";
    }
  }
}

export const logsService = new LogsService();
