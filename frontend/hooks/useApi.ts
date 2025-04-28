"use client"

/**
 * Hook personnalisé pour gérer les appels API avec gestion d'état
 *
 * Ce hook facilite l'utilisation des services API en gérant automatiquement
 * les états de chargement, d'erreur et de succès.
 */

import { useState, useCallback } from "react"
import type { ApiResponse } from "@/services/api"

interface UseApiState<T> {
  data: T | null
  isLoading: boolean
  error: Error | null
  isSuccess: boolean
}

interface UseApiOptions {
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
  loadingDelay?: number // Délai avant d'afficher l'état de chargement (ms)
}

/**
 * Hook pour gérer les appels API avec gestion d'état
 *
 * @param apiFunction Fonction du service API à appeler
 * @param options Options de configuration
 * @returns État et fonctions pour gérer l'appel API
 */
export function useApi<T, P extends any[]>(
  apiFunction: (...args: P) => Promise<ApiResponse<T>>,
  options: UseApiOptions = {},
) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    isLoading: false,
    error: null,
    isSuccess: false,
  })

  // Fonction pour exécuter l'appel API
  const execute = useCallback(
    async (...args: P) => {
      // Réinitialiser l'état
      setState((prev) => ({ ...prev, isLoading: true, error: null, isSuccess: false }))

      let loadingTimeout: NodeJS.Timeout | null = null

      // Si un délai de chargement est spécifié, on attend avant d'afficher l'état de chargement
      if (options.loadingDelay) {
        loadingTimeout = setTimeout(() => {
          setState((prev) => ({ ...prev, isLoading: true }))
        }, options.loadingDelay)
      }

      try {
        // Exécuter l'appel API
        const response = await apiFunction(...args)

        // Mettre à jour l'état avec les données
        setState({
          data: response.data,
          isLoading: false,
          error: null,
          isSuccess: true,
        })

        // Appeler le callback de succès si spécifié
        if (options.onSuccess) {
          options.onSuccess(response.data)
        }

        return response.data
      } catch (error) {
        // Mettre à jour l'état avec l'erreur
        setState({
          data: null,
          isLoading: false,
          error: error instanceof Error ? error : new Error(String(error)),
          isSuccess: false,
        })

        // Appeler le callback d'erreur si spécifié
        if (options.onError && error instanceof Error) {
          options.onError(error)
        }

        throw error
      } finally {
        // Nettoyer le timeout si nécessaire
        if (loadingTimeout) {
          clearTimeout(loadingTimeout)
        }
      }
    },
    [apiFunction, options],
  )

  // Fonction pour réinitialiser l'état
  const reset = useCallback(() => {
    setState({
      data: null,
      isLoading: false,
      error: null,
      isSuccess: false,
    })
  }, [])

  return {
    ...state,
    execute,
    reset,
  }
}
