"use client";

import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { authStorage } from "@/lib/auth-storage";

// Composant de chargement
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Authentification en cours...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  const { isAuthenticated, isLoading } = useAuth();
  
  useEffect(() => {
    // Fonction pour extraire et décoder les paramètres d'URL
    const handleRedirection = () => {
      if (!isLoading && isAuthenticated) {
        try {
          // Définir le cookie pour le middleware
          document.cookie = `auth0.is.authenticated=true; path=/; max-age=${60 * 60 * 24}; SameSite=Lax`;
          
          // Récupérer l'état de l'URL
          const urlParams = new URLSearchParams(window.location.search);
          const state = urlParams.get('state');
          
          // Valeur par défaut
          let returnTo = '/admin';
          
          // Essayer de décoder l'état pour obtenir returnTo
          if (state) {
            try {
              const decodedState = JSON.parse(atob(state));
              if (decodedState.appState?.returnTo) {
                returnTo = decodedState.appState.returnTo;
              }
            } catch (e) {
              console.error('Erreur lors du décodage de l\'état:', e);
            }
          }
          
          console.log("Redirecting to:", returnTo);
          
          // Redirection avec un délai pour s'assurer que le cookie est défini
          setTimeout(() => {
            window.location.href = returnTo;
          }, 500);
        } catch (error) {
          console.error("Error in auth callback:", error);
          // En cas d'erreur, rediriger vers la page d'accueil
          window.location.href = '/';
        }
      }
    };
    
    handleRedirection();
  }, [isAuthenticated, isLoading]);
  
  return <LoadingSpinner />;
} 