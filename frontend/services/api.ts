/**
 * Service API principal pour BerinIA
 *
 * Ce service gère toutes les requêtes API de l'application.
 * Pour l'instant, il utilise des données mockées, mais il sera facile
 * de le connecter à une vraie API plus tard.
 */

import { API_BASE_URL, DEFAULT_HEADERS, REQUEST_TIMEOUT, USE_REAL_DATA } from '@/src/config';

// Fonction utilitaire pour vérifier si le code s'exécute côté client
const isClient = typeof window !== 'undefined';

// Types de base
export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

// Fonction générique pour simuler un délai réseau
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// Fonction générique pour simuler une erreur API
const simulateError = (probability = 0.1): boolean => {
  return Math.random() < probability
}

/**
 * Classe principale du service API
 */
class ApiService {
  private baseUrl: string
  private token: string | null

  constructor() {
    this.baseUrl = API_BASE_URL
    this.token = isClient ? localStorage.getItem("token") : null
  }

  /**
   * Configure le token d'authentification
   */
  setToken(token: string): void {
    this.token = token
    if (isClient) {
      localStorage.setItem("token", token)
    }
  }

  /**
   * Supprime le token d'authentification
   */
  clearToken(): void {
    this.token = null
    if (isClient) {
      localStorage.removeItem("token")
    }
  }

  /**
   * Prépare les en-têtes pour les requêtes API
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    }

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
    }

    return headers
  }

  /**
   * Méthode générique pour effectuer des requêtes API
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`
    
    const options: RequestInit = {
      method,
      headers: {
        ...DEFAULT_HEADERS,
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {})
      },
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)
      
      options.signal = controller.signal
      
      const response = await fetch(url, options)
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `API Error: ${response.status}`)
      }
      
      const responseData = await response.json().catch(() => ({}))
      
      return {
        data: responseData,
        status: response.status
      }
    } catch (error) {
      console.error(`API Error (${method} ${endpoint}):`, error)
      throw error
    }
  }

  // Méthodes spécifiques pour chaque type de requête
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>("GET", endpoint)
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>("POST", endpoint, data)
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>("PUT", endpoint, data)
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>("DELETE", endpoint)
  }
}

// Exporter une instance unique du service API
const apiService = new ApiService();
export default apiService;

// Ne pas exporter les services spécifiques ici
// export * from "./api/auth-service"
// export * from "./api/campaigns-service"
// export * from "./api/leads-service"
// export * from "./api/agents-service"
// export * from "./api/niches-service"
// export * from "./api/stats-service"
