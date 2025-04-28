/**
 * Service de gestion des agents IA
 *
 * Gère toutes les opérations liées aux agents IA qui collectent et traitent les données.
 */

import { api, type ApiResponse } from "../api-interceptor"
import { buildRealAgentsList, generateAgentLogs } from "./real-agents-service"

// Types
export interface Agent {
  id: number
  nom: string
  type: string
  statut: string
  derniere_execution: string
  leads_generes: number
  campagnes_actives: number
}

export interface AgentLog {
  timestamp: string
  level: "info" | "success" | "warning" | "error"
  message: string
  details?: any
}

export interface AgentRestartRequest {
  force?: boolean
  reason?: string
}

export interface AgentCreate {
  nom: string
  type: string
  statut?: string
}

export interface AgentUpdate {
  nom?: string
  type?: string
  statut?: string
}

// Données mockées
const mockAgents: Agent[] = [
  {
    id: 1,
    nom: "Scraper Agent",
    type: "Collection",
    statut: "active",
    derniere_execution: "Il y a 5 minutes",
    leads_generes: 342,
    campagnes_actives: 3,
  },
  {
    id: 2,
    nom: "Cleaner Agent",
    type: "Traitement",
    statut: "active",
    derniere_execution: "Il y a 12 minutes",
    leads_generes: 342,
    campagnes_actives: 3,
  },
  {
    id: 3,
    nom: "Pivot Agent",
    type: "Analyse",
    statut: "active",
    derniere_execution: "Il y a 30 minutes",
    leads_generes: 0,
    campagnes_actives: 5,
  },
  {
    id: 4,
    nom: "Analytics Agent",
    type: "Analyse",
    statut: "error",
    derniere_execution: "Il y a 1 heure",
    leads_generes: 0,
    campagnes_actives: 8,
  },
  {
    id: 5,
    nom: "Outreach Agent",
    type: "Communication",
    statut: "active",
    derniere_execution: "Il y a 15 minutes",
    leads_generes: 128,
    campagnes_actives: 4,
  },
  {
    id: 6,
    nom: "Monitoring Agent",
    type: "Surveillance",
    statut: "warning",
    derniere_execution: "Il y a 45 minutes",
    leads_generes: 0,
    campagnes_actives: 8,
  },
  {
    id: 7,
    nom: "Integration Agent",
    type: "Intégration",
    statut: "inactive",
    derniere_execution: "Il y a 2 jours",
    leads_generes: 0,
    campagnes_actives: 0,
  },
]

// Logs mockés pour les agents
const mockAgentLogs: Record<number, AgentLog[]> = {
  4: [
    {
      timestamp: "2023-06-10 16:20:45",
      level: "error",
      message: "Erreur lors de l'analyse des données : API timeout",
      details: {
        errorCode: "API_TIMEOUT",
        endpoint: "https://api.example.com/data",
        responseTime: 30000,
      },
    },
    {
      timestamp: "2023-06-10 16:21:00",
      level: "info",
      message: "Tentative de reconnexion à l'API",
    },
    {
      timestamp: "2023-06-10 16:21:30",
      level: "error",
      message: "Échec de la reconnexion à l'API",
      details: {
        errorCode: "CONNECTION_FAILED",
        endpoint: "https://api.example.com/data",
        attempts: 3,
      },
    },
  ],
  6: [
    {
      timestamp: "2023-06-10 16:30:00",
      level: "warning",
      message: "Le taux de réponse pour la campagne 'Consultants RH Lille' est inférieur au seuil défini",
      details: {
        campaign: "Consultants RH Lille",
        currentRate: 3.2,
        threshold: 5.0,
      },
    },
  ],
}

/**
 * Service de gestion des agents IA
 */
class AgentsService {
  // Utiliser les vrais agents au lieu des agents mockés
  private realAgents: Agent[] = buildRealAgentsList();

  /**
   * Récupère la liste des agents
   */
  async getAgents(filters?: any): Promise<ApiResponse<Agent[]>> {
    // Filtrer les agents selon les critères (si fournis)
    let filteredAgents = [...this.realAgents];

    if (filters) {
      if (filters.status && filters.status !== "all") {
        filteredAgents = filteredAgents.filter((a) => a.statut === filters.status);
      }

      if (filters.type) {
        filteredAgents = filteredAgents.filter((a) => a.type === filters.type);
      }

      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        filteredAgents = filteredAgents.filter((a) => a.nom.toLowerCase().includes(searchLower));
      }
    }

