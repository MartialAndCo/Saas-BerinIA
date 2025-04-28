"use client"

/**
 * Hook personnalisé pour gérer l'authentification
 *
 * Ce hook encapsule la logique d'authentification et fournit des méthodes
 * pour se connecter, s'inscrire et se déconnecter, ainsi que l'état de l'utilisateur.
 */

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import authService from "@/services/api/auth-service"
import { User } from "@/services/api/auth-service"
import { type LoginRequest, type RegisterRequest } from "@/services/api/auth-service"
import { useApi } from "./useApi"

interface UseAuthReturn {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: Error | null
  login: (credentials: LoginRequest) => Promise<void>
  register: (userData: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
}

// Vérifier si le code s'exécute côté client
const isClient = typeof window !== 'undefined';

/**
 * Hook pour gérer l'authentification
 *
 * @returns État et fonctions pour gérer l'authentification
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Utiliser le hook useApi pour gérer les appels API d'authentification
  const loginApi = useApi(authService.login.bind(authService))
  const registerApi = useApi(authService.register.bind(authService))
  const logoutApi = useApi(authService.logout.bind(authService))
  const getCurrentUserApi = useApi(authService.getCurrentUser.bind(authService))

  useEffect(() => {
    // Cette fonction ne s'exécute que côté client
    const checkAuth = async () => {
      try {
        setLoading(true)
        // Vérifier si un token existe
        const token = isClient ? localStorage.getItem('token') : null
        
        if (token) {
          const response = await getCurrentUserApi.execute()
          setUser(response.data)
        }
      } catch (err) {
        setError('Erreur lors de la vérification de l\'authentification')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    // N'exécuter que côté client
    if (isClient) {
      checkAuth()
    } else {
      setLoading(false)
    }
  }, [])

  // Fonction de connexion
  const login = useCallback(
    async (credentials: LoginRequest) => {
      try {
        setLoading(true)
        const response = await loginApi.execute(credentials)
        setUser(response.data.user)
        router.push("/dashboard")
      } catch (err) {
        setError('Erreur lors de la connexion')
        throw err
      } finally {
        setLoading(false)
      }
    },
    [loginApi, router],
  )

  // Fonction d'inscription
  const register = useCallback(
    async (userData: RegisterRequest) => {
      try {
        const response = await registerApi.execute(userData)
        setUser(response.data.user)
        router.push("/dashboard")
      } catch (err) {
        setError('Erreur lors de l\'inscription')
        throw err
      }
    },
    [registerApi, router],
  )

  // Fonction de déconnexion
  const logout = useCallback(async () => {
    try {
      await logoutApi.execute()
      setUser(null)
      router.push("/login")
    } catch (err) {
      setError('Erreur lors de la déconnexion')
      throw err
    }
  }, [logoutApi, router])

  return {
    user,
    isLoading: loading,
    isAuthenticated: !!user,
    error: error ? new Error(error) : null,
    login,
    register,
    logout,
  }
}
