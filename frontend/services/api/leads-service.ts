/**
 * Service de gestion des leads
 *
 * Gère toutes les opérations liées aux leads générés par les campagnes.
 */

import { api, type ApiResponse, type PaginatedResponse } from "../api-interceptor"

// Types
export interface Lead {
  id: number
  nom: string
  email: string
  telephone: string
  entreprise: string
  statut: string
  date_creation: string
  campagne_id: number
}

export interface LeadCreate {
  nom: string
  email: string
  telephone?: string
  entreprise?: string
  statut?: string
  campagne_id?: number
}

export interface LeadUpdate {
  nom?: string
  email?: string
  telephone?: string
  entreprise?: string
  statut?: string
  campagne_id?: number
}

export interface LeadStatusUpdateRequest {
  status: "new" | "contacted" | "qualified" | "converted" | "lost"
  notes?: string
}

// Données mockées
const mockLeads: Lead[] = [
  {
    id: 1,
    nom: "Jean Dupont",
    email: "jean.dupont@example.com",
    telephone: "06 12 34 56 78",
    entreprise: "Immobilier Paris",
    statut: "new",
    date_creation: "01/06/2023",
    campagne_id: 1,
  },
  {
    id: 2,
    nom: "Marie Martin",
    email: "marie.martin@example.com",
    telephone: "06 23 45 67 89",
    entreprise: "Cabinet Martin",
    statut: "contacted",
    date_creation: "02/06/2023",
    campagne_id: 2,
  },
  {
    id: 3,
    nom: "Pierre Durand",
    email: "pierre.durand@example.com",
    telephone: "06 34 56 78 90",
    entreprise: "Durand Architecture",
    statut: "qualified",
    date_creation: "03/06/2023",
    campagne_id: 3,
  },
  {
    id: 4,
    nom: "Sophie Lefebvre",
    email: "sophie.lefebvre@example.com",
    telephone: "06 45 67 89 01",
    entreprise: "RH Conseil",
    statut: "converted",
    date_creation: "04/06/2023",
    campagne_id: 4,
  },
  {
    id: 5,
    nom: "Thomas Bernard",
    email: "thomas.bernard@example.com",
    telephone: "06 56 78 90 12",
    entreprise: "Clinique Vétérinaire du Parc",
    statut: "lost",
    date_creation: "05/06/2023",
    campagne_id: 5,
  },
]

/**
 * Service de gestion des leads
 */
class LeadsService {
  /**
   * Récupère la liste des leads avec pagination
   */
  async getLeads(page = 1, limit = 10, filters?: any): Promise<ApiResponse<PaginatedResponse<Lead>>> {
    // Filtrer les leads selon les critères (si fournis)
    let filteredLeads = [...mockLeads]

    if (filters) {
      if (filters.status && filters.status !== "all") {
        filteredLeads = filteredLeads.filter((l) => l.statut === filters.status)
      }

      if (filters.campagne_id) {
        filteredLeads = filteredLeads.filter((l) => l.campagne_id === Number(filters.campagne_id))
      }

      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        filteredLeads = filteredLeads.filter(
          (l) =>
            l.nom.toLowerCase().includes(searchLower) ||
            l.email.toLowerCase().includes(searchLower) ||
            l.entreprise.toLowerCase().includes(searchLower),
        )
      }
    }

    // Calculer la pagination
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + limit
    const paginatedLeads = filteredLeads.slice(startIndex, endIndex)

    // Créer la réponse paginée
    const mockResponse: PaginatedResponse<Lead> = {
      data: paginatedLeads,
      total: filteredLeads.length,
      page,
      limit,
      totalPages: Math.ceil(filteredLeads.length / limit),
    }

    return api.get<PaginatedResponse<Lead>>("/leads", mockResponse)
  }

  /**
   * Récupère les détails d'un lead spécifique
   */
  async getLead(id: number): Promise<ApiResponse<Lead>> {
    const lead = mockLeads.find((l) => l.id === id)

    if (!lead) {
      throw new Error("Lead non trouvé")
    }

    return api.get<Lead>(`/leads/${id}`, lead)
  }

  /**
   * Crée un nouveau lead
   */
  async createLead(leadData: LeadCreate): Promise<ApiResponse<Lead>> {
    // Créer un nouveau lead mock
    const newLead: Lead = {
      id: Math.max(...mockLeads.map((l) => l.id)) + 1,
      nom: leadData.nom,
      email: leadData.email,
      telephone: leadData.telephone || "",
      entreprise: leadData.entreprise || "",
      statut: leadData.statut as string || "new",
      date_creation: new Date().toLocaleDateString(),
      campagne_id: leadData.campagne_id || 0,
    }

    return api.post<Lead>("/leads", leadData, newLead)
  }

  /**
   * Met à jour un lead existant
   */
  async updateLead(id: number, leadData: LeadUpdate): Promise<ApiResponse<Lead>> {
    const leadIndex = mockLeads.findIndex((l) => l.id === id)

    if (leadIndex === -1) {
      throw new Error("Lead non trouvé")
    }

    // Mettre à jour le lead mock
    const updatedLead = {
      ...mockLeads[leadIndex],
      ...leadData,
    }

    return api.put<Lead>(`/leads/${id}`, leadData, updatedLead)
  }

  /**
   * Met à jour le statut d'un lead
   */
  async updateLeadStatus(id: number, statusData: LeadStatusUpdateRequest): Promise<ApiResponse<Lead>> {
    const leadIndex = mockLeads.findIndex((l) => l.id === id)

    if (leadIndex === -1) {
      throw new Error("Lead non trouvé")
    }

    // Mettre à jour le statut du lead mock
    const updatedLead = {
      ...mockLeads[leadIndex],
      statut: statusData.status,
    }

    return api.put<Lead>(`/leads/${id}/status`, statusData, updatedLead)
  }

  /**
   * Exporte les leads au format CSV
   */
  async exportLeads(filters?: any): Promise<ApiResponse<Blob>> {
    // Simuler un délai pour l'export
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Dans une vraie implémentation, on retournerait un Blob
    // Pour l'instant, on simule juste une réponse réussie
    return {
      data: new Blob(["mock CSV data"], { type: "text/csv" }),
      status: 200,
    }
  }
}

export const leadsService = new LeadsService()