    // Simuler une réponse API
    const response = {
      data: filteredAgents,
      status: 200
    };

    return Promise.resolve(response as ApiResponse<Agent[]>);
  }

  /**
   * Récupère les détails d'un agent spécifique
   */
  async getAgent(id: number): Promise<ApiResponse<Agent>> {
    const agent = this.realAgents.find((a) => a.id === id);

    if (!agent) {
      throw new Error("Agent non trouvé");
    }

    // Simuler une réponse API
    const response = {
      data: agent,
      status: 200
    };

    return Promise.resolve(response as ApiResponse<Agent>);
  }

  /**
   * Redémarre un agent en erreur
   */
  async restartAgent(id: number, options?: AgentRestartRequest): Promise<ApiResponse<Agent>> {
    const agentIndex = this.realAgents.findIndex((a) => a.id === id);

    if (agentIndex === -1) {
      throw new Error("Agent non trouvé");
    }

    const agent = this.realAgents[agentIndex];

    // Vérifier si l'agent est déjà actif
    if (agent.statut === "active" && !options?.force) {
      throw new Error("L'agent est déjà actif");
    }

    // Mettre à jour le statut de l'agent
    const updatedAgent: Agent = {
      ...agent,
      statut: "active",
      derniere_execution: "À l'instant",
    };

    // Mettre à jour l'agent dans la liste
    this.realAgents[agentIndex] = updatedAgent;

    // Simuler une réponse API
    const response = {
      data: updatedAgent,
      status: 200
    };

    return Promise.resolve(response as ApiResponse<Agent>);
  }

  /**
   * Récupère les logs d'un agent
   */
  async getAgentLogs(id: number, filters?: any): Promise<ApiResponse<AgentLog[]>> {
    const agent = this.realAgents.find((a) => a.id === id);

    if (!agent) {
      throw new Error("Agent non trouvé");
    }

    // Générer des logs réalistes pour cet agent
    let logs = generateAgentLogs(agent.nom);

    // Filtrer les logs selon les critères (si fournis)
    if (filters) {
      if (filters.level && filters.level !== "all") {
        logs = logs.filter((l) => l.level === filters.level);
      }

      if (filters.date) {
        logs = logs.filter((l) => l.timestamp.startsWith(filters.date));
      }

      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        logs = logs.filter((l) => l.message.toLowerCase().includes(searchLower));
      }
    }

    // Simuler une réponse API
    const response = {
      data: logs,
      status: 200
    };

    return Promise.resolve(response as ApiResponse<AgentLog[]>);
  }

  /**
   * Crée un nouvel agent
   */
  async createAgent(agentData: AgentCreate): Promise<ApiResponse<Agent>> {
    // Créer un nouvel agent
    const newId = this.realAgents.length + 1;
    const newAgent: Agent = {
      id: newId,
      nom: agentData.nom,
      type: agentData.type,
      statut: agentData.statut || "inactive",
      derniere_execution: "Jamais",
      leads_generes: 0,
      campagnes_actives: 0
    };

    // Ajouter l'agent à la liste
    this.realAgents.push(newAgent);

    // Simuler une réponse API
    const response = {
      data: newAgent,
      status: 201
    };

    return Promise.resolve(response as ApiResponse<Agent>);
  }

  /**
   * Met à jour un agent existant
   */
  async updateAgent(id: number, updateData: AgentUpdate): Promise<ApiResponse<Agent>> {
    const agentIndex = this.realAgents.findIndex((a) => a.id === id);

    if (agentIndex === -1) {
      throw new Error("Agent non trouvé");
    }

    // Mettre à jour l'agent
    const updatedAgent: Agent = {
      ...this.realAgents[agentIndex],
      ...updateData
    };

    // Mettre à jour l'agent dans la liste
    this.realAgents[agentIndex] = updatedAgent;

    // Simuler une réponse API
    const response = {
      data: updatedAgent,
      status: 200
    };

    return Promise.resolve(response as ApiResponse<Agent>);
  }

  /**
   * Supprime un agent
   */
  async deleteAgent(id: number): Promise<ApiResponse<void>> {
    const agentIndex = this.realAgents.findIndex((a) => a.id === id);

    if (agentIndex === -1) {
      throw new Error("Agent non trouvé");
    }

    // Supprimer l'agent de la liste
    this.realAgents.splice(agentIndex, 1);

    // Simuler une réponse API
    const response = {
      data: undefined,
      status: 204
    };

    return Promise.resolve(response as ApiResponse<void>);
  }
}

export const agentsService = new AgentsService()
