/**
 * Service d'authentification
 *
 * Gère toutes les opérations liées à l'authentification des utilisateurs.
 */

import apiService, { ApiResponse } from '@/services/api'

// Types
export interface User {
  id: string
  name: string
  email: string
  role: string
  avatar?: string
  lastLogin?: string
  status: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  token: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
  company?: string
  jobTitle?: string
  agreeTerms: boolean
}

// Données mockées
const mockUsers: User[] = [
  {
    id: "1",
    name: "Admin",
    email: "admin@berinia.com",
    role: "admin",
    avatar: "A",
    lastLogin: "10/06/2023 15:45",
    status: "active",
  },
  {
    id: "2",
    name: "Jean Dupont",
    email: "jean.dupont@berinia.com",
    role: "manager",
    avatar: "JD",
    lastLogin: "10/06/2023 14:30",
    status: "active",
  },
]

/**
 * Service d'authentification
 */
class AuthService {
  /**
   * Connecte un utilisateur
   */
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    const response = await apiService.post<LoginResponse>('/api/auth/login', credentials)
    
    // Stocker le token
    if (response.data.token) {
      apiService.setToken(response.data.token)
    }
    
    return response
  }

  /**
   * Déconnecte l'utilisateur
   */
  logout(): void {
    apiService.clearToken()
  }

  /**
   * Vérifie si l'utilisateur est connecté
   */
  isLoggedIn(): boolean {
    return localStorage.getItem('token') !== null
  }

  /**
   * Récupère les informations de l'utilisateur connecté
   */
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiService.get<User>('/api/auth/me')
  }

  /**
   * Enregistre un nouvel utilisateur
   */
  async register(userData: Partial<User>): Promise<ApiResponse<User>> {
    return apiService.post<User>('/api/auth/register', userData)
  }
}

const authService = new AuthService()
export default authService
