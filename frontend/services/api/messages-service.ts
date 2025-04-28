/**
 * Service de gestion des messages
 *
 * Gère toutes les opérations liées aux messages envoyés aux leads.
 */

import { api, type ApiResponse, type PaginatedResponse } from "../api-interceptor"

// Types
export interface Message {
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

export interface MessageCreate {
  lead_id: number
  lead_name: string
  lead_email: string
  subject: string
  content: string
  campaign_id: number
  campaign_name: string
}

export interface MessageFilter {
  status?: string
  campaign_id?: number
  lead_id?: number
  date_from?: string
  date_to?: string
  search?: string
}

/**
 * Service de gestion des messages
 */
class MessagesService {
  /**
   * Récupère la liste des messages avec pagination et filtres
   */
  async getMessages(page = 1, limit = 10, filters?: MessageFilter): Promise<ApiResponse<PaginatedResponse<Message>>> {
    return api.get<PaginatedResponse<Message>>("/api/messages", { 
      params: {
        page,
        limit,
        ...filters
      }
    })
  }

  /**
   * Récupère les détails d'un message spécifique
   */
  async getMessage(id: number): Promise<ApiResponse<Message>> {
    return api.get<Message>(`/api/messages/${id}`)
  }

  /**
   * Crée un nouveau message
   */
  async createMessage(message: MessageCreate): Promise<ApiResponse<Message>> {
    return api.post<Message>("/api/messages", message)
  }

  /**
   * Renvoie un message existant
   */
  async resendMessage(id: number): Promise<ApiResponse<Message>> {
    return api.post<Message>(`/api/messages/${id}/resend`)
  }

  /**
   * Supprime un message
   */
  async deleteMessage(id: number): Promise<ApiResponse<void>> {
    return api.delete<void>(`/api/messages/${id}`)
  }

  /**
   * Récupère les statistiques des messages
   */
  async getMessageStats(campaignId?: number): Promise<ApiResponse<any>> {
    return api.get("/api/messages/stats", {
      params: {
        campaign_id: campaignId
      }
    })
  }
}

export const messagesService = new MessagesService() 