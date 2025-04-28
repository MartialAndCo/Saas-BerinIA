/**
 * Service de gestion des campagnes
 *
 * Gère toutes les opérations liées aux campagnes marketing.
 */

import { api, type ApiResponse, type PaginatedResponse } from "../api-interceptor"

// Types
export interface Campaign {
  id: number
  nom: string
  description: string
  statut: "active" | "paused" | "completed" | "warning" | "error"
  niche_id: number
  target_leads: number
  agent: string
  leads: number
  conversion: number
  date_creation: string
  progress: number
}

export interface CampaignCreate {
  nom: string
  description?: string
  niche_id: number
  target_leads?: number
  agent?: string
}

export interface CampaignUpdate {
  nom?: string
  description?: string
  statut?: string
  niche_id?: number
  target_leads?: number
  agent?: string
}

// Données mockées
const mockCampaigns: Campaign[] = [
  {
    id: 1,
    nom: "Agences immobilières Paris",
    description: "",
    statut: "active",
    niche_id: 1,
    target_leads: 342,
    agent: "Scraper Agent",
    leads: 342,
    conversion: 7.8,
    date_creation: "01/05/2023",
    progress: 78,
  },
  {
    id: 2,
    nom: "Avocats d'affaires Lyon",
    description: "",
    statut: "active",
    niche_id: 2,
    target_leads: 215,
    agent: "Scraper Agent",
    leads: 215,
    conversion: 5.2,
    date_creation: "15/05/2023",
    progress: 45,
  },
  {
    id: 3,
    nom: "Architectes Bordeaux",
    description: "",
    statut: "active",
    niche_id: 3,
    target_leads: 189,
    agent: "Scraper Agent",
    leads: 189,
    conversion: 9.1,
    date_creation: "10/05/2023",
    progress: 92,
  },
  {
    id: 4,
    nom: "Consultants RH Lille",
    description: "",
    statut: "warning",
    niche_id: 4,
    target_leads: 78,
    agent: "Scraper Agent",
    leads: 78,
    conversion: 3.2,
    date_creation: "20/05/2023",
    progress: 24,
  },
  {
    id: 5,
    nom: "Cliniques vétérinaires",
    description: "",
    statut: "active",
    niche_id: 5,
    target_leads: 156,
    agent: "Scraper Agent",
    leads: 156,
    conversion: 6.5,
    date_creation: "05/05/2023",
    progress: 62,
  },
  {
    id: 6,
    nom: "Restaurants gastronomiques",
    description: "",
    statut: "paused",
    niche_id: 6,
    target_leads: 98,
    agent: "Scraper Agent",
    leads: 98,
    conversion: 4.8,
    date_creation: "25/04/2023",
    progress: 50,
  },
  {
    id: 7,
    nom: "Écoles de langues",
    description: "",
    statut: "completed",
    niche_id: 7,
    target_leads: 245,
    agent: "Scraper Agent",
    leads: 245,
    conversion: 8.3,
    date_creation: "15/04/2023",
    progress: 100,
  },
  {
    id: 8,
    nom: "Agences de voyage",
    description: "",
    statut: "error",
    niche_id: 8,
    target_leads: 45,
    agent: "Scraper Agent",
    leads: 45,
    conversion: 2.1,
    date_creation: "10/05/2023",
    progress: 30,
  },
]

/**
 * Service de gestion des campagnes
 */
class CampaignsService {
  /**
   * Récupère la liste des campagnes avec pagination
   */
  async getCampaigns(page = 1, limit = 10, filters?: any): Promise<ApiResponse<PaginatedResponse<Campaign>>> {
    // Filtrer les campagnes selon les critères (si fournis)
    let filteredCampaigns = [...mockCampaigns]

    if (filters) {
      if (filters.status && filters.status !== "all") {
        filteredCampaigns = filteredCampaigns.filter((c) => c.statut === filters.status)
      }

      if (filters.niche_id) {
        filteredCampaigns = filteredCampaigns.filter((c) => c.niche_id === filters.niche_id)
      }

      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        filteredCampaigns = filteredCampaigns.filter(
          (c) => c.nom.toLowerCase().includes(searchLower) || c.description.toLowerCase().includes(searchLower),
        )
      }
    }

    // Calculer la pagination
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + limit
    const paginatedCampaigns = filteredCampaigns.slice(startIndex, endIndex)

    // Créer la réponse paginée
    const mockResponse: PaginatedResponse<Campaign> = {
      data: paginatedCampaigns,
      total: filteredCampaigns.length,
      page,
      limit,
      totalPages: Math.ceil(filteredCampaigns.length / limit),
    }

    return api.get<PaginatedResponse<Campaign>>("/campaigns", mockResponse)
  }

  /**
   * Récupère les détails d'une campagne spécifique
   */
  async getCampaign(id: number): Promise<ApiResponse<Campaign>> {
    const campaign = mockCampaigns.find((c) => c.id === id)

    if (!campaign) {
      throw new Error("Campagne non trouvée")
    }

    return api.get<Campaign>(`/campaigns/${id}`, campaign)
  }

  /**
   * Crée une nouvelle campagne
   */
  async createCampaign(campaignData: CampaignCreate): Promise<ApiResponse<Campaign>> {
    // Créer une nouvelle campagne mock
    const newCampaign: Campaign = {
      id: Math.max(...mockCampaigns.map((c) => c.id)) + 1,
      nom: campaignData.nom,
      description: campaignData.description || "",
      statut: campaignData.statut as "active" | "paused" | "completed" | "warning" | "error",
      niche_id: campaignData.niche_id,
      target_leads: campaignData.target_leads || 0,
      agent: campaignData.agent || "Scraper Agent",
      leads: 0,
      conversion: 0,
      date_creation: new Date().toLocaleDateString(),
      progress: 0,
    }

    return api.post<Campaign>("/campaigns", campaignData, newCampaign)
  }

  /**
   * Met à jour une campagne existante
   */
  async updateCampaign(id: number, campaignData: CampaignUpdate): Promise<ApiResponse<Campaign>> {
    const campaignIndex = mockCampaigns.findIndex((c) => c.id === id)

    if (campaignIndex === -1) {
      throw new Error("Campagne non trouvée")
    }

    // Mettre à jour la campagne mock
    const updatedCampaign = {
      ...mockCampaigns[campaignIndex],
      ...campaignData,
    }

    return api.put<Campaign>(`/campaigns/${id}`, campaignData, updatedCampaign)
  }

  /**
   * Supprime une campagne
   */
  async deleteCampaign(id: number): Promise<ApiResponse<void>> {
    const campaignIndex = mockCampaigns.findIndex((c) => c.id === id)

    if (campaignIndex === -1) {
      throw new Error("Campagne non trouvée")
    }

    return api.delete<void>(`/campaigns/${id}`)
  }

  /**
   * Met à jour le statut d'une campagne
   */
  async updateCampaignStatus(id: number, status: "active" | "paused"): Promise<ApiResponse<Campaign>> {
    return this.updateCampaign(id, { statut: status })
  }

  /**
   * Exporte les leads d'une campagne
   */
  async exportCampaignLeads(id: number, format: 'csv' | 'excel' = 'csv'): Promise<ApiResponse<{ message: string }>> {
    return api.get(`/campaigns/${id}/export`, { params: { format } })
  }
}

export const campaignsService = new CampaignsService()
