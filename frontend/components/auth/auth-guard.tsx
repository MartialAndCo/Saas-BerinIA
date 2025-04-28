"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, login } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Si l'authentification est terminée et que l'utilisateur n'est pas authentifié
    if (!isLoading && !isAuthenticated) {
      // Rediriger vers la page de connexion
      login({ appState: { returnTo: window.location.pathname } })
    }
  }, [isAuthenticated, isLoading, login])

  // Afficher un écran de chargement pendant la vérification de l'authentification
  if (isLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Vérification de l'authentification...</p>
        </div>
      </div>
    )
  }

  // Si l'utilisateur est authentifié, afficher le contenu protégé
  return <>{children}</>
} 